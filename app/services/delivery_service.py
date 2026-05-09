from typing import Optional, Tuple, List, Dict
from copy import deepcopy
from datetime import datetime
import googlemaps
from app.config.settings import settings
from app.config.database import get_database
from app.utils.helpers import calculate_distance
from app.utils.constants import (
    DAILY_DELIVERY_FEE,
    DAILY_DELIVERY_RADIUS,
    DEFAULT_EXPRESS_FEE_PER_DAY,
)
from app.utils.default_delivery_zones import DEFAULT_MEAL_DELIVERY_ZONES
import logging

logger = logging.getLogger(__name__)

class DeliveryService:
    def __init__(self):
        self.gmaps = None
        self._db = None
        self._zones = None
        self._seeded_defaults = False
        self.business_lat = settings.BUSINESS_LATITUDE
        self.business_lng = settings.BUSINESS_LONGITUDE
        
        # Initialize Google Maps client only if API key is available and valid
        if settings.GOOGLE_MAPS_API_KEY and settings.GOOGLE_MAPS_API_KEY != "your-google-maps-api-key":
            try:
                self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                logger.info("Google Maps client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Maps client: {e}")
                logger.warning("Delivery service will work with limited functionality")
        else:
            logger.warning("Google Maps API key not configured. Using fallback delivery calculation.")
    
    @property
    def db(self):
        """Get database instance lazily"""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def zones(self):
        """Get delivery_zones collection lazily"""
        if self._zones is None and self.db is not None:  # ✅ Fixed
            self._zones = self.db.delivery_zones
        return self._zones

    async def ensure_default_zones(self) -> None:
        """Seed default meal subscription delivery zones when collection is empty."""
        if self._seeded_defaults:
            return

        if self.zones is None:
            return

        try:
            count = await self.zones.count_documents({})
            if count > 0:
                self._seeded_defaults = True
                return

            now = datetime.utcnow()
            documents: List[Dict[str, object]] = []
            for zone in DEFAULT_MEAL_DELIVERY_ZONES:
                payload = deepcopy(zone)
                payload.setdefault("state", "NSW")
                payload.setdefault("order_types", ["meal_subscription"])
                payload.setdefault("is_active", True)
                payload["created_at"] = now
                payload["updated_at"] = now
                documents.append(payload)

            if documents:
                await self.zones.insert_many(documents)
                logger.info("Seeded %d default delivery zones for meal subscriptions", len(documents))

            self._seeded_defaults = True
        except Exception as exc:
            logger.error(f"Failed to seed default delivery zones: {exc}")
    
    @staticmethod
    def _extract_postcode(address: str) -> Optional[str]:
        """Extract Australian postcode (4 digits) from a string."""
        if not address:
            return None
        import re
        match = re.search(r'\b(\d{4})\b', address)
        return match.group(1) if match else None

    async def _find_zone_by_postcode(
        self, postcode: Optional[str], order_type: Optional[str] = None
    ) -> Optional[dict]:
        """Lookup delivery zone by postcode if available."""
        if not postcode:
            return None
        _ = order_type

        if self.zones is None:
            for zone in DEFAULT_MEAL_DELIVERY_ZONES:
                if zone["postcode"] == postcode and zone.get("is_active", True):
                    return deepcopy(zone)
            return None

        await self.ensure_default_zones()
        query: Dict[str, object] = {"postcode": postcode, "is_active": True}
        cursor = self.zones.find(query).sort("base_delivery_fee", 1)
        matches = await cursor.to_list(length=1)
        return matches[0] if matches else None
    
    async def check_daily_delivery(
        self, address: str
    ) -> Tuple[bool, Optional[float], Optional[dict], Optional[str], float]:
        """
        Check if address is within daily delivery range.

        Returns:
            (is_available, distance_km, geocoded_address, failure_reason, delivery_fee)
        """
        try:
            failure_reason = None
            delivery_fee = DAILY_DELIVERY_FEE

            if self.gmaps:
                # Use Google Maps for accurate geocoding
                try:
                    geocode_result = self.gmaps.geocode(address)
                except Exception as e:
                    logger.warning(f"Google Maps geocode failed, falling back to postcode coverage: {e}")
                    geocode_result = None

                if not geocode_result:
                    # Fall back to postcode coverage below
                    self.gmaps = None
                else:
                    location = geocode_result[0]['geometry']['location']
                    lat = location['lat']
                    lng = location['lng']

                    # Calculate distance
                    distance = calculate_distance(
                        self.business_lat, self.business_lng,
                        lat, lng
                    )

                    formatted_address = geocode_result[0]['formatted_address']
                    postcode = self._extract_postcode(formatted_address)
                    zone = await self._find_zone_by_postcode(postcode, order_type="daily")

                radius_km: Optional[float] = DAILY_DELIVERY_RADIUS
                if zone and zone.get("distance_from_business") is not None:
                    try:
                        radius_km = float(zone.get("distance_from_business"))
                    except (TypeError, ValueError):
                        radius_km = DAILY_DELIVERY_RADIUS

                is_available = distance <= (radius_km if radius_km is not None else DAILY_DELIVERY_RADIUS)
                if not is_available:
                    failure_reason = (
                        f"This address is {distance:.1f}km away. "
                        f"Delivery is limited to {(radius_km if radius_km is not None else DAILY_DELIVERY_RADIUS):.0f}km."
                    )

                if zone and is_available:
                    delivery_fee = float(zone.get("base_delivery_fee") or DAILY_DELIVERY_FEE)
                else:
                    delivery_fee = DAILY_DELIVERY_FEE if is_available else 0.0

                geocoded_data = {
                    "formatted_address": formatted_address,
                    "latitude": lat,
                    "longitude": lng
                }

                logger.info(
                    "Daily delivery check: %s - %skm - fee=%s - postcode=%s",
                    address,
                    distance,
                    delivery_fee,
                    postcode,
                )
                return is_available, distance, geocoded_data, failure_reason, delivery_fee

            # Fallback: Simple postcode-based check
            logger.info("Using fallback delivery check (postcode-based)")

            postcode = self._extract_postcode(address)
            if postcode:
                zone_doc = await self._find_zone_by_postcode(postcode, order_type="daily")
                if zone_doc:
                    approximate_distance = zone_doc.get("distance_from_business")
                    delivery_fee = float(zone_doc.get("base_delivery_fee") or DAILY_DELIVERY_FEE)
                    geocoded_data = {
                        "formatted_address": address,
                        "latitude": self.business_lat,
                        "longitude": self.business_lng
                    }
                    return True, approximate_distance, geocoded_data, None, delivery_fee

                zone = await self.check_postcode_coverage(postcode)
                if zone and zone.get("is_covered"):
                    distance = zone.get("distance_km", 0.0)
                    is_available = distance <= DAILY_DELIVERY_RADIUS if distance is not None else False
                    if not is_available:
                        failure_reason = (
                            f"Daily delivery is limited to {DAILY_DELIVERY_RADIUS:.0f}km from Guildford."
                        )
                        return False, distance, None, failure_reason, 0.0

                    geocoded_data = {
                        "formatted_address": address,
                        "latitude": self.business_lat,
                        "longitude": self.business_lng
                    }
                    return True, distance, geocoded_data, None, DAILY_DELIVERY_FEE

            failure_reason = (
                f"We currently deliver daily orders within {DAILY_DELIVERY_RADIUS:.0f}km of Guildford. "
                "Please choose an address inside this range."
            )
            return False, None, {
                "formatted_address": address,
                "latitude": self.business_lat,
                "longitude": self.business_lng
            }, failure_reason, 0.0

        except Exception as e:
            logger.error(f"Error checking daily delivery: {e}")
            return False, None, None, (
                "Unable to verify address for daily delivery right now. "
                "Please try again or contact support."
            ), 0.0
    
    async def calculate_weekly_delivery_fee(
        self, 
        address: str, 
        order_value: float, 
        delivery_days: int,
        is_express: bool = False
    ) -> Tuple[float, float, dict]:
        """
        Calculate weekly delivery fee
        
        Returns:
            (delivery_fee, distance_km, geocoded_address)
        """
        try:
            formatted_address = address
            distance = None
            lat = self.business_lat
            lng = self.business_lng

            if self.gmaps:
                try:
                    geocode_result = self.gmaps.geocode(address)
                except Exception as e:
                    logger.warning(f"Google Maps geocode failed, falling back to postcode coverage: {e}")
                    geocode_result = None

                if not geocode_result:
                    geocode_result = None
                else:
                    formatted_address = geocode_result[0]['formatted_address']
                    location = geocode_result[0]['geometry']['location']
                    lat = location['lat']
                    lng = location['lng']
                    distance = calculate_distance(
                        self.business_lat, self.business_lng, lat, lng
                    )

                if geocode_result is None:
                    formatted_address = address
                    distance = None
                    lat = self.business_lat
                    lng = self.business_lng

            postcode = self._extract_postcode(formatted_address)
            zone = await self._find_zone_by_postcode(postcode, order_type="meal_subscription")

            if not postcode or not zone:
                raise ValueError("Delivery is not available to this postcode.")

            max_distance_km = zone.get("distance_from_business")
            if max_distance_km is not None:
                try:
                    max_distance_km = float(max_distance_km)
                except (TypeError, ValueError):
                    max_distance_km = None

            if distance is None:
                distance = max_distance_km if max_distance_km is not None else calculate_distance(
                    self.business_lat, self.business_lng, lat, lng
                )

            if (
                max_distance_km is not None
                and distance is not None
                and distance > max_distance_km
            ):
                raise ValueError(
                    f"Delivery is not available beyond {max_distance_km:.0f}km for this postcode."
                )

            geocoded_data = {
                "formatted_address": formatted_address,
                "latitude": lat,
                "longitude": lng
            }

            base_fee_per_day = 10.0
            express_fee_per_day = DEFAULT_EXPRESS_FEE_PER_DAY if is_express else 0.0

            if zone:
                base_fee_per_day = zone.get("base_delivery_fee", base_fee_per_day)
                if is_express:
                    express_fee_per_day = zone.get("express_delivery_fee", express_fee_per_day)

                max_days = zone.get("max_delivery_days")
                if max_days and delivery_days > max_days:
                    logger.warning(
                        "Requested delivery days (%s) exceed zone max (%s) for postcode %s",
                        delivery_days,
                        max_days,
                        postcode,
                    )

            total_delivery_fee = (base_fee_per_day * delivery_days) + (express_fee_per_day * delivery_days)

            logger.info(
                "Meal subscription delivery fee: base=%s express=%s days=%s total=%s postcode=%s",
                base_fee_per_day,
                express_fee_per_day if is_express else 0.0,
                delivery_days,
                total_delivery_fee,
                postcode,
            )
            return total_delivery_fee, distance, geocoded_data
            
        except Exception as e:
            logger.error(f"Error calculating weekly delivery fee: {e}")
            # Propagate value errors so the API can respond with a clear message
            if isinstance(e, ValueError):
                raise
            # Return default fee to not break the service for unexpected errors
            base_fee = 10.0 * delivery_days
            if is_express:
                base_fee += DEFAULT_EXPRESS_FEE_PER_DAY * delivery_days
            
            return base_fee, 10.0, {
                "formatted_address": address,
                "latitude": self.business_lat,
                "longitude": self.business_lng
            }
    
    async def check_postcode_coverage(self, postcode: str) -> Optional[dict]:
        """Check if postcode is covered"""
        try:
            if self.zones is None:  # ✅ Fixed
                matches = [
                    deepcopy(zone)
                    for zone in DEFAULT_MEAL_DELIVERY_ZONES
                    if zone["postcode"] == postcode and zone.get("is_active", True)
                ]
                if matches:
                    primary = matches[0]
                    response = {
                        "suburbs": primary.get("suburbs", []),
                        "postcode": primary["postcode"],
                        "distance_km": primary.get("distance_from_business"),
                        "base_delivery_fee": primary.get("base_delivery_fee"),
                        "notes": primary.get("notes"),
                        "is_covered": True,
                    }
                    if len(matches) > 1:
                        response["alternatives"] = [
                            {
                                "zone_label": zone.get("zone_label"),
                                "suburbs": zone.get("suburbs", []),
                                "base_delivery_fee": zone.get("base_delivery_fee"),
                                "notes": zone.get("notes"),
                            }
                            for zone in matches[1:]
                        ]
                    return response
                return {"is_covered": False}

            await self.ensure_default_zones()
            cursor = self.zones.find({"postcode": postcode, "is_active": True}).sort("base_delivery_fee", 1)
            zones = await cursor.to_list(length=None)

            if zones:
                primary = zones[0]
                response = {
                    "suburbs": primary.get("suburbs", []),
                    "postcode": primary["postcode"],
                    "distance_km": primary.get("distance_from_business"),
                    "base_delivery_fee": primary.get("base_delivery_fee"),
                    "notes": primary.get("notes"),
                    "is_covered": True,
                }
                if len(zones) > 1:
                    response["alternatives"] = [
                        {
                            "zone_label": zone.get("zone_label"),
                            "suburbs": zone.get("suburbs", []),
                            "base_delivery_fee": zone.get("base_delivery_fee"),
                            "notes": zone.get("notes"),
                        }
                        for zone in zones[1:]
                    ]
                return response

            return {"is_covered": False}
            
        except Exception as e:
            logger.error(f"Error checking postcode: {e}")
            return {"is_covered": False, "base_delivery_fee": None}  # Default to not covered on error
    
    async def get_available_suburbs(self) -> list:
        """Get list of all available suburbs"""
        try:
            if self.zones is None:  # ✅ Fixed
                return [
                    {
                        "postcode": zone.get("postcode"),
                        "zone_label": zone.get("zone_label"),
                        "suburbs": zone.get("suburbs", []),
                        "distance_km": zone.get("distance_from_business"),
                        "base_delivery_fee": zone.get("base_delivery_fee"),
                        "notes": zone.get("notes"),
                        "order_types": zone.get("order_types", []),
                    }
                    for zone in DEFAULT_MEAL_DELIVERY_ZONES
                    if zone.get("is_active", True)
                ]
            
            await self.ensure_default_zones()
            cursor = self.zones.find({"is_active": True}).sort("postcode", 1)
            zones = await cursor.to_list(length=None)
            
            return [
                {
                    "postcode": zone.get("postcode"),
                    "zone_label": zone.get("zone_label"),
                    "suburbs": zone.get("suburbs") or ([zone["suburb"]] if zone.get("suburb") else []),
                    "distance_km": zone.get("distance_from_business"),
                    "base_delivery_fee": zone.get("base_delivery_fee"),
                    "notes": zone.get("notes"),
                    "order_types": zone.get("order_types", []),
                }
                for zone in zones
            ]
            
        except Exception as e:
            logger.error(f"Error getting suburbs: {e}")
            return []

delivery_service = DeliveryService()
