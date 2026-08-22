import math
from typing import Dict, Tuple

def calculate_initial_bearing(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate forward azimuth (bearing) from point 1 to point 2 in degrees (0 to 360).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing_rad = math.atan2(y, x)
    bearing_deg = (math.degrees(bearing_rad) + 360) % 360
    return round(bearing_deg, 2)

def calculate_bounding_box(
    center_lat: float, center_lon: float, radius_meters: float
) -> Dict[str, float]:
    """
    Compute a lat/lon bounding box for a given center point and radius in meters.
    """
    lat_delta = (radius_meters / 6371000.0) * (180.0 / math.pi)
    lon_delta = (radius_meters / (6371000.0 * math.cos(math.radians(center_lat)))) * (180.0 / math.pi)
    return {
        "min_lat": center_lat - lat_delta,
        "max_lat": center_lat + lat_delta,
        "min_lon": center_lon - lon_delta,
        "max_lon": center_lon + lon_delta,
    }

def format_coordinates(lat: float, lon: float, precision: int = 6) -> str:
    """
    Formats latitude and longitude to standard string.
    """
    return f"{lat:.{precision}f}, {lon:.{precision}f}"
