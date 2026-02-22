# Locality Rating Platform

A tool that rates residential localities in Indian cities to help people make informed real estate decisions.

Given a locality and city, it analyses multiple factors and returns a score out of 100 along with a buy/hold/avoid recommendation.

## How it works

The platform combines 7 components to calculate a final weighted score:

- **Sentiment** — Reddit mentions and community feedback
- **Infrastructure** — Proximity to metro, hospitals, schools, and other essentials
- **Real Estate** — Property prices, trends, and rental yields
- **Developers** — Reputation and RERA compliance of builders in the area
- **Projects** — Upcoming infrastructure and development news
- **Amenities** — Restaurants, gyms, parks, and day-to-day conveniences
- **Crime** — Safety data

## Structure

```
backend/       # All scoring logic and components
frontend/      # React web interface
docs/          # Architecture and deployment notes
```

## Setup

1. Clone the repo
2. Add API keys to `config.json` (see `config.example.json`)
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python scripts/analyze_locality.py`

## Config

API keys required:
- Reddit API (sentiment)
- Google Maps API (infrastructure, amenities)
- News API (projects)!
