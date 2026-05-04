"""
Default delivery zones covering meal subscription service areas.

These records are used to seed the MongoDB `delivery_zones` collection when
it is empty. They intentionally focus on meal subscription coverage – the
daily menu retains its 6 km delivery radius and does not rely on this table.
"""
from __future__ import annotations

from typing import List, Dict

MEAL_SUBSCRIPTION_NOTE = "Meal subscriptions only"


def _zone(
    zone_label: str,
    postcode: str,
    suburbs: List[str],
    base_delivery_fee: float,
    max_distance_km: float,
    notes: str | None = None,
) -> Dict[str, object]:
    """Helper to create a consistent delivery zone payload."""
    payload: Dict[str, object] = {
        "zone_label": zone_label,
        "postcode": postcode,
        "suburbs": suburbs,
        "base_delivery_fee": base_delivery_fee,
        "distance_from_business": max_distance_km,
        "order_types": ["meal_subscription"],
        "is_active": True,
        "notes": notes or MEAL_SUBSCRIPTION_NOTE,
    }
    return payload


ZONE_1_FEE = 10.0
ZONE_2_FEE = 14.0
ZONE_3_FEE = 20.0

ZONE_1_DISTANCE = 14.0
ZONE_2_DISTANCE = 20.0
ZONE_3_DISTANCE = 30.0

DEFAULT_MEAL_DELIVERY_ZONES: List[Dict[str, object]] = [
    # Zone 1 (0-14 km)
    _zone("Zone 1 (0-14 km)", "2161", ["Guildford", "Guildford West", "Yennora", "Old Guildford"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2160", ["Merrylands", "Merrylands West"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2142", ["Granville", "South Granville", "Holroyd", "Rosehill", "Clyde"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2150", ["Parramatta", "Harris Park"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2145", ["Mays Hill", "Westmead", "South Wentworthville"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2165", ["Fairfield", "Fairfield East", "Fairfield Heights"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2162", ["Chester Hill", "Sefton"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2163", ["Villawood", "Carramar", "Lansdowne"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2141", ["Berala"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2143", ["Regents Park"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2144", ["Auburn"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2146", ["Toongabbie", "Old Toongabbie"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2147", ["Seven Hills"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2148", ["Smithfield", "Smithfield West", "Woodpark", "Wetherill Park"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2151", ["North Parramatta"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2152", ["Northmead"], ZONE_1_FEE, ZONE_1_DISTANCE),

    # Zone 2 (14-20 km)
    _zone("Zone 2 (14-20 km)", "2166", ["Cabramatta", "Cabramatta West", "Canley Vale", "Lansvale", "Canley Heights"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2168", ["Ashcroft", "Busby", "Cartwright", "Miller", "Heckenberg", "Sadlier"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2170", ["Liverpool", "Mount Pritchard", "Warwick Farm", "Lurnea", "Casula (north)"], ZONE_2_FEE, ZONE_2_DISTANCE, f"{MEAL_SUBSCRIPTION_NOTE} – northern catchment"),
    _zone("Zone 2 (14-20 km)", "2171", ["Hoxton Park", "Hinchinbrook", "Middleton Grange (north)", "Green Valley"], ZONE_2_FEE, ZONE_2_DISTANCE, f"{MEAL_SUBSCRIPTION_NOTE} – northern catchment"),
    _zone("Zone 2 (14-20 km)", "2153", ["Baulkham Hills", "Bella Vista", "Winston Hills"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2154", ["Castle Hill (southern side)", "Norwest"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2129", ["Homebush Bay"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2127", ["Sydney Olympic Park"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2126", ["Cherrybrook (southern side)"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2117", ["Dundas", "Telopea"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2122", ["Eastwood"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2118", ["Carlingford"], ZONE_2_FEE, ZONE_2_DISTANCE),

    # Zone 3 (20-30 km)
    _zone("Zone 3 (20-30 km)", "2170", ["Casula (south)", "Moorebank", "Chipping Norton", "Prestons"], ZONE_3_FEE, ZONE_3_DISTANCE, f"{MEAL_SUBSCRIPTION_NOTE} – southern catchment"),
    _zone("Zone 3 (20-30 km)", "2171", ["Middleton Grange (south)", "West Hoxton", "Carnes Hill"], ZONE_3_FEE, ZONE_3_DISTANCE, f"{MEAL_SUBSCRIPTION_NOTE} – southern catchment"),
    _zone("Zone 3 (20-30 km)", "2172", ["Sandy Point", "Voyager Point", "Pleasure Point"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2763", ["Quakers Hill"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2761", ["Glendenning", "Oakhurst"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2770", ["Rooty Hill", "Minchinbury"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2155", ["Kellyville", "Kellyville Ridge", "Beaumont Hills"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2156", ["Glenhaven", "Annangrove"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2157", ["Glenorie", "Canoelands", "Forest Glen"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2158", ["Dural", "Middle Dural", "Round Corner"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2159", ["Galston", "Arcadia", "Berrilee"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2765", ["Marsden Park", "Riverstone"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2565", ["Leppington (north)"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2167", ["Glenfield (south)"], ZONE_3_FEE, ZONE_3_DISTANCE),
]