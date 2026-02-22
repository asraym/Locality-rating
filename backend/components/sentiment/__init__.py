"""
Sentiment Component
===================
Collects Reddit posts about a locality and scores community sentiment
using VADER — a lightweight ML model tuned for social media text.

Main entry point: get_sentiment_score()

Files:
    analyzer.py   — VADER analysis logic (SentimentAnalyzer)
    collector.py  — Reddit API data collection (RedditCollector)
"""

from .Analyzer import SentimentAnalyzer, analyze_locality_sentiment
from .Collector import RedditCollector, collect_reddit_sentiment
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def get_sentiment_score(
    locality: str,
    city: str,
    config: Dict,
) -> Tuple[float, List[str]]:
    """
    Main function — collect Reddit data + return sentiment score and insights.

    Args:
        locality: Locality name (e.g. "Koramangala")
        city: City name (e.g. "Bangalore")
        config: Dict with Reddit credentials:
                {
                    "client_id": "...",
                    "client_secret": "...",
                    "user_agent": "locality_rater/1.0"   # optional
                }

    Returns:
        Tuple of:
            score (float): Sentiment score 0–100
            insights (list[str]): Human-readable findings
    """
    # Step 1: Collect posts from Reddit
    try:
        posts = collect_reddit_sentiment(
            locality=locality,
            city=city,
            reddit_credentials=config,
        )
    except Exception as e:
        logger.error(f"Reddit collection failed: {e}")
        return 50.0, [f"Could not collect Reddit data: {e}"]

    # Step 2: Analyze sentiment and return score + insights
    score, insights = analyze_locality_sentiment(posts)
    return score, insights


def get_detailed_sentiment(
    locality: str,
    city: str,
    config: Dict,
) -> Dict:
    """
    Extended analysis — returns full metrics alongside score and insights.

    Args:
        locality: Locality name
        city: City name
        config: Reddit credentials dict

    Returns:
        Dict with:
            score (float): 0–100
            avg_sentiment (float): Raw VADER average (-1 to 1)
            weighted_sentiment (float): Upvote-weighted sentiment
            recent_sentiment (float): Sentiment of recent posts
            mention_count (int): Number of posts analyzed
            trend (str): 'improving' | 'stable' | 'declining' | 'unknown'
            insights (list[str]): Human-readable findings
    """
    try:
        posts = collect_reddit_sentiment(
            locality=locality,
            city=city,
            reddit_credentials=config,
        )
    except Exception as e:
        logger.error(f"Reddit collection failed: {e}")
        return {
            'score': 50.0,
            'avg_sentiment': 0.0,
            'weighted_sentiment': 0.0,
            'recent_sentiment': 0.0,
            'mention_count': 0,
            'trend': 'unknown',
            'insights': [f"Could not collect Reddit data: {e}"],
        }

    analyzer = SentimentAnalyzer()

    if not posts:
        return {
            'score': 50.0,
            'avg_sentiment': 0.0,
            'weighted_sentiment': 0.0,
            'recent_sentiment': 0.0,
            'mention_count': 0,
            'trend': 'unknown',
            'insights': ["No community data found — defaulted to neutral score"],
        }

    analyzed = analyzer.analyze_posts(posts)
    score, metrics = analyzer.calculate_score(analyzed)
    insights = analyzer.generate_insights(score, metrics)

    return {
        'score': score,
        **metrics,
        'insights': insights,
    }


def get_sentiment_from_posts(posts: List[Dict]) -> Tuple[float, List[str]]:
    """
    Analyze pre-collected posts (skip Reddit collection step).

    Useful for testing or when you already have posts from another source.

    Args:
        posts: List of dicts, each with:
               - text (str): Post content
               - score (int): Upvotes/likes
               - created_utc (float): Unix timestamp

    Returns:
        (score 0-100, insights list)
    """
    return analyze_locality_sentiment(posts)


__all__ = [
    'get_sentiment_score',
    'get_detailed_sentiment',
    'get_sentiment_from_posts',
]