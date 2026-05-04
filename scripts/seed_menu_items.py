"""
Utility script to seed categories and menu items into MongoDB.

Usage:
    python backend/scripts/seed_menu_items.py
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables (backend/.env)
load_dotenv(ENV_PATH)

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "bakars_food_catering")


def item(name: str, description: str, price: float, **extras) -> Dict:
    """Helper to build menu items with consistent defaults."""
    data = {
        "name": name,
        "description": description,
        "price": price,
    }
    data.update(extras)
    return data


DEFAULT_IMAGES = {
    "rice": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop&auto=format",
    "curry": "https://images.unsplash.com/photo-1604908177571-6c4c4b47f228?w=400&h=300&fit=crop&auto=format",
    "bbq": "https://images.unsplash.com/photo-1555992336-cbf7cc116b66?w=400&h=300&fit=crop&auto=format",
    "sweets": "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop&auto=format",
    "drinks": "https://images.unsplash.com/photo-1497534446932-c925b458314e?w=400&h=300&fit=crop&auto=format",
}


CATEGORIES = [
    {
        "name": "rice",
        "display_name": "Rice Dishes",
        "description": "Aromatic biryanis, pulaos, and specialty rice dishes crafted with premium ingredients.",
        "image_url": DEFAULT_IMAGES["rice"],
        "sort_order": 1,
    },
    {
        "name": "curry",
        "display_name": "Curries & Gravies",
        "description": "Slow-cooked curries ranging from family favourites to regional signatures with rich flavours.",
        "image_url": DEFAULT_IMAGES["curry"],
        "sort_order": 2,
    },
    {
        "name": "bbq",
        "display_name": "BBQ & Grill",
        "description": "Flame-grilled meats and vegetables marinated in authentic spice blends.",
        "image_url": DEFAULT_IMAGES["bbq"],
        "sort_order": 3,
    },
    {
        "name": "sweets",
        "display_name": "Desserts",
        "description": "Celebratory desserts and sweets inspired by South Asian favourites and modern twists.",
        "image_url": DEFAULT_IMAGES["sweets"],
        "sort_order": 4,
    },
    {
        "name": "drinks",
        "display_name": "Beverages",
        "description": "Refreshing seasonal beverages, lassis, and signature coolers for every occasion.",
        "image_url": DEFAULT_IMAGES["drinks"],
        "sort_order": 5,
    },
]


BASE_MENU_ITEMS: Dict[str, List[Dict]] = {
    "rice": [
        item(
            "Signature Chicken Biryani",
            "Fragrant basmati rice with tender chicken, saffron, and caramelised onions.",
            14.5,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Vegetable Dum Biryani",
            "Layered vegetables and basmati rice slow-cooked in dum style with whole spices.",
            12.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Lemon Curry Leaf Rice",
            "Tangy tempered rice with mustard seeds, peanuts, and fresh lemon.",
            11.0,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["peanuts"],
        ),
        item(
            "Jeera Tempered Rice",
            "Classic cumin-infused rice pilaf perfect for pairing with curries.",
            9.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Mutton Shahi Biryani",
            "Royal-style lamb biryani finished with ghee and saffron milk.",
            16.5,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Paneer Tikka Pulao",
            "Smoky paneer cubes tossed through spiced basmati rice with peppers.",
            13.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Coconut Cashew Rice",
            "Gently spiced coconut milk rice with toasted cashews and curry leaves.",
            11.5,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["tree nuts"],
        ),
        item(
            "Garlic Butter Rice Pilaf",
            "Golden rice sautéed with roasted garlic, herbs, and butter.",
            10.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Egg Masala Fried Rice",
            "Street-style fried rice with fluffy eggs, peppers, and scallions.",
            11.0,
            allergens=["egg", "soy"],
        ),
        item(
            "Schezwan Chicken Fried Rice",
            "Indo-Chinese fried rice tossed with fiery Schezwan sauce and chicken.",
            13.0,
            spice_level="hot",
            allergens=["soy"],
            is_halal=True,
        ),
        item(
            "Herb Infused Brown Rice",
            "Nutty brown rice cooked with fresh herbs, cumin, and roasted seeds.",
            11.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Tandoori Prawn Biryani",
            "Char-grilled prawns folded through aromatic biryani rice.",
            16.0,
            spice_level="medium",
            allergens=["shellfish", "dairy"],
        ),
        item(
            "Spinach Chickpea Pilaf",
            "Protein-rich chickpeas with wilted spinach and fluffy rice.",
            11.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Zafrani Chicken Pilaf",
            "Saffron scented rice with chicken morsels and toasted almonds.",
            14.0,
            allergens=["tree nuts"],
            is_halal=True,
        ),
        item(
            "Corn Methi Rice",
            "Sweet corn kernels with fenugreek leaves and mild spices.",
            11.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Smoked Lamb Pilaf",
            "Smoky lamb pieces tossed with caramelised onions and basmati rice.",
            15.5,
            spice_level="medium",
            is_halal=True,
        ),
        item(
            "Cashew Raisin Pulao",
            "Festive pulao dotted with raisins, cashews, and whole spices.",
            12.0,
            is_vegetarian=True,
            allergens=["tree nuts"],
        ),
        item(
            "Quinoa Vegetable Khichdi",
            "Wholesome quinoa and lentil khichdi with seasonal vegetables.",
            12.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Turmeric Coconut Rice",
            "Sunshine turmeric rice finished with coconut oil and curry leaves.",
            11.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Harvest Wild Mushroom Rice",
            "Earthy mushrooms folded through herb butter rice with pepper.",
            12.5,
            is_vegetarian=True,
        ),
    ],
    "curry": [
        item(
            "Butter Chicken Deluxe",
            "Creamy tomato gravy with tandoor-roasted chicken and fenugreek.",
            15.5,
            spice_level="mild",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Paneer Makhani Supreme",
            "Silky tomato and cashew sauce with soft paneer cubes.",
            14.0,
            spice_level="mild",
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Lamb Rogan Josh",
            "Kashmiri-style lamb curry simmered with yogurt and aromatic spices.",
            16.5,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Goan Prawn Curry",
            "Tangy coconut curry with prawns, kokum, and curry leaves.",
            17.0,
            spice_level="medium",
            allergens=["shellfish"],
        ),
        item(
            "Chickpea Masala Pot",
            "Hearty chickpeas cooked in onion-tomato masala with garam spices.",
            12.0,
            spice_level="medium",
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Beef Madras Curry",
            "South Indian style beef curry with roasted chilies and coconut.",
            16.0,
            spice_level="hot",
        ),
        item(
            "Vegetable Korma Royale",
            "Cashew cream curry with seasonal vegetables and mild spices.",
            13.5,
            spice_level="mild",
            is_vegetarian=True,
            allergens=["tree nuts", "dairy"],
        ),
        item(
            "Chicken Chettinad Roast",
            "Peppery Chettinad chicken with roasted coconut and curry leaves.",
            15.0,
            spice_level="hot",
            is_halal=True,
        ),
        item(
            "Palak Paneer Classic",
            "Spinach puree with cottage cheese cubes and ghee tempering.",
            13.0,
            spice_level="mild",
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Fish Moilee Coconut",
            "Kerala coconut milk curry with fish fillets and ginger.",
            16.0,
            spice_level="medium",
            allergens=["fish"],
        ),
        item(
            "Dal Makhani Signature",
            "Slow-cooked black lentils finished with cream and butter.",
            12.5,
            spice_level="mild",
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Pumpkin Coconut Curry",
            "Roasted pumpkin in spiced coconut gravy with toasted seeds.",
            12.0,
            spice_level="mild",
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Chicken Tikka Masala",
            "Charcoal-grilled chicken in smoky tomato cream sauce.",
            15.0,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Egg Masala Curry",
            "Boiled eggs simmered in spiced onion-tomato gravy.",
            12.0,
            spice_level="medium",
            allergens=["egg"],
        ),
        item(
            "Thai Green Veg Curry",
            "Lemongrass and coconut curry with Asian greens and basil.",
            14.0,
            spice_level="medium",
            is_vegetarian=True,
        ),
        item(
            "Kashmiri Dum Aloo",
            "Baby potatoes in yogurt gravy with Kashmiri chili.",
            13.0,
            spice_level="medium",
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Goat Vindaloo Fire",
            "Vinegar-marinated goat curry with bold spices and heat.",
            16.5,
            spice_level="hot",
            is_halal=True,
        ),
        item(
            "Tofu Tikka Curry",
            "Charred tofu cubes in dairy-free tikka masala sauce.",
            13.5,
            spice_level="medium",
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Black Pepper Prawn Curry",
            "Pepper-spiced prawn curry with coconut milk and garlic.",
            17.0,
            spice_level="medium",
            allergens=["shellfish"],
        ),
        item(
            "Malabar Chicken Stew",
            "Mild coconut stew with chicken, vegetables, and whole spices.",
            14.0,
            spice_level="mild",
            is_halal=True,
        ),
    ],
    "bbq": [
        item(
            "Smoky Tandoori Chicken",
            "Char-grilled chicken marinated in yogurt, chili, and garam masala.",
            15.0,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "BBQ Lamb Chops",
            "Tender lamb chops marinated in herbs and grilled over charcoal.",
            18.5,
            spice_level="medium",
            is_halal=True,
        ),
        item(
            "Paneer Tikka Skewers",
            "Paneer cubes with peppers grilled in smoky tikka marinade.",
            14.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "BBQ Prawn Skewers",
            "Juicy prawns brushed with garlic butter and grilled.",
            17.5,
            spice_level="medium",
            allergens=["shellfish"],
        ),
        item(
            "Spicy Seekh Kebabs",
            "Ground lamb seekh kebabs with fresh herbs and chilies.",
            15.5,
            spice_level="hot",
            is_halal=True,
        ),
        item(
            "BBQ Chicken Wings",
            "Tamarind glazed wings finished with sesame smoke.",
            13.0,
            spice_level="medium",
            is_halal=True,
        ),
        item(
            "Grilled Corn Cob",
            "Charred corn brushed with lime chili seasoning.",
            8.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "BBQ Vegetable Platter",
            "Seasonal vegetables flame-grilled with smoked paprika oil.",
            12.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Charcoal Grilled Fish",
            "Whole fish with lemon herb rub grilled over charcoal.",
            18.0,
            spice_level="medium",
            allergens=["fish"],
        ),
        item(
            "BBQ Jackfruit Burnt Ends",
            "Pulled jackfruit caramelised in tangy BBQ sauce.",
            13.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Chicken Malai Tikka",
            "Creamy malai marinade with cheese, cream, and mild spices.",
            15.5,
            spice_level="mild",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "BBQ Beef Ribs",
            "Slow-smoked beef ribs finished with tamarind glaze.",
            19.5,
            spice_level="medium",
        ),
        item(
            "Tandoori Salmon Fillet",
            "Salmon fillet marinated in yogurt, dill, and mild chili.",
            18.5,
            spice_level="mild",
            allergens=["fish", "dairy"],
        ),
        item(
            "Peri Peri Chicken Skewers",
            "Fiery peri peri marinated chicken skewers flame-grilled.",
            15.0,
            spice_level="hot",
            is_halal=True,
        ),
        item(
            "BBQ Mushroom Medley",
            "Portobello and shiitake mushrooms with garlic herb glaze.",
            12.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Smoked Sausage Platter",
            "Assorted smoked chicken and beef sausages with mustard.",
            14.5,
            spice_level="medium",
        ),
        item(
            "BBQ Cauliflower Steaks",
            "Harissa spiced cauliflower steaks charred over grill.",
            11.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Lamb Kofta Kebabs",
            "Hand-rolled lamb kofta with mint and toasted spices.",
            16.0,
            spice_level="medium",
            is_halal=True,
        ),
        item(
            "BBQ Pineapple Rings",
            "Caramelised pineapple rings dusted with chili sugar.",
            8.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Korean BBQ Short Ribs",
            "Sweet and savoury gochujang glazed beef short ribs.",
            18.5,
            spice_level="medium",
            allergens=["soy", "sesame"],
        ),
    ],
    "sweets": [
        item(
            "Rasmalai Royale",
            "Soft paneer discs soaked in saffron cardamom milk.",
            8.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Gulab Jamun Supreme",
            "Golden fried milk dumplings in rose scented syrup.",
            7.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Kesar Kulfi Delight",
            "Slow churned saffron pistachio kulfi on a stick.",
            6.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Mango Lassi Cheesecake",
            "Baked cheesecake with mango puree and yogurt glaze.",
            8.0,
            is_vegetarian=True,
            allergens=["dairy", "gluten"],
        ),
        item(
            "Cardamom Rice Kheer",
            "Creamy rice pudding simmered with almonds and saffron.",
            7.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Chocolate Jalebi Sundae",
            "Crisp jalebi spirals layered with chocolate ice cream.",
            8.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts", "gluten"],
        ),
        item(
            "Rose Pistachio Truffle",
            "Hand-rolled truffles with rose petals and pistachio dust.",
            6.0,
            is_vegetarian=True,
            allergens=["tree nuts"],
        ),
        item(
            "Baked Rasgulla Pudding",
            "Spongy rasgullas baked in sweet custard and caramel.",
            7.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Coconut Barfi Bites",
            "Toasted coconut fudge squares with cardamom.",
            6.0,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["tree nuts"],
        ),
        item(
            "Masala Chai Tiramisu",
            "Fusion tiramisu soaked in masala chai syrup.",
            8.0,
            is_vegetarian=True,
            allergens=["dairy", "gluten"],
        ),
        item(
            "Saffron Phirni Cups",
            "Ground rice pudding served chilled with pistachios.",
            7.0,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Kesari Sheera Pots",
            "Semolina pudding with ghee, saffron, and cashews.",
            6.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Chocolate Chai Brownie",
            "Fudgy brownie infused with chai spice blend.",
            6.5,
            is_vegetarian=True,
            allergens=["dairy", "gluten"],
        ),
        item(
            "Pistachio Baklava Cups",
            "Mini baklava bites with pistachio and honey drizzle.",
            7.5,
            is_vegetarian=True,
            allergens=["tree nuts", "gluten"],
        ),
        item(
            "Malai Sandwich Delight",
            "Layered Bengali sweet with clotted cream filling.",
            7.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Carrot Halwa Tart",
            "Butter tart shell filled with gajar halwa and nuts.",
            8.0,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts", "gluten"],
        ),
        item(
            "Masala Panna Cotta",
            "Vanilla panna cotta finished with cardamom caramel.",
            7.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Coconut Jaggery Payasam",
            "Coconut milk payasam with jaggery and roasted cashews.",
            6.5,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["tree nuts"],
        ),
        item(
            "Saffron Basque Cheesecake",
            "Burnt basque cheesecake with saffron accents.",
            8.5,
            is_vegetarian=True,
            allergens=["dairy", "gluten"],
        ),
        item(
            "Rose Falooda Parfait",
            "Layered falooda with basil seeds, jelly, and kulfi.",
            7.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
    ],
    "drinks": [
        item(
            "Rose Cardamom Lassi",
            "Refreshing yogurt drink blended with rose syrup and cardamom.",
            6.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Mango Mint Cooler",
            "Chilled mango nectar with muddled mint and lime.",
            5.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Masala Chaas",
            "Spiced buttermilk with toasted cumin and coriander.",
            5.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Kesar Pista Milkshake",
            "Rich saffron pistachio milkshake topped with nuts.",
            6.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Tamarind Ginger Spritz",
            "Sweet and tangy tamarind cooler with ginger fizz.",
            5.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Filter Coffee Frappe",
            "Iced frappe prepared with South Indian filter coffee.",
            5.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Lychee Rose Sangria",
            "Non-alcoholic sangria with lychee, rose, and citrus.",
            5.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Masala Lime Soda",
            "Sparkling lime soda seasoned with chaat masala.",
            4.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Kokum Mint Cooler",
            "Konkan-style kokum sherbet with mint and jaggery.",
            5.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Saffron Badam Milk",
            "Warm almond milk infused with saffron and cardamom.",
            5.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Cold Brew Spice Latte",
            "Cold brew coffee with cinnamon, star anise, and cream.",
            5.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Pineapple Jalapeno Refresher",
            "Sweet pineapple cooler balanced with jalapeno heat.",
            5.5,
            spice_level="medium",
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Thandai Festival Shake",
            "Festival favourite with soaked nuts and fennel.",
            6.0,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Cucumber Basil Cooler",
            "Hydrating cucumber juice with basil and lime.",
            4.8,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Turmeric Golden Latte",
            "Anti-inflammatory turmeric latte with honey and pepper.",
            5.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Spiced Apple Punch",
            "Warm apple punch with cinnamon, cloves, and citrus.",
            5.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Jamun Kala Khatta Slush",
            "Vibrant black plum slush with tangy spice blend.",
            5.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Caramel Date Shake",
            "Smooth date shake blended with caramel and almond milk.",
            6.0,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["tree nuts"],
        ),
        item(
            "Lemongrass Iced Tea",
            "Refreshing iced tea brewed with lemongrass and lime.",
            4.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Rose Coconut Smoothie",
            "Creamy coconut milk smoothie perfumed with rose water.",
            5.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
    ],
}


def get_menu_items() -> Dict[str, List[Dict]]:
    """Return deep copies of the seed menu items to avoid mutation."""
    return {category: [dict(item_) for item_ in items] for category, items in BASE_MENU_ITEMS.items()}


async def seed_categories(db) -> Dict[str, str]:
    """Insert or update categories and return their IDs."""
    categories_collection = db.categories
    category_ids: Dict[str, str] = {}

    for category in CATEGORIES:
        existing = await categories_collection.find_one({"name": category["name"]})
        payload = {
            **category,
            "is_active": True,
            "updated_at": datetime.utcnow(),
        }
        if existing:
            await categories_collection.update_one({"_id": existing["_id"]}, {"$set": payload})
            category_ids[category["name"]] = str(existing["_id"])
        else:
            payload["created_at"] = datetime.utcnow()
            result = await categories_collection.insert_one(payload)
            category_ids[category["name"]] = str(result.inserted_id)

    return category_ids


def build_menu_item_payload(item_data: Dict, category: str) -> Dict:
    """Prepare a menu item document ready for insert/update."""
    now = datetime.utcnow()
    payload = {
        "name": item_data["name"],
        "description": item_data.get("description"),
        "category": category,
        "price": float(item_data["price"]),
        "image_url": item_data.get("image_url", DEFAULT_IMAGES.get(category)),
        "is_available": item_data.get("is_available", True),
        "is_available_for_daily": item_data.get("is_available_for_daily", True),
        "is_available_for_meal_plan": item_data.get("is_available_for_meal_plan", True),
        "allergens": item_data.get("allergens", []),
        "spice_level": item_data.get("spice_level"),
        "is_vegetarian": item_data.get("is_vegetarian", False),
        "is_vegan": item_data.get("is_vegan", False),
        "is_halal": item_data.get("is_halal", True),
        "nutritional_info": item_data.get("nutritional_info"),
        "serving_size": item_data.get("serving_size", "Single serve"),
        "created_at": now,
        "updated_at": now,
    }
    return payload


async def seed_menu_items(db):
    """Ensure each category has at least 20 menu items."""
    menu_collection = db.menu_items
    menu_items = get_menu_items()

    for category, items in menu_items.items():
        for item_data in items:
            payload = build_menu_item_payload(item_data, category)
            existing = await menu_collection.find_one({"name": payload["name"], "category": category})
            if existing:
                payload["created_at"] = existing.get("created_at", payload["created_at"])
                await menu_collection.update_one({"_id": existing["_id"]}, {"$set": payload})
            else:
                await menu_collection.insert_one(payload)

        count = await menu_collection.count_documents({"category": category})
        if count < 20:
            raise RuntimeError(f"Category '{category}' has only {count} items after seeding.")


async def main():
    if not MONGODB_URL:
        raise EnvironmentError("MONGODB_URL is not configured. Check backend/.env.")

    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]

    try:
        await client.admin.command("ping")
        print("MongoDB connection successful.")

        category_ids = await seed_categories(db)
        print(f"Upserted categories: {', '.join(category_ids.keys())}")

        await seed_menu_items(db)

        menu_collection = db.menu_items
        print("\nMenu item counts by category:")
        for category in BASE_MENU_ITEMS.keys():
            count = await menu_collection.count_documents({"category": category})
            print(f" - {category}: {count} items")

        print("\nSeeding completed successfully.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
