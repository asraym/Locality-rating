"""
Google Maps API Wrapper
Handles all Google Maps API interactions for infrastructure scoring.
"""

import googlemaps
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class GoogleMapsAPI:
    """
    Wrapper for Google Maps APIs:
    - Geocoding API: Convert locality name to coordinates
    - Places API: Find nearby amenities/infrastructure
    - Distance Matrix API: Calculate travel times
    """

    def __init__(self, api_key: str):
        """
        Initialize with Google Maps API key.

        Args:
            api_key: Google Maps API key (needs Geocoding, Places, Distance Matrix enabled)
        """
        self.client = googlemaps.Client(key=api_key)
        self.api_key = api_key

    def geocode_locality(self, locality: str, city: str) -> Optional[Dict]:
        """
        Convert locality name to lat/lng coordinates.

        Args:
            locality: Locality/area name (e.g., "Koramangala")
            city: City name (e.g., "Bangalore")

        Returns:
            Dict with 'lat', 'lng', 'formatted_address' or None if not found
        """
        try:
            query = f"{locality}, {city}, India"
            results = self.client.geocode(query)

            if not results:
                logger.warning(f"No geocoding results for: {query}")
                return None

            location = results[0]['geometry']['location']
            return {
                'lat': location['lat'],
                'lng': location['lng'],
                'formatted_address': results[0].get('formatted_address', query)
            }

        except Exception as e:
            logger.error(f"Geocoding error for {locality}, {city}: {e}")
            return None

    def find_nearby_places(
        self,
        lat: float,
        lng: float,
        place_type: str,
        radius: int = 3000
    ) -> List[Dict]:
        """
        Find places of a specific type near given coordinates.

        Args:
            lat: Latitude
            lng: Longitude
            place_type: Google Places type (e.g., 'hospital', 'school', 'subway_station')
            radius: Search radius in meters (default: 3km)

        Returns:
            List of place dicts with name, location, rating
        """
        try:
            results = self.client.places_nearby(
                location=(lat, lng),
                radius=radius,
                type=place_type
            )

            places = []
            for place in results.get('results', []):
                location = place['geometry']['location']
                places.append({
                    'name': place.get('name', 'Unknown'),
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'rating': place.get('rating', None),
                    'vicinity': place.get('vicinity', ''),
                    'place_id': place.get('place_id', '')
                })

            return places

        except Exception as e:
            logger.error(f"Places API error for type {place_type}: {e}")
            return []

    def get_distance_matrix(
        self,
        origin: Tuple[float, float],
        destinations: List[Tuple[float, float]],
        mode: str = 'driving'
    ) -> List[Optional[Dict]]:
        """
        Calculate distances and travel times from origin to multiple destinations.

        Args:
            origin: (lat, lng) tuple
            destinations: List of (lat, lng) tuples
            mode: 'driving', 'walking', 'transit', 'bicycling'

        Returns:
            List of dicts with 'distance_m', 'duration_s', or None if failed
        """
        if not destinations:
            return []

        try:
            result = self.client.distance_matrix(
                origins=[origin],
                destinations=destinations,
                mode=mode,
                units='metric'
            )

            distances = []
            elements = result['rows'][0]['elements']
            for element in elements:
                if element['status'] == 'OK':
                    distances.append({
                        'distance_m': element['distance']['value'],
                        'duration_s': element['duration']['value'],
                        'distance_text': element['distance']['text'],
                        'duration_text': element['duration']['text']
                    })
                else:
                    distances.append(None)

            return distances

        except Exception as e:
            logger.error(f"Distance Matrix API error: {e}")
            return [None] * len(destinations)

    def find_nearest_place(
        self,
        lat: float,
        lng: float,
        place_type: str,
        max_radius: int = 10000
    ) -> Optional[Dict]:
        """
        Find the single nearest place of a given type.

        Args:
            lat: Latitude
            lng: Longitude
            place_type: Google Places type
            max_radius: Max search radius in meters

        Returns:
            Dict with place info + distance, or None
        """
        places = self.find_nearby_places(lat, lng, place_type, radius=max_radius)
        if not places:
            return None

        # Get distances to all found places
        destinations = [(p['lat'], p['lng']) for p in places[:10]]  # limit API calls
        distances = self.get_distance_matrix((lat, lng), destinations)

        # Find nearest
        nearest = None
        min_dist = float('inf')

        for place, dist_info in zip(places[:10], distances):
            if dist_info and dist_info['distance_m'] < min_dist:
                min_dist = dist_info['distance_m']
                nearest = {**place, **dist_info}

        return nearest