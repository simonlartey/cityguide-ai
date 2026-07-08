#!/usr/bin/env python3
"""
CityGuide AI — Chat Server
Loads Portland places data and serves it to the LLM for recommendations.

Usage:
    pip install flask openai
    export OPENAI_API_KEY="your_key_here"
    python server.py
"""

import json
import re
import os
from pathlib import Path

from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import requests

# ── Load private config ─────────────────────────────────────

LOCAL_PATH = Path(__file__).parent / "local"
_env = LOCAL_PATH.read_text() if LOCAL_PATH.exists() else ""
for line in _env.splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())

# ── Config ──────────────────────────────────────────────────

app = Flask(__name__)
client = OpenAI(
    api_key=os.environ.get("LITELLM_API_KEY"),
    base_url=os.environ.get("LITELLM_BASE_URL"),
)

MODEL = os.environ.get("LITELLM_MODEL", "qwen-3.6-27b")

PLACES_PATH = Path(__file__).parent / "data" / "places.json"

# Load places data
places = json.loads(PLACES_PATH.read_text()) if PLACES_PATH.exists() else []

# ── System prompt — Portland, ME, college student focus ─────

SYSTEM_PROMPT = """You are CityGuide AI, a Portland, Maine local recommendations expert for college students.

YOUR RULES:
- You ONLY know about Portland, ME. If someone asks about another city, politely say you only cover Portland, Maine.
- You know about restaurants, groceries, housing, study spaces, shopping, entertainment, fitness, health, services, transportation, auto repair, pet services, banking, and shipping.
- Always recommend real places from the data provided — never make up a place.
- When recommending, include: name, rating (out of 5), price range, address, and why it's good for a student.
- Be warm, concise, and local in tone — like a friendly local giving insider advice to a new student.
- Prioritize affordable, student-friendly options when possible.
- If you don't have relevant data for a question, say so honestly.
- Keep responses under 150 words unless the user asks for more detail.
- Offer to narrow down or provide more options if relevant.

Here is the data you have access to:

{places_data}"""


# ── Data Retrieval ──────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "restaurant": [
        "restaurant", "food", "eat", "lunch", "dinner", "brunch", "breakfast",
        "cook", "cafe", "coffee", "pizza", "sushi", "burger", "taco", "asian",
        "italian", "mexican", "indian", "ethiopian", "vegan", "vegetarian",
        "dine", "meal", "snack", "dessert", "hungry", "chef", "menu",
        "wine", "cocktail", "bar", "pub", "taproom", "brewery",
        "cheap eats", "affordable", "budget", "late night", "ramen", "fast food",
    ],
    "groceries": [
        "grocery", "market", "supermarket", "food store", "produce", "organic",
        "farmers", "whole foods", "trader", "natural", "health food", "deli",
        "butcher", "bakery", "bread", "shop", "buy", "dollar store", "budget",
        "cheap", "affordable", "groceries",
    ],
    "housing": [
        "apartment", "rent", "housing", "sublet", "roommate", "room", "lease",
        "dorm", "off-campus", "living", "move in", "landlord", "complex",
        "short term", "airbnb", "hotel", "stay",
    ],
    "study": [
        "study", "library", "quiet", "homework", "reading", "work", "coworking",
        "laptop", "wifi", "desk", "focus", "exam", "research",
    ],
    "shopping": [
        "shop", "store", "retail", "clothes", "thrift", "secondhand", "consignment",
        "discount", "bargain", "sale", "mall", "pharmacy", "drugstore",
        "cvs", "walgreens", "dollar", "cheap", "affordable",
    ],
    "entertainment": [
        "fun", "nightlife", "bar", "club", "music", "concert", "show", "movie",
        "park", "hike", "museum", "art", "gallery", "event", "activity",
        "outdoor", "trail", "zoo", "aquarium", "theater", "comedy",
        "thing to do", "weekend", "hang out", "party", "live music", "brewery",
        "beer", "happy hour", "recreation", "entertainment",
    ],
    "fitness": [
        "gym", "fitness", "workout", "exercise", "yoga", "pilates", "train",
        "crossfit", "running", "trail", "swim", "pool", "sport", "active",
        "cheap gym", "budget fitness", "student discount",
    ],
    "health": [
        "pharmacy", "drug", "medicine", "urgent", "clinic", "hospital",
        "doctor", "dentist", "vet", "veterinary", "health", "medical",
        "prescription", "cvs", "walgreens", "dental", "mental health",
        "therapy", "counseling",
    ],
    "services": [
        "salon", "hair", "nail", "spa", "massage", "repair", "cobbler", "shoe",
        "laundry", "laundromat", "dry clean", "wellness", "beauty", "style",
        "barber", "thread", "wax", "tattoo", "piercing", "print", "printing",
        "copy", "photocopy", "dry cleaner",
    ],
    "transport": [
        "bus", "transit", "train", "subway", "metro", "bicycle", "bike",
        "gas station", "fuel", "parking", "ride share", "uber", "lyft",
        "car rental", "shuttle", "ferry",
    ],
    "auto": [
        "auto", "car repair", "mechanic", "oil change", "tire", "flat",
        "car wash", "detailing", "parts", "smog", "inspection", "body shop",
    ],
    "pets": [
        "pet", "dog", "cat", "veterinary", "vet", "pet store", "dog park",
        "grooming", "groomer", "pet food", "animal", "paw",
    ],
    "finance": [
        "bank", "atm", "cash", "credit union", "money", "finance",
        "withdraw", "deposit", "checking", "savings", "loan",
    ],
    "shipping": [
        "ship", "shipping", "post", "mail", "package", "ups", "fedex",
        "usps", "dhl", "deliver", "delivery", "pickup", "locker", "parcel",
        "postal", "stamp",
    ],
}


def retrieve_places(query: str, top_per_category: int = 8) -> list:
    """Find relevant places from the dataset based on the user query."""
    query_lower = query.lower()
    matched_categories = set()

    # Find which categories are relevant
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            matched_categories.add(cat)

    # If no category matched, include all (general question)
    if not matched_categories:
        matched_categories = set(CATEGORY_KEYWORDS.keys())

    # Score places by relevance
    scored = []
    for place in places:
        score = 0
        p_text = " ".join(
            str(v) for v in [
                place.get("title", ""),
                place.get("description", ""),
                place.get("type", ""),
                place.get("address", ""),
                place.get("price", ""),
            ]
        ).lower()

        # Category match (required)
        if place.get("category") not in matched_categories:
            continue

        # Keyword relevance
        for word in query_lower.split():
            if len(word) > 2 and word in p_text:
                score += 3

        # Boost highly rated places
        rating = place.get("rating")
        if rating:
            score += rating * 2

        if score > 0:
            scored.append((score, place))

    # Sort by score and take top N per category
    scored.sort(key=lambda x: x[0], reverse=True)

    result = []
    cat_counts = {}
    for _, place in scored:
        cat = place.get("category", "")
        if cat_counts.get(cat, 0) < top_per_category:
            result.append(place)
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

    return result[:30]  # cap total


def format_places_data(places_list: list) -> str:
    """Format places into a compact text block for the LLM."""
    lines = []
    for i, p in enumerate(places_list, 1):
        lines.append(
            f"{i}. {p.get('title', 'Unknown')} | ⭐{p.get('rating', '?')} "
            f"({p.get('reviews', '?')} reviews) | {p.get('price', 'N/A')} | "
            f"{p.get('address', '')} | {p.get('type', '')} | "
            f"'{p.get('description', '')}'"
        )
    return "\n".join(lines)


# ── Chat endpoint ──────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data["message"]

    # Retrieve relevant places
    relevant = retrieve_places(message)

    if not relevant:
        return jsonify({
            "reply": "I don't have data on that in Portland, ME. Try asking about restaurants, groceries, housing, study spaces, entertainment, fitness, health, laundromats, auto repair, pet services, banking, or shipping!"
        })

    # Build prompt
    places_text = format_places_data(relevant)
    system = SYSTEM_PROMPT.replace("{places_data}", places_text)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=500,
            extra_body={"reasoning_effort": "none"},
        )
        reply = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": f"LLM error: {str(e)}"}), 500

    return jsonify({"reply": reply})


# ── Health check ───────────────────────────────────────────

@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "places_loaded": len(places)})


# ── Run ────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"🤖 CityGuide AI loaded {len(places)} places")
    print("🚀 Running at http://localhost:5000")
    app.run(port=5000, debug=True)
