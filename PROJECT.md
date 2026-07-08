# CityGuide AI — Project Brief

## Vision
An AI-powered chatbot that helps people discover the best local places in specific cities — restaurants, grocery stores, services, entertainment, and more. Users ask naturally in plain English and get tailored, personalized recommendations.

## Core Product
- **Chat-first interface** — users type questions like "Where's the best brunch near the North End?" or "I need a 24-hour pharmacy."
- **City-limited** — launches city by city with curated, accurate data per location.
- **No signup required** to start chatting.
- **Categories covered:**
  - 🍽️ Restaurants (best eats, hidden gems, date spots)
  - 🛒 Groceries (fresh markets, specialty, organic stores)
  - 💇 Services (salons, repair shops, fitness, wellness)
  - 🎭 Entertainment (nightlife, events, museums, parks)
  - 🏥 Health (pharmacies, clinics, urgent care)
  - 📦 Shipping (post offices, lockers, pickup points)

## Launch City
- Portland

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
- [ ] Install SerpApi & run initial scrape
- [ ] Decide tech stack
- [ ] Build chat interface
- [ ] Set up AI backend
- [ ] Add local context enrichment
- [ ] Deploy

## Decisions Log
| Date | Decision | Reason |
|------|----------|--------|
| 2025-07-07 | Green accent color | Fresh, local, trustworthy vibe |
| 2025-07-07 | Chat-first UX | Most natural way to ask for recommendations |
| 2025-07-07 | Single city: Portland | Deep coverage over broad coverage |
| 2025-07-07 | SerpApi for data scraping | Structured Google Maps results with ratings, hours, reviews in one shot |

## Notes
- Add new decisions, changes, and course corrections here as the project evolves.
