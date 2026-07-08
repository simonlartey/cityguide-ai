#!/usr/bin/env python3
"""
CityGuide AI — Data Scraper
Pulls Google Maps local results for Portland across all categories via SerpApi REST API.

Usage:
    pip install requests
    python scripts/scrape.py
"""

import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

# ── Load private config ─────────────────────────────────────

LOCAL_PATH = Path(__file__).parent.parent / "local"
_env = LOCAL_PATH.read_text() if LOCAL_PATH.exists() else ""
for line in _env.splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())

# ── Config ──────────────────────────────────────────────────

CITY = "Portland, ME"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SerpApi has a rate limit; space out requests
DELAY = 3  # seconds between searches

SERPAPI_BASE = "https://serpapi.com/search"


SEARCHES = [
    # ── Food & Dining (College Student Essentials) ───────
    {
        "name": "restaurants_cheap",
        "query": f"cheap restaurants in {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_affordable",
        "query": f"affordable restaurants in {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_fast_food",
        "query": f"fast food near {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_pizza",
        "query": f"best pizza in {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_coffee",
        "query": f"best coffee shops in {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_late_night",
        "query": f"late night food in {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_brunch",
        "query": f"best brunch spots in {CITY}",
        "category": "restaurant",
    },
    # ── Groceries (Budget-Friendly) ──────────────────────
    {
        "name": "groceries_cheap",
        "query": f"cheap grocery stores in {CITY}",
        "category": "groceries",
    },
    {
        "name": "groceries_farmers",
        "query": f"farmers market near {CITY}",
        "category": "groceries",
    },
    {
        "name": "groceries_dollar",
        "query": f"dollar store near {CITY}",
        "category": "groceries",
    },
    # ── Housing (College Student Needs) ──────────────────
    {
        "name": "housing_apartments",
        "query": f"apartments for rent in {CITY}",
        "category": "housing",
    },
    {
        "name": "housing_short_term",
        "query": f"short term rentals in {CITY}",
        "category": "housing",
    },
    {
        "name": "housing_roommate",
        "query": f"roommate sublet in {CITY}",
        "category": "housing",
    },
    # ── Study Spaces (Quiet & Productive) ────────────────
    {
        "name": "study_cafes",
        "query": f"quiet study cafes in {CITY}",
        "category": "study",
    },
    {
        "name": "study_libraries",
        "query": f"public libraries in {CITY}",
        "category": "study",
    },
    {
        "name": "study_coworking",
        "query": f"coworking spaces in {CITY}",
        "category": "study",
    },
    # ── Shopping (Discount & Thrift) ─────────────────────
    {
        "name": "shopping_thrift",
        "query": f"thrift stores in {CITY}",
        "category": "shopping",
    },
    {
        "name": "shopping_discount",
        "query": f"discount shopping in {CITY}",
        "category": "shopping",
    },
    {
        "name": "shopping_pharmacy",
        "query": f"pharmacy in {CITY}",
        "category": "shopping",
    },
    # ── Entertainment (Nightlife & Activities) ───────────
    {
        "name": "entertainment_nightlife",
        "query": f"bars and nightlife in {CITY}",
        "category": "entertainment",
    },
    {
        "name": "entertainment_live_music",
        "query": f"live music venues in {CITY}",
        "category": "entertainment",
    },
    {
        "name": "entertainment_hiking",
        "query": f"hiking trails near {CITY}",
        "category": "entertainment",
    },
    {
        "name": "entertainment_museums",
        "query": f"museums in {CITY}",
        "category": "entertainment",
    },
    {
        "name": "entertainment_parks",
        "query": f"parks in {CITY}",
        "category": "entertainment",
    },
    # ── Fitness (Gyms & Yoga) ────────────────────────────
    {
        "name": "fitness_gyms",
        "query": f"cheap gyms in {CITY}",
        "category": "fitness",
    },
    {
        "name": "fitness_yoga",
        "query": f"yoga studios in {CITY}",
        "category": "fitness",
    },
    {
        "name": "fitness_trails",
        "query": f"running trails in {CITY}",
        "category": "fitness",
    },
    # ── Health (Urgent Care & Mental Health) ─────────────
    {
        "name": "health_urgent",
        "query": f"urgent care in {CITY}",
        "category": "health",
    },
    {
        "name": "health_pharmacy",
        "query": f"pharmacy near {CITY}",
        "category": "health",
    },
    {
        "name": "health_mental",
        "query": f"mental health clinics in {CITY}",
        "category": "health",
    },
    # ── Essential Services (Laundry, Dry Cleaning, Print) ─
    {
        "name": "services_laundromat",
        "query": f"laundromat in {CITY}",
        "category": "services",
    },
    {
        "name": "services_dry_clean",
        "query": f"dry cleaning in {CITY}",
        "category": "services",
    },
    {
        "name": "services_print",
        "query": f"print shops in {CITY}",
        "category": "services",
    },
    {
        "name": "services_hair",
        "query": f"hair salons in {CITY}",
        "category": "services",
    },
    # ── Transportation (Gas, Bike, Bus) ──────────────────
    {
        "name": "transport_gas",
        "query": f"gas stations in {CITY}",
        "category": "transport",
    },
    {
        "name": "transport_bike",
        "query": f"bike shops in {CITY}",
        "category": "transport",
    },
    {
        "name": "transport_bus",
        "query": f"bus routes near {CITY}",
        "category": "transport",
    },
    # ── Auto Services (Car Repair, Oil Change) ───────────
    {
        "name": "auto_repair",
        "query": f"cheap car repair in {CITY}",
        "category": "auto",
    },
    {
        "name": "auto_wash",
        "query": f"car wash in {CITY}",
        "category": "auto",
    },
    {
        "name": "auto_parts",
        "query": f"auto parts in {CITY}",
        "category": "auto",
    },
    # ── Pet Services (Vet, Pet Stores, Dog Parks) ────────
    {
        "name": "pets_vet",
        "query": f"veterinary clinics in {CITY}",
        "category": "pets",
    },
    {
        "name": "pets_stores",
        "query": f"pet stores in {CITY}",
        "category": "pets",
    },
    {
        "name": "pets_dog_parks",
        "query": f"dog parks in {CITY}",
        "category": "pets",
    },
    # ── Banking & Finance (ATMs, Banks, Credit Unions) ───
    {
        "name": "finance_atm",
        "query": f"ATMs in {CITY}",
        "category": "finance",
    },
    {
        "name": "finance_banks",
        "query": f"banks in {CITY}",
        "category": "finance",
    },
    {
        "name": "finance_credit_union",
        "query": f"credit unions in {CITY}",
        "category": "finance",
    },
    # ── Shipping & Post (Post Office, UPS, FedEx) ────────
    {
        "name": "shipping_post",
        "query": f"post office in {CITY}",
        "category": "shipping",
    },
    {
        "name": "shipping_ups",
        "query": f"UPS shipping near {CITY}",
        "category": "shipping",
    },
    {
        "name": "shipping_fedex",
        "query": f"FedEx shipping near {CITY}",
        "category": "shipping",
    },
]


# ── Scraper ─────────────────────────────────────────────────

def search_google(query: str) -> dict:
    """Run a Google Maps search via SerpApi REST API."""
    params = {
        "engine": "google_maps",
        "q": query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": os.environ["SERPAPI_API_KEY"],
    }
    resp = requests.get(SERPAPI_BASE, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_places(raw: dict, search_name: str) -> list:
    """Extract structured place dicts from SerpApi results."""
    places = []

    # Local pack results (list of place dicts)
    for item in raw.get("local_results", []):
        places.append({
            "title": item.get("title"),
            "rating": item.get("rating"),
            "reviews": item.get("reviews"),
            "address": item.get("address"),
            "phone": item.get("phone"),
            "hours": item.get("hours"),
            "price": item.get("price"),
            "gps": {
                "lat": item.get("gps_coordinates", {}).get("latitude") if isinstance(item.get("gps_coordinates"), dict) else None,
                "lng": item.get("gps_coordinates", {}).get("longitude") if isinstance(item.get("gps_coordinates"), dict) else None,
            },
            "thumbnail": item.get("thumbnail"),
            "source": search_name,
            "place_id": item.get("place_id"),
            "google_url": item.get("link"),
            "description": item.get("description"),
            "type": item.get("type"),
        })

    return places


def run():
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        print("❌  No SerpApi key found.")
        print(f"   Add it to: {LOCAL_PATH}")
        print("   Format: SERPAPI_API_KEY=your_key_here")
        print("\nGet one free at https://serpapi.com/dashboard (100 searches/mo)")
        return

    all_places = []
    total = len(SEARCHES)

    for i, s in enumerate(SEARCHES, 1):
        name = s["name"]
        query = s["query"]
        category = s["category"]

        print(f"\n[{i}/{total}] Searching: {query}")

        try:
            raw = search_google(query)

            # Save raw JSON for debugging
            raw_path = OUTPUT_DIR / f"{name}.json"
            with open(raw_path, "w") as f:
                json.dump(raw, f, indent=2)

            places = extract_places(raw, name)
            for p in places:
                p["category"] = category
            all_places.extend(places)

            print(f"  ✓ Found {len(places)} places → {raw_path.name}")

        except requests.exceptions.HTTPError as e:
            print(f"  ✗ HTTP Error: {e.response.status_code} — {e.response.text[:200]}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        # Rate limit
        if i < total:
            time.sleep(DELAY)

    # ── Deduplicate ──
    seen = {}
    for p in all_places:
        key = p.get("title", "").lower().strip()
        if key not in seen or (p.get("rating") or 0) > (seen[key].get("rating") or 0):
            seen[key] = p

    deduped = list(seen.values())

    # ── Save unified places ──
    places_path = Path(__file__).parent.parent / "data" / "places.json"
    with open(places_path, "w") as f:
        json.dump(deduped, f, indent=2)

    # ── Summary ──
    categories = {}
    for p in deduped:
        cat = p.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\n{'='*50}")
    print(f"📊 Total scraped:  {len(all_places)}")
    print(f"📊 Unique places:  {len(deduped)}")
    print(f"💾 Saved to:        {places_path}")
    print(f"\n📂 By category:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count}")


if __name__ == "__main__":
    run()
