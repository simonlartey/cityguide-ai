# CityGuide AI — Project Brief

## Vision
An AI-powered chatbot that helps people discover the best local places in specific cities — restaurants, grocery stores, services, entertainment, and more. Users ask naturally in plain English and get tailored, personalized recommendations.

## Core Product
- **Chat-first interface** — users type questions like "Where can I find a cheap apartment?" or "Best late-night food under $15?"
- **City-limited** — launches city by city with curated, accurate data per location.
- **No signup required** to start chatting.
- **Target audience: College students relocating to a new city.**
- **Categories covered:**
  - 🍽️ Restaurants (cheap eats, late night, budget-friendly, coffee shops)
  - 🛒 Groceries (budget stores, farmers markets, dollar stores)
  - 🏠 Housing (apartments, short-term rentals, sublets, roommates)
  - 📚 Study Spaces (quiet cafes, libraries, coworking)
  - 🛍️ Shopping (thrift stores, discount retail, pharmacies)
  - 🎭 Entertainment (nightlife, live music, hiking, museums, parks)
  - 🏋️ Fitness (cheap gyms, yoga, running trails)
  - 🏥 Health (urgent care, pharmacies, mental health)
  - 💇 Services (laundromats, dry cleaning, print shops, hair salons)
  - 🚗 Transport (gas stations, bike shops, bus routes)
  - 🔧 Auto Repair (cheap mechanics, car wash, parts)
  - 🐾 Pet Services (vets, pet stores, dog parks)
  - 🏦 Banking (ATMs, banks, credit unions)
  - 📦 Shipping (post office, UPS, FedEx)

## Launch City
- Portland, ME (Maine)

## Design Direction
- **Color:** Green accent (#16a34a) — fresh, local, trustworthy
- **Style:** Clean, card-based, modern, minimal
- **Typography:** System font stack (Apple System, Segoe UI, Roboto)
- **Responsive:** Mobile-first
- **No external dependencies** for initial mockup (pure HTML/CSS)

## Tech Stack
*(TBD — to be decided)*

## Repo
- **Local:** `/Users/davidjohnson/Desktop/cityguide-ai`
- **Remote:** `https://github.com/simonlartey/cityguide-ai.git`
- **Branch:** `main`

## Current Status
- [x] Homepage mockup designed (`index.html`)
- [x] Data pipeline designed (SerpApi scraper)
- [x] Initial data scraped — 346 unique Portland OR places
- [x] Chat server built (`server.py`)
- [x] Chat interface built (`templates/chat.html`)
- [x] LLM wired up — `qwen-3.6-27b` via LiteLLM
- [x] Pivoted to Portland, ME — college student focus
- [x] Expanded categories to 14 (housing, study, auto, pets, finance, etc.)
- [x] Expanded scraper to 60+ search queries
- [ ] Re-scrape Portland, ME data
- [ ] Test & refine with ME data
- [ ] Deploy

## Tech Stack
- **Backend:** Flask + Python 3.11
- **LLM:** `qwen-3.6-27b` via LiteLLM (same model as Hermes)
- **Data:** Portland, ME places via SerpApi (Google Maps) — 14 categories, 60+ queries
- **Frontend:** Pure HTML/CSS/JS (no framework)
- **Target Audience:** College students relocating to a new city

## Decisions Log
| Date | Decision | Reason |
|------|----------|--------|
| 2025-07-07 | Green accent color | Fresh, local, trustworthy vibe |
| 2025-07-07 | Chat-first UX | Most natural way to ask for recommendations |
| 2025-07-07 | Single city: Portland | Deep coverage over broad coverage |
| 2025-07-07 | SerpApi for data scraping | Structured Google Maps results with ratings, hours, reviews in one shot |
| 2025-07-07 | qwen-3.6-27b via LiteLLM | Same model Hermes uses — no external API dependency |
| 2026-07-07 | Keyword-based retrieval + LLM | Simple, reliable, no vector DB needed for ~500 places |
| 2026-07-08 | Pivoted to Portland, ME | Focus on college student relocation needs |
| 2026-07-08 | Expanded to 14 categories | Housing, study, auto, pets, finance, transport, fitness, shopping |
| 2026-07-08 | 60+ SerpApi queries | Broader coverage for student services |

## Notes
- Add new decisions, changes, and course corrections here as the project evolves.
