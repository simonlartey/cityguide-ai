# CityGuide AI — Project Brief

## Vision
An AI-powered chatbot that helps college students discover the best local places in Portland, ME — apartments, cheap eats, study spots, laundromats, gyms, and everything else you need when moving to a new city. Users ask naturally in plain English and get tailored, personalized recommendations.

## Core Product
- **Chat-first interface** — users type questions like "Where can I find a cheap apartment?" or "Best late-night food under $15?"
- **City-limited** — Portland, ME only (deep coverage over broad coverage).
- **No signup required** to start chatting.
- **Target audience: College students relocating to a new city.**
- **Categories covered (14):**
  - 🍽️ Restaurants (cheap eats, late night, pizza, coffee, brunch)
  - 🛒 Groceries (budget stores, farmers markets, dollar stores)
  - 🏠 Housing (apartments, short-term rentals, sublets)
  - 📚 Study Spaces (quiet cafes, libraries, coworking)
  - 🛍️ Shopping (thrift stores, discount retail, pharmacies)
  - 🎭 Entertainment (nightlife, live music, hiking, museums, parks)
  - 🏋️ Fitness (cheap gyms, yoga, running trails)
  - 🏥 Health (urgent care, pharmacies, mental health)
  - 💇 Services (laundromats, dry cleaning, print shops, hair)
  - 🚗 Transport (gas stations, bike shops, bus routes)
  - 🔧 Auto Repair (cheap mechanics, car wash, parts)
  - 🐾 Pet Services (vets, pet stores, dog parks)
  - 🏦 Banking (ATMs, banks, credit unions)
  - 📦 Shipping (post office, UPS, FedEx)

## Launch City
- **Portland, ME** (Maine) — 642 unique places across 14 categories

## Tech Stack
- **Backend:** Flask + Python 3.11
- **LLM:** `qwen-3.6-27b` via LiteLLM (hosted at `litellm.colby.edu:4000`)
- **Data:** SerpApi (Google Maps scraping) — 49 search queries → 642 deduplicated places
- **Frontend:** Pure HTML/CSS/JS (no framework, single-page chat UI)
- **Config:** `local` file (gitignored) for API keys
- **Browser:** Auto-opens Chrome on server start

## Repo
- **Local:** `/Users/davidjohnson/Desktop/cityguide-ai`
- **Remote:** `https://github.com/simonlartey/cityguide-ai.git`
- **Branch:** `main`

## Current Status
- [x] Data pipeline designed and built (`scripts/scrape.py`)
- [x] 49 SerpApi queries across 14 college-student categories
- [x] Re-scraped Portland, ME — 642 unique places
- [x] Chat server built (`server.py`) — keyword retrieval + LLM
- [x] Chat UI built (`templates/index.html`) — welcome screen + chat + suggestions
- [x] LLM wired up — `qwen-3.6-27b` via LiteLLM (Colby College)
- [x] Auto-open Chrome on server start
- [x] System prompt tuned for college students
- [ ] Test & refine with user feedback
- [ ] Deploy

## Design
- **Color:** Green accent (#16a34a) — fresh, local, trustworthy
- **Style:** Clean, card-based, minimal
- **Typography:** System font stack
- **Responsive:** Mobile-first
- **No external frontend dependencies**

## Decisions Log
| Date | Decision | Reason |
|------|----------|--------|
| 2025-07-07 | Green accent color | Fresh, local, trustworthy vibe |
| 2025-07-07 | Chat-first UX | Most natural way to ask for recommendations |
| 2025-07-07 | Single city focus | Deep coverage over broad coverage |
| 2025-07-07 | SerpApi for data | Structured Google Maps results (ratings, hours, reviews) |
| 2025-07-07 | qwen-3.6-27b via LiteLLM | Same model as Hermes — no external API dependency |
| 2026-07-08 | Pivoted to Portland, ME | Target college students relocating to new cities |
| 2026-07-08 | Expanded to 14 categories | Housing, study, auto, pets, finance, transport, fitness, shopping |
| 2026-07-08 | 49 SerpApi queries | Broader coverage for student services |
| 2026-07-08 | Keyword-based retrieval | Simple, reliable, no vector DB needed for ~640 places |
| 2026-07-08 | Auto-open Chrome on start | Seamless developer experience — just run `python server.py` |

## Notes
- Add new decisions, changes, and course corrections here as the project evolves.
