"""
Proximity Calculator
Handles distance calculations and radius-based checks for infrastructure scoring.
"""

import math
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Infrastructure categories and their Google Places types
INFRASTRUCTURE_TYPES = {
    'metro': {
        'place_types': ['subway_station', 'train_station'],
        'ideal_radius_m': 1000,     # within 1km = excellent
        'max_radius_m': 5000,       # beyond 5km = poor
        'weight': 0.25
    },
    'hospital': {
        'place_types': ['hospital'],
        'ideal_radius_m': 2000,
        'max_radius_m': 8000,
        'weight': 0.20
    },
    'school': {
        'place_types': ['school', 'primary_school', 'secondary_school'],
        'ideal_radius_m': 1500,
        'max_radius_m': 5000,
        'weight': 0.15
    },
    'supermarket': {
        'place_types': ['supermarket', 'grocery_or_supermarket'],
        'ideal_radius_m': 1000,
        'max_radius_m': 3000,
        'weight': 0.15
    },
    'bank': {
        'place_types': ['bank', 'atm'],
        'ideal_radius_m': 1000,
        'max_radius_m': 3000,
        'weight': 0.10
    },
    'bus_stop': {
        'place_types': ['bus_station', 'transit_station'],
        'ideal_radius_m': 500,
        'max_radius_m': 2000,
        'weight': 0.15
    }
}


class ProximityCalculator:
    """
    Calculates proximity-based scores for infrastructure points.
    Uses both straight-line (Haversine) and actual road distances.
    """

    @staticmethod
    def haversine_distance(
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """
        Calculate straight-line distance between two coordinates using Haversine formula.

        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lng2 - lng1)

        a = (
            math.sin(dphi / 2) ** 2 +
            math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @staticmethod
    def distance_to_score(
        distance_m: float,
        ideal_radius_m: float,
        max_radius_m: float
    ) -> float:
        """
        Convert a distance in meters to a 0-100 score.

        Scoring logic:
        - distance <= ideal_radius → 100 (excellent)
        - ideal_radius < distance <= max_radius → linearly interpolated 0-100
        - distance > max_radius → 0 (poor)

        Args:
            distance_m: Actual distance in meters
            ideal_radius_m: Distance for maximum score
            max_radius_m: Distance at which score becomes 0

        Returns:
            Score between 0 and 100
        """
        if distance_m <= ideal_radius_m:
            return 100.0
        elif distance_m >= max_radius_m:
            return 0.0
        else:
            # Linear interpolation
            ratio = (distance_m - ideal_radius_m) / (max_radius_m - ideal_radius_m)
            return round(100.0 * (1 - ratio), 2)

    def score_infrastructure_type(
        self,
        infra_type: str,
        nearest_distance_m: Optional[float],
        count_in_radius: int
    ) -> Dict:
        """
        Score a specific infrastructure type based on nearest distance and count.

        Args:
            infra_type: Key from INFRASTRUCTURE_TYPES (e.g., 'metro', 'hospital')
            nearest_distance_m: Distance to nearest facility in meters (None if not found)
            count_in_radius: Number of facilities found within max_radius

        Returns:
            Dict with 'score', 'distance_score', 'count_score', 'details'
        """
        config = INFRASTRUCTURE_TYPES.get(infra_type, {})
        ideal = config.get('ideal_radius_m', 2000)
        max_r = config.get('max_radius_m', 5000)

        # Distance score (70% of total)
        if nearest_distance_m is None:
            distance_score = 0.0
        else:
            distance_score = self.distance_to_score(nearest_distance_m, ideal, max_r)

        # Count score (30% of total) — more options = better
        if count_in_radius == 0:
            count_score = 0.0
        elif count_in_radius == 1:
            count_score = 50.0
        elif count_in_radius <= 3:
            count_score = 75.0
        elif count_in_radius <= 6:
            count_score = 90.0
        else:
            count_score = 100.0

        combined_score = (distance_score * 0.7) + (count_score * 0.3)

        return {
            'score': round(combined_score, 2),
            'distance_score': distance_score,
            'count_score': count_score,
            'nearest_distance_m': nearest_distance_m,
            'count_in_radius': count_in_radius
        }

    def count_places_in_radius(
        self,
        center_lat: float,
        center_lng: float,
        places: List[Dict],
        radius_m: float
    ) -> int:
        """
        Count how many places fall within a given radius using Haversine distance.

        Args:
            center_lat, center_lng: Center point
            places: List of place dicts with 'lat', 'lng'
            radius_m: Radius in meters

        Returns:
            Count of places within radius
        """
        count = 0
        for place in places:
            dist = self.haversine_distance(
                center_lat, center_lng,
                place['lat'], place['lng']
            )
            if dist <= radius_m:
                count += 1
        return count