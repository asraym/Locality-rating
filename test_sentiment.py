"""
Quick test script for the Sentiment Component.
No API key needed — uses Reddit's public JSON endpoints.

Run from your project root:
    python test_sentiment.py
"""

import sys
import os

# Add backend to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.components.sentiment import get_sentiment_score, get_detailed_sentiment


def main():
    print("\n🏙️  LOCALITY SENTIMENT TESTER")
    print("=" * 40)

    locality = input("Enter locality name (e.g. Koramangala): ").strip()
    city     = input("Enter city name     (e.g. Bangalore):  ").strip()

    if not locality or not city:
        print("❌ Locality and city cannot be empty.")
        sys.exit(1)

    print(f"\n🔍 Searching Reddit for '{locality}, {city}'...")
    print("   (No API key needed — using public JSON)")
    print("   This may take 1-2 minutes...\n")

    try:
        # config={} because no credentials needed in JSON mode
        result = get_detailed_sentiment(
            locality=locality,
            city=city,
            config={},
        )
    except Exception as e:
        print(f"❌ Something went wrong: {e}")
        sys.exit(1)

    # Print results
    print("=" * 40)
    print(f"📍 {locality}, {city}")
    print("=" * 40)
    print(f"⭐ Sentiment Score    : {result['score']} / 100")
    print(f"📊 Mentions Found     : {result['mention_count']}")
    print(f"📈 Trend              : {result['trend'].capitalize()}")
    print(f"🧠 Avg Sentiment      : {result['avg_sentiment']}  (-1 to 1)")
    print(f"👍 Weighted Sentiment : {result['weighted_sentiment']}  (upvote-weighted)")
    print(f"🕐 Recent Sentiment   : {result['recent_sentiment']}  (latest posts)")
    print("\n💬 Insights:")
    for i, insight in enumerate(result['insights'], 1):
        print(f"   {i}. {insight}")
    print("=" * 40)

    score = result['score']
    if score >= 75:
        print("\n✅ Strong positive community sentiment")
    elif score >= 60:
        print("\n🟡 Generally positive sentiment")
    elif score >= 45:
        print("\n⚠️  Mixed or neutral sentiment")
    else:
        print("\n🔴 Negative community sentiment — dig deeper")

    print()
    again = input("Test another locality? (y/n): ").strip().lower()
    if again == 'y':
        main()


if __name__ == '__main__':
    main()
