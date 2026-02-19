

"""
Reddit Collector (No API Key Version)
Collects locality-related posts using Reddit's public JSON endpoints.
No credentials required — works immediately.

When you get official Reddit API access later, swap this file with
collector_praw.py and everything else stays the same.
"""

import requests
import time
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (locality-rater research tool)'
}

DEFAULT_SUBREDDITS = [
    'india',
    'bangalore',
    'mumbai',
    'delhi',
    'pune',
    'hyderabad',
    'chennai',
    'kolkata',
    'indianrealestate',
    'personalfinanceindia',
    'realestate',
]

QUERY_TEMPLATES = [
    '{locality} {city}',
    '{locality} area',
    'living in {locality}',
    '{locality} review',
]


class RedditCollector:
    """Collects Reddit posts using public JSON endpoints. No API key needed."""

    def __init__(self, credentials=None):
        """credentials param kept for future PRAW compatibility but not used."""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search_subreddit(self, subreddit, query, limit=25):
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': query,
            'limit': limit,
            'sort': 'relevance',
            't': 'year',
            'restrict_sr': 1,
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 429:
                logger.warning("Rate limited — waiting 5 seconds...")
                time.sleep(5)
                response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"r/{subreddit} returned status {response.status_code}")
                return []

            posts = response.json().get('data', {}).get('children', [])
            results = []
            for post in posts:
                p = post.get('data', {})
                text = f"{p.get('title', '')}. {p.get('selftext', '')}".strip()
                results.append({
                    'id': p.get('id', ''),
                    'text': text,
                    'score': p.get('score', 0),
                    'created_utc': p.get('created_utc', 0),
                    'url': f"https://reddit.com{p.get('permalink', '')}",
                    'subreddit': subreddit,
                    'num_comments': p.get('num_comments', 0),
                })
            time.sleep(0.5)
            return results

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on r/{subreddit}")
            return []
        except Exception as e:
            logger.warning(f"Error on r/{subreddit}: {e}")
            return []

    def search_all(self, locality, city, subreddits=None):
        subreddits = subreddits or DEFAULT_SUBREDDITS
        all_posts = []
        seen_ids = set()

        for template in QUERY_TEMPLATES:
            query = template.format(locality=locality, city=city)
            for subreddit in subreddits:
                for post in self.search_subreddit(subreddit, query):
                    if post['id'] and post['id'] not in seen_ids:
                        seen_ids.add(post['id'])
                        all_posts.append(post)

        logger.info(f"Collected {len(all_posts)} raw posts for '{locality}, {city}'")
        return all_posts

    def filter_relevant_posts(self, posts, locality, min_text_length=20):
        locality_lower = locality.lower()
        filtered = [
            p for p in posts
            if locality_lower in p.get('text', '').lower()
            and len(p.get('text', '')) >= min_text_length
        ]
        logger.info(f"Filtered to {len(filtered)} relevant posts")
        return filtered

    def collect(self, locality, city, max_posts=100):
        raw = self.search_all(locality, city)
        relevant = self.filter_relevant_posts(raw, locality)
        relevant.sort(key=lambda p: p.get('score', 0), reverse=True)
        return relevant[:max_posts]


def collect_reddit_sentiment(locality, city, reddit_credentials=None, max_posts=100):
    """
    Convenience function — no credentials needed in this version.
    reddit_credentials param kept for future API compatibility.
    """
    collector = RedditCollector()
    return collector.collect(locality, city, max_posts=max_posts)