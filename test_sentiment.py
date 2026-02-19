"""
Quick test script for the Sentiment Component.
Run this from your project root:

    python test_sentiment.py

Make sure your config.json has Reddit credentials before running.
"""

import json
import sys
import os

# Add backend to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from components.sentiment import get_sentiment_score, get_detailed_sentiment


def load_config():
    """Load API credentials from config.json"""
    try:
        with open('config.json') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        print("   Create config.json at your project root with your Reddit credentials.")
        print("   See config.example.json for the format.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ config.json has invalid JSON. Check for typos.")
        sys.exit(1)


def main():
    # Load config
    config = load_config()
    reddit_config = config.get('reddit')

    if not reddit_config or not reddit_config.get('client_id'):
        print("❌ Reddit credentials missing in config.json")
        print("   Make sure you have client_id and client_secret filled in.")
        sys.exit(1)

    print("\n🏙️  LOCALITY SENTIMENT TESTER")
    print("=" * 40)

    # Ask for locality and city
    locality = input("Enter locality name (e.g. Koramangala): ").strip()
    city = input("Enter city name (e.g. Bangalore): ").strip()

    if not locality or not city:
        print("❌ Locality and city cannot be empty.")
        sys.exit(1)

    print(f"\n🔍 Searching Reddit for '{locality}, {city}'...")
    print("   This may take 1-2 minutes...\n")

    # Run the sentiment analysis
    try:
        result = get_detailed_sentiment(
            locality=locality,
            city=city,
            config=reddit_config,
        )
    except Exception as e:
        print(f"❌ Something went wrong: {e}")
        sys.exit(1)

    # Print results
    print("=" * 40)
    print(f"📍 {locality}, {city}")
    print("=" * 40)
    print(f"⭐ Sentiment Score   : {result['score']} / 100")
    print(f"📊 Mentions Found    : {result['mention_count']}")
    print(f"📈 Trend             : {result['trend'].capitalize()}")
    print(f"🧠 Avg Sentiment     : {result['avg_sentiment']}  (-1 to 1 scale)")
    print(f"👍 Weighted Sentiment: {result['weighted_sentiment']}  (upvote-weighted)")
    print(f"🕐 Recent Sentiment  : {result['recent_sentiment']}  (latest posts)")
    print("\n💬 Insights:")
    for i, insight in enumerate(result['insights'], 1):
        print(f"   {i}. {insight}")
    print("=" * 40)

    # Simple recommendation
    score = result['score']
    if score >= 75:
        verdict = "✅ Strong positive community sentiment"
    elif score >= 60:
        verdict = "🟡 Generally positive sentiment"
    elif score >= 45:
        verdict = "⚠️  Mixed or neutral sentiment"
    else:
        verdict = "🔴 Negative community sentiment — dig deeper"

    print(f"\n{verdict}")
    print()

    # Option to test another locality
    again = input("Test another locality? (y/n): ").strip().lower()
    if again == 'y':
        main()


if __name__ == '__main__':
    main()