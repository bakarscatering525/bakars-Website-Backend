"""
Seed the delivery_zones collection with the default meal-subscription coverage.

Usage:
    python backend/scripts/seed_delivery_zones.py

The script is idempotent: it only inserts records when the collection is empty.
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from app.utils.default_delivery_zones import DEFAULT_MEAL_DELIVERY_ZONES

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "bakars_food_catering")


async def seed_zones() -> None:
    if not MONGODB_URL:
        raise RuntimeError("MONGODB_URL is not set. Please configure backend/.env before seeding.")

    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    collection = db.delivery_zones

    try:
        existing = await collection.count_documents({})
        if existing > 0:
            print(f"Delivery zones already present ({existing} documents). Nothing to seed.")
            return

        now = datetime.utcnow()
        documents: List[Dict[str, Any]] = []

        for zone in DEFAULT_MEAL_DELIVERY_ZONES:
            payload = dict(zone)
            payload.setdefault("state", "NSW")
            payload.setdefault("order_types", ["meal_subscription"])
            payload.setdefault("is_active", True)
            payload["created_at"] = now
            payload["updated_at"] = now
            documents.append(payload)

        if not documents:
            print("No default delivery zones defined; nothing to seed.")
            return

        result = await collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} delivery zones.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_zones())
