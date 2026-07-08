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

CITY = "Portland, OR"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SerpApi has a rate limit; space out requests
DELAY = 3  # seconds between searches

SERPAPI_BASE = "https://serpapi.com/search"


SEARCHES = [
    # ── Restaurants ──
    {
        "name": "restaurants_best",
        "query": f"best restaurants in {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_brunch",
        "query": f"best brunch spots in {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_food_carts",
        "query": f"best food carts in {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_date_night",
        "query": f"romantic date night restaurants {CITY}",
        "category": "restaurant",
    },
    {
        "name": "restaurants_hidden_gems",
        "query": f"hidden gem restaurants {CITY}",
        "category": "restaurant",
    },

    # ── Groceries ──
    {
        "name": "groceries_best",
        "query": f"best grocery stores in {CITY}",
        "category": "grocery",
    },
    {
        "name": "groceries_organic",
        "query": f"organic farmers market {CITY}",
        "category": "grocery",
    },
    {
        "name": "groceries_specialty",
        "query": f"specialty food stores {CITY}",
        "category": "grocery",
    },

    # ── Services ──
    {
        "name": "services_salon",
        "query": f"best hair salon in {CITY}",
        "category": "service",
    },
    {
        "name": "services_fitness",
        "query": f"best gym fitness studio {CITY}",
        "category": "service",
    },
    {
        "name": "services_repair",
        "query": f"best shoe repair cobbler {CITY}",
        "category": "service",
    },
    {
        "name": "services_wellness",
        "query": f"best spa massage {CITY}",
        "category": "service",
    },

    # ── Entertainment ──
    {
        "name": "entertainment_nightlife",
        "query": f"best nightlife bars in {CITY}",
        "category": "entertainment",
    },
    {
        "name": "entertainment_music",
        "query": f"best live music venues {CITY}",
        "category": "entertainment",
    },
    {
        "name": "entertainment_parks",
        "query": f"best parks things to do {CITY}",
        "category": "entertainment",
    },
    {
        "name": "entertainment_museums",
        "query": f"best museums {CITY}",
        "category": "entertainment",
    },

    # ── Health ──
    {
        "name": "health_pharmacy",
        "query": f"best pharmacies in {CITY}",
        "category": "health",
    },
    {
        "name": "health_urgent_care",
        "query": f"urgent care clinic {CITY}",
        "category": "health",
    },
    {
        "name": "health_dental",
        "query": f"best dentist in {CITY}",
        "category": "health",
    },

    # ── Shipping ──
    {
        "name": "shipping_post_office",
        "query": f"post office in {CITY}",
        "category": "shipping",
    },
    {
        "name": "shipping_shipping_centers",
        "query": f"shipping UPS FedEx center {CITY}",
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
