from typing import Dict, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.config.database import get_database
from app.utils.constants import OrderStatus, PaymentStatus
import logging
import re

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self):
        self._db = None
        self._orders = None
        self._users = None
        self._meal_subs = None
        self._legacy_weekly_subs = None
        self._catering_orders = None
    
    @property
    def db(self):
        """Get database instance lazily"""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def orders(self):
        """Get orders collection lazily"""
        if self._orders is None and self.db is not None:
            self._orders = self.db.orders
        return self._orders
    
    @property
    def users(self):
        """Get users collection lazily"""
        if self._users is None and self.db is not None:
            self._users = self.db.users
        return self._users
    
    @property
    def meal_subs(self):
        """Get meal_subscriptions collection lazily"""
        if self._meal_subs is None and self.db is not None:
            self._meal_subs = self.db.meal_subscriptions
        return self._meal_subs
    
    @property
    def weekly_subs_legacy(self):
        """Access legacy weekly_subscriptions collection if it exists."""
        if self._legacy_weekly_subs is None and self.db is not None:
            self._legacy_weekly_subs = getattr(self.db, "weekly_subscriptions", None)
        return self._legacy_weekly_subs
    
    @property
    def catering_orders(self):
        """Get catering_orders collection lazily"""
        if self._catering_orders is None and self.db is not None:
            self._catering_orders = self.db.catering_orders
        return self._catering_orders

    @staticmethod
    def _calculate_growth(current: float, previous: float) -> float:
        """Calculate percentage growth between current and previous values."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)

    @staticmethod
    def _serialize_datetime(value):
        """Convert datetime-like values to ISO strings for API responses."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _normalize_address(address: Dict) -> Dict:
        """Ensure delivery address fields are serializable for responses."""
        if not address:
            return None

        normalized = dict(address)
        for key in ("_id", "id", "user_id"):
            if normalized.get(key) is not None:
                normalized[key] = str(normalized[key])

        for key in ("created_at", "updated_at"):
            if key in normalized:
                normalized[key] = AdminService._serialize_datetime(normalized.get(key))
        return normalized

    @staticmethod
    def _map_order_type(order_type: str) -> str:
        """Align backend order types with admin frontend expectations."""
        mapping = {
            "daily": "daily_menu",
            "daily_menu": "daily_menu",
            "weekly": "meal_subscription",
            "subscription": "meal_subscription",
            "meal_subscription": "meal_subscription",
            "catering": "special_catering",
            "special_catering": "special_catering",
        }
        return mapping.get(order_type, order_type)

    @staticmethod
    def _subscription_label(order: Dict) -> Optional[str]:
        """Return a human-friendly label for meal subscription plan tab."""
        tab = str(order.get("primary_plan_tab") or "").strip().lower()
        tab_labels = {
            "weekly": "Weekly",
            "fortnight": "Fortnight",
            "monthly": "Monthly",
            "regular": "Regular Meal",
            "custom": "Custom",
        }
        if tab in tab_labels:
            return tab_labels[tab]

        name = str(order.get("primary_plan_name") or "").lower()
        for keyword, label in (
            ("weekly", "Weekly"),
            ("fortnight", "Fortnight"),
            ("month", "Monthly"),
            ("regular", "Regular Meal"),
            ("custom", "Custom"),
        ):
            if keyword in name:
                return label
        return None
    
    async def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics with real-time data"""
        try:
            if self.orders is None:
                logger.warning("Orders collection not available")
                return self._get_empty_stats()

            # ✅ FIX: Use local time instead of UTC for better date accuracy
            now = datetime.now()
            today_start = datetime(now.year, now.month, now.day)
            today_end = today_start + timedelta(days=1)
            yesterday_start = today_start - timedelta(days=1)
            yesterday_end = today_start

            # Get current week boundaries (Monday to Sunday)
            week_start_dt = now - timedelta(days=now.weekday())
            week_start = datetime(week_start_dt.year, week_start_dt.month, week_start_dt.day)
            week_end = week_start + timedelta(days=7)
            prev_week_start = week_start - timedelta(days=7)
            prev_week_end = week_start

            # Get current month boundaries
            month_start = datetime(now.year, now.month, 1)
            if month_start.month == 12:
                next_month_start = datetime(month_start.year + 1, 1, 1)
            else:
                next_month_start = datetime(month_start.year, month_start.month + 1, 1)
            if month_start.month == 1:
                prev_month_start = datetime(month_start.year - 1, 12, 1)
            else:
                prev_month_start = datetime(month_start.year, month_start.month - 1, 1)
            prev_month_end = month_start

            logger.info(f"📊 Calculating dashboard stats for {now.strftime('%Y-%m-%d %H:%M')}")
            logger.info(f"   Today: {today_start.strftime('%Y-%m-%d')} to {today_end.strftime('%Y-%m-%d')}")
            logger.info(f"   This week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")

            # ✅ FIX: Count ALL orders (not just paid ones) for total orders
            total_orders = await self.orders.count_documents({})
            logger.info(f"   Total orders in DB: {total_orders}")

            # Current month vs previous month orders (for growth)
            current_month_orders = await self.orders.count_documents({
                "created_at": {"$gte": month_start, "$lt": next_month_start}
            })
            previous_month_orders = await self.orders.count_documents({
                "created_at": {"$gte": prev_month_start, "$lt": prev_month_end}
            })
            total_orders_growth_percent = self._calculate_growth(
                current_month_orders, previous_month_orders
            )

            logger.info(f"   Orders this month: {current_month_orders}, last month: {previous_month_orders}")

            # ✅ FIX: Count pending orders (pending, confirmed, preparing)
            pending_statuses = [
                OrderStatus.PENDING.value,
                OrderStatus.CONFIRMED.value,
                OrderStatus.PREPARING.value,
            ]
            pending_orders = await self.orders.count_documents({
                "status": {"$in": pending_statuses}
            })

            # Pending orders this week vs last week
            pending_orders_this_week = await self.orders.count_documents({
                "status": {"$in": pending_statuses},
                "created_at": {"$gte": week_start, "$lt": week_end}
            })
            pending_orders_last_week = await self.orders.count_documents({
                "status": {"$in": pending_statuses},
                "created_at": {"$gte": prev_week_start, "$lt": prev_week_end}
            })
            pending_orders_weekly_change_percent = self._calculate_growth(
                pending_orders_this_week, pending_orders_last_week
            )

            logger.info(f"   Pending orders: {pending_orders} (this week: {pending_orders_this_week})")

            # Status breakdown
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            status_results = await self.orders.aggregate(status_pipeline).to_list(None)
            status_counts = {res["_id"]: res["count"] for res in status_results}

            confirmed_orders = status_counts.get(OrderStatus.CONFIRMED.value, 0)
            preparing_orders = status_counts.get(OrderStatus.PREPARING.value, 0)
            out_for_delivery_orders = status_counts.get(OrderStatus.OUT_FOR_DELIVERY.value, 0)
            completed_orders = status_counts.get(OrderStatus.DELIVERED.value, 0)
            cancelled_orders = status_counts.get(OrderStatus.CANCELLED.value, 0)

            # ✅ FIX: Include BOTH paid AND pending orders in revenue (since pending will be paid)
            revenue_statuses = [PaymentStatus.PAID.value, PaymentStatus.PENDING.value]

            # Today's revenue
            today_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": today_start, "$lt": today_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            today_result = await self.orders.aggregate(today_pipeline).to_list(1)
            today_revenue = today_result[0]["total"] if today_result else 0.0

            # Yesterday's revenue
            yesterday_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": yesterday_start, "$lt": yesterday_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            yesterday_result = await self.orders.aggregate(yesterday_pipeline).to_list(1)
            yesterday_revenue = yesterday_result[0]["total"] if yesterday_result else 0.0
            today_vs_yesterday_percent = self._calculate_growth(today_revenue, yesterday_revenue)

            logger.info(f"   Today's revenue: ${today_revenue:.2f}, yesterday: ${yesterday_revenue:.2f}")

            # Weekly revenue
            weekly_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": week_start, "$lt": week_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            weekly_result = await self.orders.aggregate(weekly_pipeline).to_list(1)
            weekly_revenue = weekly_result[0]["total"] if weekly_result else 0.0

            # Previous week revenue
            previous_week_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": prev_week_start, "$lt": prev_week_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            previous_week_result = await self.orders.aggregate(previous_week_pipeline).to_list(1)
            previous_week_revenue = previous_week_result[0]["total"] if previous_week_result else 0.0
            weekly_growth_percent = self._calculate_growth(weekly_revenue, previous_week_revenue)

            logger.info(f"   Weekly revenue: ${weekly_revenue:.2f}, last week: ${previous_week_revenue:.2f}")

            # Monthly revenue
            monthly_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": month_start, "$lt": next_month_start},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            monthly_result = await self.orders.aggregate(monthly_pipeline).to_list(1)
            monthly_revenue = monthly_result[0]["total"] if monthly_result else 0.0

            # Previous month revenue
            previous_month_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": prev_month_start, "$lt": prev_month_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            previous_month_result = await self.orders.aggregate(previous_month_pipeline).to_list(1)
            previous_month_revenue = previous_month_result[0]["total"] if previous_month_result else 0.0
            monthly_growth_percent = self._calculate_growth(monthly_revenue, previous_month_revenue)

            logger.info(f"   Monthly revenue: ${monthly_revenue:.2f}, last month: ${previous_month_revenue:.2f}")

            # Total revenue (all time)
            total_revenue_pipeline = [
                {
                    "$match": {
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            total_revenue_result = await self.orders.aggregate(total_revenue_pipeline).to_list(1)
            total_revenue = total_revenue_result[0]["total"] if total_revenue_result else 0.0
            total_revenue_growth_percent = monthly_growth_percent  # Use monthly growth as trend

            logger.info(f"   Total revenue: ${total_revenue:.2f}")

            # ✅ FIX: Weekly revenue breakdown (Mon-Sun) with actual data
            weekly_breakdown_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": week_start, "$lt": week_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {
                    "$project": {
                        "total_amount": 1,
                        "day_of_week": {"$dayOfWeek": "$created_at"}
                    }
                },
                {
                    "$group": {
                        "_id": "$day_of_week",
                        "total": {"$sum": "$total_amount"}
                    }
                }
            ]
            weekly_breakdown_results = await self.orders.aggregate(weekly_breakdown_pipeline).to_list(None)
            
            # Map MongoDB day of week (1=Sunday) to array index (0=Monday)
            breakdown_map = {i: 0.0 for i in range(7)}
            for result in weekly_breakdown_results:
                mongo_day = result["_id"]  # 1=Sunday, 2=Monday, ..., 7=Saturday
                # Convert: Sunday(1) -> 6, Monday(2) -> 0, Tuesday(3) -> 1, etc.
                index = (mongo_day + 5) % 7
                breakdown_map[index] = round(result["total"], 2)

            day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            weekly_revenue_breakdown = []
            for offset in range(7):
                day_date = week_start + timedelta(days=offset)
                weekly_revenue_breakdown.append({
                    "label": day_labels[offset],
                    "date": day_date.strftime("%Y-%m-%d"),
                    "total": breakdown_map.get(offset, 0.0)
                })

            breakdown_log = [f"{d['label']}:${d['total']:.2f}" for d in weekly_revenue_breakdown]
            logger.info("   Weekly breakdown: %s", breakdown_log)

            # Active subscriptions
            active_subs = 0
            subscription_collections = [
                coll for coll in [self.meal_subs, self.weekly_subs_legacy] if coll is not None
            ]
            for coll in subscription_collections:
                try:
                    active_subs += await coll.count_documents({
                        "$or": [
                            {"status": {"$in": ["active", "paused"]}},
                            {"is_active": True},
                        ]
                    })
                except Exception as sub_error:
                    logger.warning(f"Unable to count active subscriptions: {sub_error}")

            # Upcoming catering events
            upcoming_catering = 0
            if self.catering_orders is not None:
                upcoming_catering = await self.catering_orders.count_documents({
                    "event_date": {"$gte": now}
                })

            stats = {
                "total_orders": total_orders,
                "total_orders_growth_percent": total_orders_growth_percent,
                "pending_orders": pending_orders,
                "pending_orders_weekly_change_percent": pending_orders_weekly_change_percent,
                "confirmed_orders": confirmed_orders,
                "preparing_orders": preparing_orders,
                "out_for_delivery_orders": out_for_delivery_orders,
                "completed_orders": completed_orders,
                "cancelled_orders": cancelled_orders,
                "today_revenue": round(today_revenue, 2),
                "today_vs_yesterday_percent": today_vs_yesterday_percent,
                "weekly_revenue": round(weekly_revenue, 2),
                "weekly_growth_percent": weekly_growth_percent,
                "monthly_revenue": round(monthly_revenue, 2),
                "monthly_growth_percent": monthly_growth_percent,
                "total_revenue": round(total_revenue, 2),
                "total_revenue_growth_percent": total_revenue_growth_percent,
                "weekly_revenue_breakdown": weekly_revenue_breakdown,
                "active_subscriptions": active_subs,
                "upcoming_catering_events": upcoming_catering
            }

            logger.info("✅ Dashboard stats calculated successfully")
            return stats

        except Exception as e:
            logger.error(f"❌ Error getting dashboard stats: {e}", exc_info=True)
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict:
        """Return empty stats structure as fallback"""
        return {
            "total_orders": 0,
            "total_orders_growth_percent": 0.0,
            "pending_orders": 0,
            "pending_orders_weekly_change_percent": 0.0,
            "confirmed_orders": 0,
            "preparing_orders": 0,
            "out_for_delivery_orders": 0,
            "completed_orders": 0,
            "cancelled_orders": 0,
            "today_revenue": 0.0,
            "today_vs_yesterday_percent": 0.0,
            "weekly_revenue": 0.0,
            "weekly_growth_percent": 0.0,
            "monthly_revenue": 0.0,
            "monthly_growth_percent": 0.0,
            "total_revenue": 0.0,
            "total_revenue_growth_percent": 0.0,
            "weekly_revenue_breakdown": [
                {"label": "Mon", "date": "", "total": 0.0},
                {"label": "Tue", "date": "", "total": 0.0},
                {"label": "Wed", "date": "", "total": 0.0},
                {"label": "Thu", "date": "", "total": 0.0},
                {"label": "Fri", "date": "", "total": 0.0},
                {"label": "Sat", "date": "", "total": 0.0},
                {"label": "Sun", "date": "", "total": 0.0},
            ],
            "active_subscriptions": 0,
            "upcoming_catering_events": 0
        }
    
    # ... (rest of the methods remain the same - get_all_orders, get_sales_report, etc.)
    
    async def get_all_orders(
        self,
        skip: int = 0,
        limit: int = 50,
        status: str = None,
        order_type: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        search: str = None
    ) -> tuple[List, int]:
        """Get all orders with filters"""
        try:
            if self.orders is None:
                return [], 0
                
            query = {}
            
            if status:
                query["status"] = status
            
            if order_type:
                query["order_type"] = order_type
            
            if date_from or date_to:
                query["created_at"] = {}
                if date_from:
                    query["created_at"]["$gte"] = date_from
                if date_to:
                    query["created_at"]["$lte"] = date_to

                if not query["created_at"]:
                    query.pop("created_at", None)

            if search:
                search_value = search.strip()
                if search_value:
                    escaped = re.escape(search_value)
                    query["$or"] = [
                        {"order_number": {"$regex": escaped, "$options": "i"}}
                    ]
                    if ObjectId.is_valid(search_value):
                        query["$or"].append({"_id": ObjectId(search_value)})
            
            # Get total count
            total = await self.orders.count_documents(query)
            
            # Get orders
            cursor = (
                self.orders.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            orders = await cursor.to_list(length=limit)

            serialized_orders: List[Dict] = []
            for order in orders:
                if self.users is not None and order.get("user_id") is not None:
                    user = await self.users.find_one({"_id": order["user_id"]})
                    if user:
                        order["user_name"] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                        order["user_email"] = user.get("email")
                        order["user_phone"] = user.get("phone")

                delivery_slots_serialized = []
                if order.get("order_type") in ("meal_subscription", "weekly", "subscription"):
                    # Pull delivery slots from meal_subscriptions collection for admin visibility
                    subscription = None
                    if self.meal_subs is not None:
                        subscription = await self.meal_subs.find_one({"order_id": order.get("_id")})
                    if subscription is None and self.weekly_subs_legacy is not None:
                        subscription = await self.weekly_subs_legacy.find_one({"order_id": order.get("_id")})
                    if subscription:
                        for slot in subscription.get("delivery_slots", []):
                            raw_date = slot.get("delivery_date")
                            date_str = (
                                raw_date.isoformat() if hasattr(raw_date, "isoformat") else str(raw_date)
                            )
                            delivery_slots_serialized.append(
                                {
                                    "delivery_date": date_str,
                                    "menu_items": {str(k): int(v) for k, v in (slot.get("menu_items") or {}).items()},
                                    "notes": slot.get("notes"),
                                }
                            )

                serialized = {
                    "_id": str(order.get("_id")),
                    "order_number": order.get("order_number"),
                    "user_id": str(order.get("user_id")) if order.get("user_id") is not None else None,
                    "order_type": self._map_order_type(order.get("order_type")),
                    "primary_plan_tab": order.get("primary_plan_tab"),
                    "primary_plan_name": order.get("primary_plan_name"),
                    "subscription_type": self._subscription_label(order),
                    "status": order.get("status"),
                    "payment_status": order.get("payment_status"),
                    "payment_method": order.get("payment_method"),
                    "payment_intent_id": order.get("stripe_payment_intent_id"),
                    "items": order.get("items", []),
                    "sidelines": order.get("sidelines", []),
                    "subtotal": order.get("subtotal", 0.0),
                    "tax_amount": order.get("tax_amount", 0.0),
                    "delivery_fee": order.get("delivery_fee", 0.0),
                    "total_amount": order.get("total_amount", 0.0),
                    "total": order.get("total_amount", 0.0),
                    "extra_boxes": order.get("extra_boxes", 0),
                    "extra_boxes_price": order.get("extra_boxes_price", 0.0),
                    "plan_price_total": order.get("plan_price_total", 0.0),
                    "delivery_method": order.get("delivery_method"),
                    "delivery_address": self._normalize_address(order.get("delivery_address")),
                    "delivery_instructions": order.get("delivery_instructions"),
                    "notes": order.get("notes"),
                    "admin_notes": order.get("admin_notes"),
                    "created_at": self._serialize_datetime(order.get("created_at")),
                    "updated_at": self._serialize_datetime(order.get("updated_at")),
                    "delivered_at": self._serialize_datetime(order.get("delivered_at")),
                    "user_name": order.get("user_name"),
                    "user_email": order.get("user_email"),
                    "user_phone": order.get("user_phone"),
                    "delivery_slots": delivery_slots_serialized if delivery_slots_serialized else None,
                }
                serialized_orders.append(serialized)

            return serialized_orders, total
            
        except Exception as e:
            logger.error(f"Error getting all orders: {e}")
            raise
    
    async def get_sales_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate sales report for date range"""
        try:
            if self.orders is None:
                return {
                    "date_range": {
                        "from": start_date.strftime("%Y-%m-%d"),
                        "to": end_date.strftime("%Y-%m-%d")
                    },
                    "by_order_type": {},
                    "total_orders": 0,
                    "total_revenue": 0.0
                }
                
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date, "$lte": end_date},
                        "payment_status": {"$in": [PaymentStatus.PAID.value, PaymentStatus.PENDING.value]}
                    }
                },
                {
                    "$group": {
                        "_id": "$order_type",
                        "count": {"$sum": 1},
                        "total_revenue": {"$sum": "$total_amount"}
                    }
                }
            ]
            
            results = await self.orders.aggregate(pipeline).to_list(None)
            
            report = {
                "date_range": {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d")
                },
                "by_order_type": {},
                "total_orders": 0,
                "total_revenue": 0.0
            }
            
            for result in results:
                order_type = result["_id"]
                report["by_order_type"][order_type] = {
                    "count": result["count"],
                    "revenue": round(result["total_revenue"], 2)
                }
                report["total_orders"] += result["count"]
                report["total_revenue"] += result["total_revenue"]
            
            report["total_revenue"] = round(report["total_revenue"], 2)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating sales report: {e}")
            raise

    async def get_menu_item_orders_report(
        self,
        skip: int = 0,
        limit: int = 50,
        date_from: datetime = None,
        date_to: datetime = None,
        order_type: str = None,
        menu_item_id: str = None,
    ) -> tuple[List[Dict], int]:
        """
        Aggregate how many orders each menu item has on each date.

        Combines daily orders and meal subscription delivery slots.
        """
        if self.orders is None:
            return [], 0

        # Map admin order type labels back to stored values
        type_map = {
            "daily_menu": "daily",
            "daily": "daily",
            "meal_subscription": "meal_subscription",
            "weekly": "meal_subscription",
            "subscription": "meal_subscription",
            "special_catering": "catering",
            "catering": "catering",
        }
        normalized_order_type = type_map.get(order_type, None) if order_type else None

        # Build match windows
        order_date_filter = {}
        slot_date_filter = {}
        if date_from:
            order_date_filter["$gte"] = date_from
            slot_date_filter["$gte"] = date_from
        if date_to:
            order_date_filter["$lte"] = date_to
            slot_date_filter["$lte"] = date_to

        include_daily = normalized_order_type in (None, "daily")
        include_subscriptions = normalized_order_type in (None, "meal_subscription")

        pipeline: List[Dict] = []

        if include_daily:
            order_match: Dict[str, Dict] = {}
            if order_date_filter:
                order_match["created_at"] = order_date_filter
            if normalized_order_type:
                order_match["order_type"] = normalized_order_type

            daily_pipeline: List[Dict] = [
                {"$match": order_match},
                {"$unwind": "$items"},
                {
                    "$project": {
                        "menu_item_id": "$items.item_id",
                        "menu_item_name": "$items.item_name",
                        "category": "$items.category",
                        "quantity": "$items.quantity",
                        "order_type": {"$literal": "daily_menu"},
                        "date": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$created_at",
                            }
                        },
                    }
                },
            ]

            if menu_item_id:
                daily_pipeline.append({"$match": {"menu_item_id": menu_item_id}})

            daily_pipeline.extend(
                [
                    {
                        "$group": {
                            "_id": {
                                "menu_item_id": "$menu_item_id",
                                "date": "$date",
                                "order_type": "$order_type",
                            },
                            "total_quantity": {"$sum": "$quantity"},
                            "order_count": {"$sum": 1},
                            "menu_item_name": {"$first": "$menu_item_name"},
                            "category": {"$first": "$category"},
                            "order_type": {"$first": "$order_type"},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "menu_item_id": "$_id.menu_item_id",
                            "date": "$_id.date",
                            "order_type": "$_id.order_type",
                            "total_quantity": 1,
                            "order_count": 1,
                            "menu_item_name": 1,
                            "category": 1,
                            "source": {"$literal": "daily"},
                        }
                    },
                ]
            )

            pipeline.extend(daily_pipeline)

        if include_subscriptions:
            # Only union if we already started with daily pipeline; otherwise start fresh
            union_stage_target = {
                "coll": "meal_subscriptions",
                "pipeline": [],
            }

            sub_pipeline: List[Dict] = []

            # Match delivery slots by date early
            if slot_date_filter:
                sub_pipeline.append(
                    {"$match": {"delivery_slots.delivery_date": slot_date_filter}}
                )

            sub_pipeline.extend(
                [
                    {"$unwind": "$delivery_slots"},
                    {
                        "$project": {
                            "delivery_date": "$delivery_slots.delivery_date",
                            "items_array": {"$objectToArray": "$delivery_slots.menu_items"},
                        }
                    },
                    {"$unwind": "$items_array"},
                    {
                        "$project": {
                            "menu_item_id": "$items_array.k",
                            "quantity": "$items_array.v",
                            "order_type": {"$literal": "meal_subscription"},
                            "date": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d",
                                    "date": "$delivery_date",
                                }
                            },
                        }
                    },
                    {"$match": {"quantity": {"$gt": 0}}},
                ]
            )

            if menu_item_id:
                sub_pipeline.append({"$match": {"menu_item_id": menu_item_id}})

            sub_pipeline.extend(
                [
                    {
                        "$group": {
                            "_id": {
                                "menu_item_id": "$menu_item_id",
                                "date": "$date",
                                "order_type": "$order_type",
                            },
                            "total_quantity": {"$sum": "$quantity"},
                            "order_count": {"$sum": 1},
                            "order_type": {"$first": "$order_type"},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "menu_item_id": "$_id.menu_item_id",
                            "date": "$_id.date",
                            "order_type": "$_id.order_type",
                            "total_quantity": 1,
                            "order_count": 1,
                            "source": {"$literal": "subscription"},
                        }
                    },
                ]
            )

            union_stage_target["pipeline"] = sub_pipeline

            if include_daily:
                pipeline.append({"$unionWith": union_stage_target})
            else:
                # No daily pipeline was built; start with an empty cursor and union subscription data
                pipeline = [
                    {"$match": {"_id": {"$exists": False}}},
                    {"$unionWith": union_stage_target},
                ]

        # Merge potential duplicates (same item/date across sources)
        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": {
                            "menu_item_id": "$menu_item_id",
                            "date": "$date",
                            "order_type": "$order_type",
                        },
                        "total_quantity": {"$sum": "$total_quantity"},
                        "order_count": {"$sum": "$order_count"},
                        "menu_item_name": {"$first": "$menu_item_name"},
                        "category": {"$first": "$category"},
                        "order_type": {"$first": "$order_type"},
                    }
                },
                {
                    "$lookup": {
                        "from": "menu_items",
                        "let": {"itemId": "$_id.menu_item_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": [
                                            "$_id",
                                            {
                                                "$convert": {
                                                    "input": "$$itemId",
                                                    "to": "objectId",
                                                    "onError": None,
                                                    "onNull": None,
                                                }
                                            },
                                        ]
                                    }
                                }
                            },
                            {"$project": {"name": 1, "category": 1}},
                        ],
                        "as": "menu_item_doc",
                    }
                },
                {
                    "$addFields": {
                        "menu_item_name": {
                            "$ifNull": [
                                {"$arrayElemAt": ["$menu_item_doc.name", 0]},
                                "$menu_item_name",
                            ]
                        },
                        "category": {
                            "$ifNull": [
                                {"$arrayElemAt": ["$menu_item_doc.category", 0]},
                                "$category",
                            ]
                        },
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "menu_item_id": "$_id.menu_item_id",
                        "date": "$_id.date",
                        "order_type": "$_id.order_type",
                        "total_quantity": 1,
                        "order_count": 1,
                        "menu_item_name": 1,
                        "category": 1,
                    }
                },
                {"$sort": {"date": -1, "order_type": 1, "menu_item_name": 1}},
                {
                    "$facet": {
                        "results": [
                            {"$skip": skip},
                            {"$limit": limit},
                        ],
                        "total": [{"$count": "count"}],
                    }
                },
            ]
        )

        results = await self.orders.aggregate(pipeline).to_list(length=1)
        if not results:
            return [], 0

        first = results[0]
        data = first.get("results", [])
        total = first.get("total", [])
        total_count = total[0]["count"] if total else 0
        return data, total_count

admin_service = AdminService()
