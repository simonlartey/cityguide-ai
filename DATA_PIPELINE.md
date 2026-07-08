# Data Pipeline — CityGuide AI

## Source
**SerpApi** — Scrapes Google Maps & local search results.
- Docs: https://serpapi.com/
- Dashboard: https://serpapi.com/dashboard
- Python lib: `serpapi`

## Setup
1. Get an API key at https://serpapi.com/dashboard (free tier = 100 searches/month)
2. Install: `pip install serpapi`
3. Set env var: `export SERPAPI_API_KEY="your_key_here"`

## Search Strategy
For each category, we run targeted Google searches to pull the best Portland results:

| Category | Search Query | Expected Results |
|----------|--------------|-----------------|
| 🍽️ Restaurants | "best restaurants in Portland OR" | 20-30 places |
| 🛒 Groceries | "best grocery stores in Portland OR" | 10-15 places |
| 💇 Services | "best services in Portland OR" | 15-20 places |
| 🎭 Entertainment | "best entertainment in Portland OR" | 15-20 places |
| 🏥 Health | "best pharmacies clinics in Portland OR" | 10-15 places |
| 📦 Shipping | "shipping services in Portland OR" | 5-10 places |

## Output
- Raw JSON per search → `data/raw/`
- Cleaned, unified places → `data/places.json`
- Enriched with local context → `data/context.json`

## What We Extract Per Place
```json
{
  "title": "Bluehour Cafe",
  "rating": 4.5,
  "reviews": 1200,
  "address": "1015 NW Lovejoy St, Portland, OR 97209",
  "category": "restaurant",
  "phone": "(503) 274-1211",
  "hours": "Open ⋅ Closes 3PM",
  "price": "$$",
  "gps": {"lat": 45.5300, "lng": -122.6820},
  "thumbnail": "https://...",
  "context": "Portland institution. Famous for heart-shaped pancakes."
}
```

## Pipeline Stages
1. **Scrape** — `scripts/scrape.py` runs all SerpApi searches, saves raw JSON
2. **Parse** — `scripts/parse.py` extracts structured fields from raw results
3. **Deduplicate** — merge duplicates, keep highest-rated version
4. **Enrich** — `scripts/enrich.py` adds local context (manual or LLM-assisted)
5. **Export** — unified `data/places.json` ready for the chatbot
