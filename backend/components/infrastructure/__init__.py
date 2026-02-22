"""
Infrastructure Component
========================
Scores a locality's infrastructure using Google Maps APIs.

Evaluates 6 infrastructure categories:
- Metro / Train stations
- Hospitals
- Schools
- Supermarkets
- Banks / ATMs
- Bus stops / Transit

Main entry point: get_infrastructure_score()
"""

from .google_maps import GoogleMapsAPI
from .scorer import InfrastructureScorer
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def get_infrastructure_score(
    locality: str,
    city: str,
    config: Dict
) -> Tuple[float, List[str]]:
    """
    Main function — get infrastructure score for a locality.

    Args:
        locality: Locality/area name (e.g., "Koramangala")
        city: City name (e.g., "Bangalore")
        config: Dict with 'api_key' for Google Maps

    Returns:
        Tuple of (score: float 0-100, insights: List[str])

    Example:
        >>> score, insights = get_infrastructure_score(
        ...     locality="Bandra West",
        ...     city="Mumbai",
        ...     config={"api_key": "your_google_maps_key"}
        ... )
        >>> print(f"Score: {score}/100")
        >>> print(insights)
    """
    api_key = config.get('api_key') or config.get('google_maps_key')

    if not api_key:
        logger.error("No Google Maps API key provided in config")
        return 50.0, ["Infrastructure analysis unavailable — no API key"]

    try:
        maps_api = GoogleMapsAPI(api_key=api_key)
        scorer = InfrastructureScorer(maps_api=maps_api)

        score, insights, _ = scorer.analyze(locality, city)
        return score, insights

    except Exception as e:
        logger.error(f"Infrastructure scoring failed for {locality}, {city}: {e}")
        return 50.0, [f"Infrastructure analysis encountered an error — using neutral score"]


def get_detailed_infrastructure(
    locality: str,
    city: str,
    config: Dict
) -> Dict:
    """
    Get full detailed infrastructure analysis (includes per-category breakdown).

    Returns:
        Dict with 'score', 'insights', 'component_scores', 'location'
    """
    api_key = config.get('api_key') or config.get('google_maps_key')

    if not api_key:
        return {'score': 50.0, 'insights': ["No API key"], 'component_scores': {}}

    try:
        maps_api = GoogleMapsAPI(api_key=api_key)
        scorer = InfrastructureScorer(maps_api=maps_api)

        score, insights, detailed = scorer.analyze(locality, city)

        return {
            'score': score,
            'insights': insights,
            **detailed
        }

    except Exception as e:
        logger.error(f"Detailed infrastructure analysis failed: {e}")
        return {'score': 50.0, 'insights': [str(e)], 'component_scores': {}}


__all__ = ['get_infrastructure_score', 'get_detailed_infrastructure']