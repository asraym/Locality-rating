"""
Data Collection Guide & API Setup
For Locality Rating System
"""

# ============================================================================
# QUICK START GUIDE
# ============================================================================

"""
STEP 1: Install Required Libraries
-----------------------------------
pip install --break-system-packages pandas numpy requests beautifulsoup4 selenium
pip install --break-system-packages praw tweepy googlemaps vaderSentiment textblob
pip install --break-system-packages plotly matplotlib seaborn

STEP 2: Get API Keys
-------------------
1. Google Maps API: https://console.cloud.google.com/
   - Enable: Places API, Distance Matrix API, Geocoding API
   
2. Reddit API: https://www.reddit.com/prefs/apps
   - Create app, get client_id and client_secret
   
3. NewsAPI: https://newsapi.org/
   - Free tier: 100 requests/day
   
4. Twitter API (optional): https://developer.twitter.com/
   - Basic: Free, Academic: Better limits

STEP 3: Store API Keys Securely
-------------------------------
Create a file: config.json (add to .gitignore!)
"""

import os
import json

# Example config structure
config_template = {
    "google_maps_api_key": "YOUR_GOOGLE_MAPS_KEY",
    "reddit_client_id": "YOUR_REDDIT_CLIENT_ID",
    "reddit_client_secret": "YOUR_REDDIT_SECRET",
    "reddit_user_agent": "locality_rater/1.0",
    "news_api_key": "YOUR_NEWS_API_KEY",
    "twitter_bearer_token": "YOUR_TWITTER_TOKEN"  # Optional
}

# Save config template
with open('config_template.json', 'w') as f:
    json.dump(config_template, f, indent=2)

# ============================================================================
# DATA COLLECTION FUNCTIONS
# ============================================================================

import requests
from typing import Dict, List
import time

def load_config():
    """Load API keys from config file"""
    with open('config.json', 'r') as f:
        return json.load(f)

# ----------------------------------------------------------------------------
# 1. SENTIMENT ANALYSIS - Reddit Data
# ----------------------------------------------------------------------------

def collect_reddit_sentiment(locality_name: str, city: str, config: Dict) -> Dict:
    """
    Collect sentiment from Reddit posts/comments
    
    Returns:
        {
            'avg_sentiment': float,
            'mention_count': int,
            'recent_sentiment': float,
            'posts': List[Dict]
        }
    """
    try:
        import praw
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        
        # Initialize Reddit
        reddit = praw.Reddit(
            client_id=config['reddit_client_id'],
            client_secret=config['reddit_client_secret'],
            user_agent=config['reddit_user_agent']
        )
        
        # Initialize sentiment analyzer
        sia = SentimentIntensityAnalyzer()
        
        # Search queries
        queries = [
            f"{locality_name} {city}",
            f"living in {locality_name}",
            f"{locality_name} review"
        ]
        
        posts_data = []
        
        # Search relevant subreddits
        subreddits = ['india', 'bangalore', 'mumbai', 'delhi', 'pune']  # Add relevant city subs
        
        for query in queries:
            for sub in subreddits:
                try:
                    subreddit = reddit.subreddit(sub)
                    for post in subreddit.search(query, time_filter='year', limit=50):
                        text = f"{post.title} {post.selftext}"
                        sentiment = sia.polarity_scores(text)
                        
                        posts_data.append({
                            'text': text[:200],
                            'sentiment': sentiment['compound'],
                            'created_utc': post.created_utc,
                            'score': post.score,
                            'source': f"r/{sub}"
                        })
                        
                        # Also check comments
                        post.comments.replace_more(limit=5)
                        for comment in post.comments.list()[:10]:
                            sentiment = sia.polarity_scores(comment.body)
                            posts_data.append({
                                'text': comment.body[:200],
                                'sentiment': sentiment['compound'],
                                'created_utc': comment.created_utc,
                                'score': comment.score,
                                'source': f"r/{sub}"
                            })
                except Exception as e:
                    print(f"Error searching r/{sub}: {e}")
                    continue
                
                time.sleep(2)  # Rate limiting
        
        # Calculate metrics
        if posts_data:
            avg_sentiment = sum(p['sentiment'] for p in posts_data) / len(posts_data)
            
            # Recent sentiment (last 6 months)
            import datetime
            six_months_ago = datetime.datetime.now().timestamp() - (180 * 24 * 60 * 60)
            recent_posts = [p for p in posts_data if p['created_utc'] > six_months_ago]
            recent_sentiment = sum(p['sentiment'] for p in recent_posts) / len(recent_posts) if recent_posts else avg_sentiment
            
            return {
                'avg_sentiment': avg_sentiment,
                'mention_count': len(posts_data),
                'recent_sentiment': recent_sentiment,
                'posts': posts_data[:50]  # Top 50
            }
        else:
            return {
                'avg_sentiment': 0,
                'mention_count': 0,
                'recent_sentiment': 0,
                'posts': []
            }
            
    except Exception as e:
        print(f"Error collecting Reddit data: {e}")
        return {'avg_sentiment': 0, 'mention_count': 0, 'recent_sentiment': 0}


# ----------------------------------------------------------------------------
# 2. INFRASTRUCTURE - Google Maps Data
# ----------------------------------------------------------------------------

def collect_infrastructure_data(locality_name: str, city: str, config: Dict) -> Dict:
    """
    Collect infrastructure data using Google Maps API
    """
    try:
        import googlemaps
        
        gmaps = googlemaps.Client(key=config['google_maps_api_key'])
        
        # Geocode the locality
        geocode_result = gmaps.geocode(f"{locality_name}, {city}")
        if not geocode_result:
            return {}
        
        location = geocode_result[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        
        # Search for metro stations
        metro_results = gmaps.places_nearby(
            location=(lat, lng),
            keyword='metro station',
            radius=5000
        )
        
        metro_distance = None
        if metro_results.get('results'):
            # Calculate distance to nearest metro
            nearest_metro = metro_results['results'][0]
            metro_location = nearest_metro['geometry']['location']
            
            distance_result = gmaps.distance_matrix(
                origins=[(lat, lng)],
                destinations=[(metro_location['lat'], metro_location['lng'])],
                mode='walking'
            )
            
            if distance_result['rows'][0]['elements'][0]['status'] == 'OK':
                metro_distance = distance_result['rows'][0]['elements'][0]['distance']['value'] / 1000  # Convert to km
        
        # Search for hospitals
        hospitals = gmaps.places_nearby(
            location=(lat, lng),
            type='hospital',
            radius=5000
        )
        hospitals_count = len(hospitals.get('results', []))
        
        # Search for schools
        schools = gmaps.places_nearby(
            location=(lat, lng),
            type='school',
            radius=3000
        )
        schools_count = len(schools.get('results', []))
        
        # Search for shopping
        shopping = gmaps.places_nearby(
            location=(lat, lng),
            type='shopping_mall',
            radius=3000
        )
        shopping_density = 'high' if len(shopping.get('results', [])) > 3 else 'medium' if len(shopping.get('results', [])) > 1 else 'low'
        
        return {
            'metro_distance_km': metro_distance or 999,
            'hospitals_5km': hospitals_count,
            'schools_3km': schools_count,
            'connectivity': 'good',  # This needs manual input or traffic API
            'shopping_density': shopping_density,
            'coordinates': {'lat': lat, 'lng': lng}
        }
        
    except Exception as e:
        print(f"Error collecting infrastructure data: {e}")
        return {}


# ----------------------------------------------------------------------------
# 3. REAL ESTATE TRENDS - Web Scraping
# ----------------------------------------------------------------------------

def collect_real_estate_data(locality_name: str, city: str) -> Dict:
    """
    Collect real estate data (requires web scraping or manual input)
    
    NOTE: This is a template - actual implementation needs:
    - Web scraping from 99acres/MagicBricks
    - Or API integration if available
    - Or manual data entry
    """
    # PLACEHOLDER - Manual data entry for now
    return {
        'price_appreciation_yoy': 0,  # Manual input needed
        'rental_yield': 0,  # Manual input needed
        'inventory_turnover_days': 180,  # Manual input needed
        'price_vs_city_avg': 1.0,  # Manual input needed
        'avg_price_per_sqft': 0  # Manual input needed
    }


# ----------------------------------------------------------------------------
# 4. MAJOR PROJECTS - News Search
# ----------------------------------------------------------------------------

def collect_project_news(locality_name: str, city: str, config: Dict) -> Dict:
    """
    Search for major infrastructure projects using News API
    """
    try:
        from newsapi import NewsApiClient
        
        newsapi = NewsApiClient(api_key=config['news_api_key'])
        
        # Search queries
        queries = [
            f"{locality_name} {city} metro",
            f"{locality_name} {city} infrastructure",
            f"{locality_name} {city} development",
            f"{city} IT park {locality_name}"
        ]
        
        projects = {
            'metro': {'count': 0, 'timeline': '5_years'},
            'it_park': {'count': 0, 'timeline': '5_years'},
            'highway': {'count': 0, 'timeline': '5_years'},
            'smart_city': {'count': 0, 'timeline': '5_years'}
        }
        
        for query in queries:
            articles = newsapi.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=20
            )
            
            for article in articles.get('articles', []):
                title = article['title'].lower()
                description = (article.get('description') or '').lower()
                content = title + ' ' + description
                
                # Simple keyword matching
                if 'metro' in content:
                    projects['metro']['count'] += 1
                    if 'under construction' in content or 'construction' in content:
                        projects['metro']['timeline'] = 'construction'
                
                if 'it park' in content or 'tech park' in content or 'sez' in content:
                    projects['it_park']['count'] += 1
                
                if 'highway' in content or 'expressway' in content:
                    projects['highway']['count'] += 1
                
                if 'smart city' in content:
                    projects['smart_city']['count'] += 1
            
            time.sleep(1)  # Rate limiting
        
        return projects
        
    except Exception as e:
        print(f"Error collecting project news: {e}")
        return {}


# ----------------------------------------------------------------------------
# 5. AMENITIES - Google Places
# ----------------------------------------------------------------------------

def collect_amenities_data(locality_name: str, city: str, config: Dict) -> Dict:
    """
    Collect amenities data using Google Places API
    """
    try:
        import googlemaps
        
        gmaps = googlemaps.Client(key=config['google_maps_api_key'])
        
        # Geocode
        geocode_result = gmaps.geocode(f"{locality_name}, {city}")
        if not geocode_result:
            return {}
        
        location = geocode_result[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        
        # Count amenities
        amenities = {}
        
        # Restaurants
        restaurants = gmaps.places_nearby(
            location=(lat, lng),
            type='restaurant',
            radius=2000
        )
        amenities['restaurants_2km'] = len(restaurants.get('results', []))
        
        # Gyms
        gyms = gmaps.places_nearby(
            location=(lat, lng),
            keyword='gym fitness',
            radius=2000
        )
        amenities['gyms_2km'] = len(gyms.get('results', []))
        
        # Parks
        parks = gmaps.places_nearby(
            location=(lat, lng),
            type='park',
            radius=2000
        )
        amenities['parks_2km'] = len(parks.get('results', []))
        
        # Entertainment
        entertainment = gmaps.places_nearby(
            location=(lat, lng),
            keyword='cinema theater entertainment',
            radius=2000
        )
        amenities['entertainment_2km'] = len(entertainment.get('results', []))
        
        # Markets
        markets = gmaps.places_nearby(
            location=(lat, lng),
            type='supermarket',
            radius=2000
        )
        amenities['markets_2km'] = len(markets.get('results', []))
        
        return amenities
        
    except Exception as e:
        print(f"Error collecting amenities data: {e}")
        return {}


# ============================================================================
# MAIN DATA COLLECTION ORCHESTRATOR
# ============================================================================

def collect_all_data(locality_name: str, city: str, config: Dict) -> Dict:
    """
    Orchestrate all data collection
    """
    print(f"\n{'='*70}")
    print(f"Collecting data for: {locality_name}, {city}")
    print(f"{'='*70}\n")
    
    data = {}
    
    # 1. Sentiment
    print("1. Collecting sentiment data from Reddit...")
    data['sentiment'] = collect_reddit_sentiment(locality_name, city, config)
    print(f"   ✓ Found {data['sentiment']['mention_count']} mentions")
    
    # 2. Infrastructure
    print("\n2. Collecting infrastructure data from Google Maps...")
    data['infrastructure'] = collect_infrastructure_data(locality_name, city, config)
    print(f"   ✓ Found {data['infrastructure'].get('hospitals_5km', 0)} hospitals, "
          f"{data['infrastructure'].get('schools_3km', 0)} schools")
    
    # 3. Real Estate (manual for now)
    print("\n3. Real estate data (manual input needed)...")
    data['real_estate'] = collect_real_estate_data(locality_name, city)
    print("   ! Requires manual data entry")
    
    # 4. Developers (manual)
    print("\n4. Developer data (manual input needed)...")
    data['developers'] = {
        'reputed_developer_count': 0,
        'track_record': 'average',
        'on_time_delivery_rate': 70
    }
    print("   ! Requires manual data entry")
    
    # 5. Projects
    print("\n5. Collecting major projects from news...")
    data['projects'] = collect_project_news(locality_name, city, config)
    print(f"   ✓ Found infrastructure projects")
    
    # 6. Amenities
    print("\n6. Collecting amenities data from Google Places...")
    data['amenities'] = collect_amenities_data(locality_name, city, config)
    print(f"   ✓ Found {data['amenities'].get('restaurants_2km', 0)} restaurants, "
          f"{data['amenities'].get('parks_2km', 0)} parks")
    
    # 7. Crime (manual)
    print("\n7. Crime data (manual input needed)...")
    data['crime'] = {'comparison': 'average'}
    print("   ! Requires manual data entry")
    
    # Metadata
    from datetime import datetime
    data['meta'] = {
        'data_freshness_days': 0,
        'data_completeness': 0.7,  # Update based on what was collected
        'source_reliability': 0.8,
        'sentiment_sample_size': data['sentiment']['mention_count'],
        'collected_at': datetime.now().isoformat()
    }
    
    print(f"\n{'='*70}")
    print("Data collection complete!")
    print(f"{'='*70}\n")
    
    return data


# ============================================================================
# MANUAL DATA ENTRY TEMPLATE
# ============================================================================

manual_data_template = {
    "real_estate": {
        "price_appreciation_yoy": 0,  # % - Check 99acres trends
        "rental_yield": 0,  # % - Check rental listings
        "inventory_turnover_days": 180,  # Days - Check property portals
        "price_vs_city_avg": 1.0  # Ratio - Compare with city average
    },
    "developers": {
        "reputed_developer_count": 0,  # Count - Check RERA website
        "track_record": "average",  # excellent/good/average/poor
        "on_time_delivery_rate": 70  # % - From RERA data
    },
    "crime": {
        "comparison": "average"  # much_below/below/average/above/much_above
    }
}

# Save manual template
with open('manual_data_template.json', 'w') as f:
    json.dump(manual_data_template, f, indent=2)

print("\n" + "="*70)
print("SETUP COMPLETE!")
print("="*70)
print("\nNext Steps:")
print("1. Copy config_template.json to config.json")
print("2. Add your API keys to config.json")
print("3. Run: python data_collector.py")
print("4. Fill in manual data using manual_data_template.json")
print("5. Run: python locality_rating_system.py")
print("\n" + "="*70)
