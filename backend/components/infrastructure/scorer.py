"""
Infrastructure Scorer
Orchestrates data collection and scoring for all infrastructure types.
"""

import logging
from typing import Dict, List, Optional, Tuple

from .google_maps import GoogleMapsAPI
from .calculator import ProximityCalculator, INFRASTRUCTURE_TYPES

logger = logging.getLogger(__name__)


class InfrastructureScorer:
    """
    Scores a locality's infrastructure by:
    1. Finding the locality coordinates via geocoding
    2. Searching for each infrastructure type nearby
    3. Scoring based on distance + count
    4. Combining into a weighted final score
    """

    def __init__(self, maps_api: GoogleMapsAPI):
        self.maps = maps_api
        self.calculator = ProximityCalculator()

    def collect_infrastructure_data(
        self,
        lat: float,
        lng: float
    ) -> Dict[str, Dict]:
        """
        Collect data for all infrastructure types around a coordinate.

        Returns:
            Dict keyed by infra type with 'nearest' and 'places' info
        """
        data = {}

        for infra_type, config in INFRASTRUCTURE_TYPES.items():
            logger.info(f"Searching for {infra_type}...")
            all_places = []

            # Search for each Google Place type associated with this infra type
            for place_type in config['place_types']:
                places = self.maps.find_nearby_places(
                    lat, lng,
                    place_type=place_type,
                    radius=config['max_radius_m']
                )
                all_places.extend(places)

            # Deduplicate by place_id
            seen = set()
            unique_places = []
            for p in all_places:
                pid = p.get('place_id', p['name'])
                if pid not in seen:
                    seen.add(pid)
                    unique_places.append(p)

            # Find nearest via Haversine (avoids extra API calls)
            nearest_dist = None
            for place in unique_places:
                dist = self.calculator.haversine_distance(
                    lat, lng, place['lat'], place['lng']
                )
                if nearest_dist is None or dist < nearest_dist:
                    nearest_dist = dist

            count = self.calculator.count_places_in_radius(
                lat, lng, unique_places, config['max_radius_m']
            )

            data[infra_type] = {
                'places': unique_places,
                'nearest_distance_m': nearest_dist,
                'count_in_radius': count
            }

        return data

    def score_all(self, infra_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Score each infrastructure type.

        Returns:
            Dict of scores per type
        """
        scores = {}
        for infra_type, data in infra_data.items():
            scores[infra_type] = self.calculator.score_infrastructure_type(
                infra_type=infra_type,
                nearest_distance_m=data['nearest_distance_m'],
                count_in_radius=data['count_in_radius']
            )
        return scores

    def calculate_final_score(self, scores: Dict[str, Dict]) -> float:
        """
        Calculate weighted final infrastructure score (0-100).
        """
        total_weight = 0
        weighted_sum = 0

        for infra_type, score_data in scores.items():
            weight = INFRASTRUCTURE_TYPES.get(infra_type, {}).get('weight', 0.1)
            weighted_sum += score_data['score'] * weight
            total_weight += weight

        if total_weight == 0:
            return 50.0  # neutral default

        return round(weighted_sum / total_weight, 2)

    def generate_insights(
        self,
        scores: Dict[str, Dict],
        infra_data: Dict[str, Dict],
        final_score: float
    ) -> List[str]:
        """
        Generate human-readable insights from infrastructure data.
        """
        insights = []

        # Overall assessment
        if final_score >= 80:
            insights.append(f"Excellent infrastructure connectivity (score: {final_score}/100)")
        elif final_score >= 60:
            insights.append(f"Good infrastructure with room for improvement (score: {final_score}/100)")
        elif final_score >= 40:
            insights.append(f"Moderate infrastructure — some gaps exist (score: {final_score}/100)")
        else:
            insights.append(f"Poor infrastructure connectivity (score: {final_score}/100)")

        # Specific highlights (best and worst)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)

        # Top 2 strengths
        for infra_type, score_data in sorted_scores[:2]:
            dist = score_data.get('nearest_distance_m')
            count = score_data.get('count_in_radius', 0)
            dist_text = f"{int(dist)}m" if dist else "unknown distance"
            insights.append(
                f"Strong {infra_type} access: {count} options, nearest at {dist_text}"
            )

        # Top 2 weaknesses
        for infra_type, score_data in sorted_scores[-2:]:
            if score_data['score'] < 50:
                dist = score_data.get('nearest_distance_m')
                dist_text = f"{int(dist)}m away" if dist else "none found nearby"
                insights.append(
                    f"Limited {infra_type} access: {dist_text}"
                )

        return insights[:5]

    def analyze(
        self,
        locality: str,
        city: str
    ) -> Tuple[float, List[str], Dict]:
        """
        Full analysis pipeline for a locality.

        Args:
            locality: Locality name
            city: City name

        Returns:
            (final_score, insights, detailed_data)
        """
        # Step 1: Geocode
        location = self.maps.geocode_locality(locality, city)
        if not location:
            logger.error(f"Could not geocode {locality}, {city}")
            return 50.0, ["Could not geocode locality — using neutral score"], {}

        lat, lng = location['lat'], location['lng']
        logger.info(f"Analyzing infrastructure for {locality} at ({lat}, {lng})")

        # Step 2: Collect data
        infra_data = self.collect_infrastructure_data(lat, lng)

        # Step 3: Score each type
        scores = self.score_all(infra_data)

        # Step 4: Final weighted score
        final_score = self.calculate_final_score(scores)

        # Step 5: Generate insights
        insights = self.generate_insights(scores, infra_data, final_score)

        detailed = {
            'location': location,
            'component_scores': scores,
            'final_score': final_score
        }

        return final_score, insights, detailed