"""
Locality Rating System - Starter Implementation
A Python-based system to evaluate localities for real estate investment
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

# Weights for each component (must sum to 1.0)
WEIGHTS = {
    'sentiment': 0.20,
    'infrastructure': 0.25,
    'real_estate': 0.20,
    'developers': 0.15,
    'projects': 0.10,
    'amenities': 0.08,
    'crime': 0.02
}

# Scoring thresholds
RECOMMENDATION_THRESHOLDS = {
    'buy': {'score': 75, 'confidence': 70},
    'hold': {'score': 60, 'confidence': 60},
    'avoid': {'score': 0, 'confidence': 0}
}

# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def calculate_sentiment_score(sentiment_data: Dict) -> Tuple[float, List[str]]:
    """
    Calculate sentiment score from user comments/posts
    
    Args:
        sentiment_data: {
            'avg_sentiment': -1 to +1,
            'mention_count': int,
            'recent_sentiment': -1 to +1 (last 6 months)
        }
    
    Returns:
        (score, insights)
    """
    insights = []
    
    # Normalize sentiment to 0-100
    base_score = ((sentiment_data.get('avg_sentiment', 0) + 1) / 2) * 100
    
    # Volume boost
    mention_count = sentiment_data.get('mention_count', 0)
    if mention_count > 500:
        base_score = min(100, base_score + 10)
        insights.append(f"High user engagement ({mention_count} mentions)")
    elif mention_count > 100:
        base_score = min(100, base_score + 5)
        insights.append(f"Good user engagement ({mention_count} mentions)")
    
    # Recency adjustment (weight recent sentiment 2x)
    recent = sentiment_data.get('recent_sentiment', sentiment_data.get('avg_sentiment', 0))
    weighted_sentiment = (sentiment_data.get('avg_sentiment', 0) + 2 * recent) / 3
    final_score = ((weighted_sentiment + 1) / 2) * 100
    
    if sentiment_data.get('recent_sentiment', 0) > sentiment_data.get('avg_sentiment', 0):
        insights.append("Improving sentiment trend")
    
    return round(final_score, 2), insights


def calculate_infrastructure_score(infra_data: Dict) -> Tuple[float, List[str]]:
    """
    Calculate infrastructure score
    
    Args:
        infra_data: {
            'metro_distance_km': float,
            'hospitals_5km': int,
            'schools_3km': int,
            'connectivity': 'excellent'|'good'|'average'|'poor',
            'shopping_density': 'high'|'medium'|'low'
        }
    """
    score = 0
    insights = []
    
    # Metro proximity (25 pts max)
    metro_dist = infra_data.get('metro_distance_km', 999)
    if metro_dist < 1:
        score += 25
        insights.append(f"Excellent metro connectivity ({metro_dist:.1f}km)")
    elif metro_dist < 3:
        score += 15
        insights.append(f"Good metro connectivity ({metro_dist:.1f}km)")
    elif metro_dist < 5:
        score += 5
    
    # Hospitals (15 pts max)
    hospitals = infra_data.get('hospitals_5km', 0)
    if hospitals >= 3:
        score += 15
        insights.append(f"Multiple hospitals nearby ({hospitals})")
    elif hospitals == 2:
        score += 10
    elif hospitals == 1:
        score += 5
    
    # Schools (15 pts max)
    schools = infra_data.get('schools_3km', 0)
    if schools >= 5:
        score += 15
        insights.append(f"Good educational infrastructure ({schools} schools)")
    elif schools >= 3:
        score += 10
    elif schools >= 1:
        score += 5
    
    # Connectivity (25 pts max)
    connectivity_scores = {
        'excellent': 25,
        'good': 15,
        'average': 10,
        'poor': 0
    }
    conn = infra_data.get('connectivity', 'average').lower()
    score += connectivity_scores.get(conn, 10)
    if conn == 'excellent':
        insights.append("Excellent road connectivity")
    
    # Shopping density (20 pts max)
    shopping_scores = {
        'high': 20,
        'medium': 10,
        'low': 5
    }
    shopping = infra_data.get('shopping_density', 'medium').lower()
    score += shopping_scores.get(shopping, 10)
    
    return round(score, 2), insights


def calculate_real_estate_score(re_data: Dict) -> Tuple[float, List[str]]:
    """
    Calculate real estate trends score
    
    Args:
        re_data: {
            'price_appreciation_yoy': float (%),
            'rental_yield': float (%),
            'inventory_turnover_days': int,
            'price_vs_city_avg': float (ratio)
        }
    """
    score = 0
    insights = []
    risks = []
    
    # Price appreciation (30 pts max)
    appreciation = re_data.get('price_appreciation_yoy', 0)
    if appreciation > 15:
        score += 30
        insights.append(f"Strong price appreciation ({appreciation:.1f}% YoY)")
    elif appreciation > 10:
        score += 25
        insights.append(f"Good price appreciation ({appreciation:.1f}% YoY)")
    elif appreciation > 5:
        score += 20
    elif appreciation > 0:
        score += 10
    else:
        risks.append(f"Negative price growth ({appreciation:.1f}% YoY)")
    
    # Rental yield (25 pts max)
    rental_yield = re_data.get('rental_yield', 0)
    if rental_yield > 4:
        score += 25
        insights.append(f"Excellent rental yield ({rental_yield:.1f}%)")
    elif rental_yield > 3:
        score += 20
    elif rental_yield > 2:
        score += 15
    else:
        score += 10
    
    # Inventory turnover (20 pts max)
    turnover = re_data.get('inventory_turnover_days', 365)
    if turnover < 90:
        score += 20
        insights.append("High demand (quick inventory turnover)")
    elif turnover < 180:
        score += 15
    elif turnover < 365:
        score += 10
    else:
        score += 5
        risks.append("Slow inventory movement")
    
    # Price competitiveness (25 pts max)
    price_ratio = re_data.get('price_vs_city_avg', 1.0)
    if price_ratio < 0.9:
        score += 25
        insights.append("Below city average pricing")
    elif price_ratio < 1.1:
        score += 15
    else:
        score += 5
        risks.append("Above city average pricing")
    
    return round(score, 2), insights, risks


def calculate_developer_score(dev_data: Dict) -> Tuple[float, List[str]]:
    """
    Calculate developer presence score
    
    Args:
        dev_data: {
            'reputed_developer_count': int,
            'track_record': 'excellent'|'good'|'average'|'poor',
            'on_time_delivery_rate': float (%)
        }
    """
    score = 0
    insights = []
    
    # Number of reputed developers (40 pts max)
    dev_count = dev_data.get('reputed_developer_count', 0)
    if dev_count >= 3:
        score += 40
        insights.append(f"Strong developer presence ({dev_count} reputed brands)")
    elif dev_count == 2:
        score += 25
    elif dev_count == 1:
        score += 15
    
    # Track record (30 pts max)
    track_record_scores = {
        'excellent': 30,
        'good': 20,
        'average': 10,
        'poor': 0
    }
    track = dev_data.get('track_record', 'average').lower()
    score += track_record_scores.get(track, 10)
    
    # On-time delivery (30 pts max)
    delivery_rate = dev_data.get('on_time_delivery_rate', 0)
    if delivery_rate > 80:
        score += 30
        insights.append(f"Reliable delivery track record ({delivery_rate:.0f}%)")
    elif delivery_rate > 60:
        score += 20
    else:
        score += 10
    
    return round(score, 2), insights


def calculate_projects_score(projects_data: Dict) -> Tuple[float, List[str]]:
    """
    Calculate major projects score
    
    Args:
        projects_data: {
            'metro': {'count': int, 'timeline': 'construction'|'2_years'|'5_years'|'beyond'},
            'it_park': {...},
            'highway': {...},
            'smart_city': {...}
        }
    """
    score = 0
    insights = []
    
    # Project values
    project_values = {
        'metro': 40,
        'airport': 40,
        'it_park': 30,
        'sez': 30,
        'highway': 25,
        'smart_city': 20
    }
    
    # Timeline multipliers
    timeline_multipliers = {
        'construction': 1.5,
        'under_construction': 1.5,
        '2_years': 1.2,
        'within_2_years': 1.2,
        '5_years': 1.0,
        '2_5_years': 1.0,
        'beyond': 0.7,
        'beyond_5_years': 0.7
    }
    
    for project_type, value in project_values.items():
        if project_type in projects_data:
            project = projects_data[project_type]
            count = project.get('count', 0)
            timeline = project.get('timeline', '5_years').lower()
            
            if count > 0:
                multiplier = timeline_multipliers.get(timeline, 1.0)
                project_score = min(value, value * count * 0.7) * multiplier
                score += project_score
                
                insights.append(f"{project_type.replace('_', ' ').title()} planned ({timeline.replace('_', ' ')})")
    
    # Cap at 100
    score = min(100, score)
    
    return round(score, 2), insights


def calculate_amenities_score(amenities_data: Dict) -> Tuple[float, List[str]]:
    """
    Calculate amenities score
    
    Args:
        amenities_data: {
            'restaurants_2km': int,
            'gyms_2km': int,
            'parks_2km': int,
            'entertainment_2km': int,
            'markets_2km': int
        }
    """
    score = 0
    insights = []
    
    categories = {
        'restaurants_2km': ('Restaurants', 20, 5),
        'gyms_2km': ('Fitness facilities', 20, 3),
        'parks_2km': ('Parks/recreation', 20, 2),
        'entertainment_2km': ('Entertainment', 20, 2),
        'markets_2km': ('Markets/groceries', 20, 3)
    }
    
    for key, (name, max_points, divisor) in categories.items():
        count = amenities_data.get(key, 0)
        points = min(max_points, count / divisor)
        score += points
        
        if count >= divisor * 3:
            insights.append(f"Good {name.lower()} availability")
    
    return round(score, 2), insights


def calculate_crime_score(crime_data: Dict) -> Tuple[float, List[str]]:
    """
    Calculate crime score
    
    Args:
        crime_data: {
            'comparison': 'much_below'|'below'|'average'|'above'|'much_above'
        }
    """
    score_map = {
        'much_below': 100,
        'below_average': 75,
        'below': 75,
        'average': 50,
        'above_average': 25,
        'above': 25,
        'much_above': 0
    }
    
    comparison = crime_data.get('comparison', 'average').lower()
    score = score_map.get(comparison, 50)
    
    insights = []
    if score >= 75:
        insights.append("Low crime rate")
    elif score <= 25:
        insights.append("Higher than average crime rate")
    
    return round(score, 2), insights


# ============================================================================
# CONFIDENCE CALCULATION
# ============================================================================

def calculate_confidence(data_meta: Dict) -> float:
    """
    Calculate confidence level based on data quality
    
    Args:
        data_meta: {
            'data_freshness_days': int,
            'data_completeness': float (0-1),
            'source_reliability': float (0-1),
            'sentiment_sample_size': int
        }
    """
    # Data freshness (0-30 pts)
    freshness_days = data_meta.get('data_freshness_days', 365)
    if freshness_days <= 30:
        freshness_score = 30
    elif freshness_days <= 90:
        freshness_score = 20
    else:
        freshness_score = 10
    
    # Data completeness (0-30 pts)
    completeness = data_meta.get('data_completeness', 0.5)
    completeness_score = completeness * 30
    
    # Source reliability (0-20 pts)
    reliability = data_meta.get('source_reliability', 0.7)
    reliability_score = reliability * 20
    
    # Sample size (0-20 pts)
    sample_size = data_meta.get('sentiment_sample_size', 0)
    if sample_size >= 100:
        sample_score = 20
    elif sample_size >= 50:
        sample_score = 15
    elif sample_size >= 20:
        sample_score = 10
    else:
        sample_score = 5
    
    confidence = freshness_score + completeness_score + reliability_score + sample_score
    
    return round(confidence, 2)


# ============================================================================
# MAIN RATING FUNCTION
# ============================================================================

def rate_locality(locality_name: str, data: Dict) -> Dict:
    """
    Main function to rate a locality
    
    Args:
        locality_name: Name of the locality
        data: All collected data for the locality
    
    Returns:
        Complete rating report
    """
    # Calculate component scores
    sentiment_score, sentiment_insights = calculate_sentiment_score(
        data.get('sentiment', {})
    )
    
    infra_score, infra_insights = calculate_infrastructure_score(
        data.get('infrastructure', {})
    )
    
    re_score, re_insights, re_risks = calculate_real_estate_score(
        data.get('real_estate', {})
    )
    
    dev_score, dev_insights = calculate_developer_score(
        data.get('developers', {})
    )
    
    projects_score, projects_insights = calculate_projects_score(
        data.get('projects', {})
    )
    
    amenities_score, amenities_insights = calculate_amenities_score(
        data.get('amenities', {})
    )
    
    crime_score, crime_insights = calculate_crime_score(
        data.get('crime', {})
    )
    
    # Store component scores
    component_scores = {
        'sentiment': sentiment_score,
        'infrastructure': infra_score,
        'real_estate': re_score,
        'developers': dev_score,
        'projects': projects_score,
        'amenities': amenities_score,
        'crime': crime_score
    }
    
    # Calculate weighted final score
    final_score = sum(
        component_scores[key] * WEIGHTS[key] 
        for key in WEIGHTS.keys()
    )
    
    # Calculate confidence
    confidence = calculate_confidence(data.get('meta', {}))
    
    # Determine recommendation
    if final_score >= 75 and confidence >= 70:
        recommendation = "BUY"
        reasoning = "Strong fundamentals and positive trends"
    elif final_score >= 60 and confidence >= 60:
        recommendation = "HOLD"
        reasoning = "Decent potential but monitor trends"
    else:
        recommendation = "AVOID"
        reasoning = "Weak fundamentals or insufficient data"
    
    # Apply safety rules
    if crime_score < 30 and WEIGHTS.get('crime', 0) > 0:
        if recommendation == "BUY":
            recommendation = "HOLD"
            reasoning += " (downgraded due to crime concerns)"
    
    if re_score < 20:
        if recommendation == "BUY":
            recommendation = "HOLD"
            reasoning += " (downgraded due to negative real estate trends)"
    
    # Compile all insights
    all_insights = (
        sentiment_insights + infra_insights + re_insights + 
        dev_insights + projects_insights + amenities_insights + crime_insights
    )
    
    # Compile report
    report = {
        'locality': locality_name,
        'final_score': round(final_score, 2),
        'confidence': confidence,
        'confidence_level': 'High' if confidence >= 80 else 'Medium' if confidence >= 60 else 'Low',
        'recommendation': recommendation,
        'reasoning': reasoning,
        'component_scores': component_scores,
        'key_insights': all_insights[:10],  # Top 10 insights
        'risks': re_risks if re_risks else [],
        'weights_used': WEIGHTS,
        'timestamp': datetime.now().isoformat(),
    }
    
    return report


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example data for Whitefield, Bangalore
    example_data = {
        'sentiment': {
            'avg_sentiment': 0.35,
            'mention_count': 245,
            'recent_sentiment': 0.45
        },
        'infrastructure': {
            'metro_distance_km': 2.5,
            'hospitals_5km': 4,
            'schools_3km': 8,
            'connectivity': 'good',
            'shopping_density': 'high'
        },
        'real_estate': {
            'price_appreciation_yoy': 12.5,
            'rental_yield': 3.2,
            'inventory_turnover_days': 120,
            'price_vs_city_avg': 1.15
        },
        'developers': {
            'reputed_developer_count': 4,
            'track_record': 'good',
            'on_time_delivery_rate': 75
        },
        'projects': {
            'metro': {'count': 1, 'timeline': 'construction'},
            'it_park': {'count': 2, 'timeline': '2_years'}
        },
        'amenities': {
            'restaurants_2km': 45,
            'gyms_2km': 8,
            'parks_2km': 6,
            'entertainment_2km': 5,
            'markets_2km': 12
        },
        'crime': {
            'comparison': 'below_average'
        },
        'meta': {
            'data_freshness_days': 15,
            'data_completeness': 0.85,
            'source_reliability': 0.9,
            'sentiment_sample_size': 245
        }
    }
    
    # Rate the locality
    report = rate_locality("Whitefield, Bangalore", example_data)
    
    # Print the report
    print("\n" + "="*70)
    print(f"LOCALITY RATING REPORT: {report['locality']}")
    print("="*70)
    print(f"\nFinal Score: {report['final_score']}/100")
    print(f"Confidence: {report['confidence']}% ({report['confidence_level']})")
    print(f"\nRECOMMENDATION: {report['recommendation']}")
    print(f"Reasoning: {report['reasoning']}")
    
    print(f"\n{'Component Scores:':<30}")
    print("-" * 50)
    for component, score in report['component_scores'].items():
        weight = WEIGHTS[component]
        print(f"{component.title():<25} {score:>6.1f}/100  (weight: {weight:.0%})")
    
    print(f"\n{'Key Insights:':<30}")
    print("-" * 50)
    for i, insight in enumerate(report['key_insights'], 1):
        print(f"{i}. {insight}")
    
    if report['risks']:
        print(f"\n{'Risks/Concerns:':<30}")
        print("-" * 50)
        for i, risk in enumerate(report['risks'], 1):
            print(f"{i}. {risk}")
    
    print("\n" + "="*70)
    
    # Save to JSON
    with open('example_rating_output.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\nReport saved to: example_rating_output.json")
