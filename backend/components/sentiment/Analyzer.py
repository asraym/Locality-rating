"""
Sentiment Analyzer
Core sentiment analysis logic using VADER ML model.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment of locality-related posts using VADER."""

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text.

        Args:
            text: Text to analyze

        Returns:
            Dict with compound, pos, neu, neg scores
        """
        if not text or not text.strip():
            return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}

        scores = self.vader.polarity_scores(text)
        return scores

    def analyze_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        Analyze sentiment for a list of posts.

        Args:
            posts: List of dicts with 'text', 'score', 'created_utc'

        Returns:
            Same posts with 'sentiment' key added
        """
        analyzed = []
        for post in posts:
            text = post.get('text', '')
            sentiment = self.analyze_text(text)
            analyzed.append({
                **post,
                'sentiment': sentiment
            })
        return analyzed

    def calculate_score(
        self,
        analyzed_posts: List[Dict],
        use_weighted: bool = True
    ) -> Tuple[float, Dict]:
        """
        Convert analyzed posts into a 0-100 sentiment score.

        Args:
            analyzed_posts: Posts with 'sentiment' key
            use_weighted: Whether to weight by upvotes

        Returns:
            (score 0-100, metrics dict)
        """
        if not analyzed_posts:
            return 50.0, {
                'avg_sentiment': 0.0,
                'weighted_sentiment': 0.0,
                'recent_sentiment': 0.0,
                'mention_count': 0,
                'trend': 'unknown'
            }

        compounds = [p['sentiment']['compound'] for p in analyzed_posts]
        upvotes = [max(p.get('score', 1), 1) for p in analyzed_posts]

        # Simple average sentiment
        avg_sentiment = sum(compounds) / len(compounds)

        # Upvote-weighted sentiment
        total_weight = sum(upvotes)
        weighted_sentiment = (
            sum(c * w for c, w in zip(compounds, upvotes)) / total_weight
        )

        # Recent sentiment (last 30% of posts by timestamp)
        sorted_posts = sorted(analyzed_posts, key=lambda p: p.get('created_utc', 0))
        recent_cutoff = max(1, int(len(sorted_posts) * 0.7))
        recent_posts = sorted_posts[recent_cutoff:]
        recent_sentiment = (
            sum(p['sentiment']['compound'] for p in recent_posts) / len(recent_posts)
            if recent_posts else avg_sentiment
        )

        # Determine trend (recent vs overall)
        if recent_sentiment > avg_sentiment + 0.05:
            trend = 'improving'
        elif recent_sentiment < avg_sentiment - 0.05:
            trend = 'declining'
        else:
            trend = 'stable'

        # Use weighted sentiment as primary signal
        primary = weighted_sentiment if use_weighted else avg_sentiment

        # Convert compound (-1 to 1) → score (0 to 100)
        # compound 1.0  → 95
        # compound 0.0  → 50
        # compound -1.0 → 5
        score = (primary + 1) / 2 * 90 + 5
        score = round(max(0.0, min(100.0, score)), 2)

        return score, {
            'avg_sentiment': round(avg_sentiment, 4),
            'weighted_sentiment': round(weighted_sentiment, 4),
            'recent_sentiment': round(recent_sentiment, 4),
            'mention_count': len(analyzed_posts),
            'trend': trend
        }

    def generate_insights(self, score: float, metrics: Dict) -> List[str]:
        """
        Generate human-readable insights from score and metrics.

        Args:
            score: 0-100 sentiment score
            metrics: Dict from calculate_score()

        Returns:
            List of insight strings
        """
        insights = []
        count = metrics.get('mention_count', 0)
        trend = metrics.get('trend', 'unknown')
        weighted = metrics.get('weighted_sentiment', 0)

        # Mention count
        if count >= 100:
            insights.append(f"High community engagement ({count} mentions found)")
        elif count >= 30:
            insights.append(f"Moderate community engagement ({count} mentions found)")
        elif count > 0:
            insights.append(f"Limited data available ({count} mentions found)")
        else:
            insights.append("No community mentions found — score defaulted to neutral")

        # Overall sentiment
        if score >= 75:
            insights.append("Residents express strongly positive feedback about this area")
        elif score >= 60:
            insights.append("Generally positive feedback from residents")
        elif score >= 45:
            insights.append("Mixed or neutral sentiment from the community")
        else:
            insights.append("Predominantly negative feedback — residents flag concerns")

        # Trend
        if trend == 'improving':
            insights.append("Sentiment has been improving recently")
        elif trend == 'declining':
            insights.append("Sentiment shows a declining trend recently")

        # Engagement quality (popular posts vs average)
        if metrics.get('weighted_sentiment', 0) > metrics.get('avg_sentiment', 0) + 0.1:
            insights.append("Most upvoted posts are more positive than average")
        elif metrics.get('weighted_sentiment', 0) < metrics.get('avg_sentiment', 0) - 0.1:
            insights.append("Most upvoted posts are more critical than average")

        return insights


def analyze_locality_sentiment(posts: List[Dict]) -> Tuple[float, List[str]]:
    """
    Main entry point — analyze pre-collected posts and return score + insights.

    Args:
        posts: List of dicts with 'text', 'score', 'created_utc'

    Returns:
        (score 0-100, insights list)
    """
    analyzer = SentimentAnalyzer()

    if not posts:
        logger.warning("No posts provided — returning neutral score")
        return 50.0, ["No community data available — defaulted to neutral score"]

    analyzed = analyzer.analyze_posts(posts)
    score, metrics = analyzer.calculate_score(analyzed)
    insights = analyzer.generate_insights(score, metrics)

    return score, insights