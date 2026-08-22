import math
from typing import List, Tuple

EARTH_RADIUS_METERS = 6371000.0  # Earth radius in meters

def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points on Earth in meters using Haversine formula.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_METERS * c

def is_point_in_radius(
    lat: float, lon: float, center_lat: float, center_lon: float, radius_meters: float
) -> bool:
    """
    Checks if a (lat, lon) point falls within radius_meters of (center_lat, center_lon).
    """
    dist = calculate_haversine_distance(lat, lon, center_lat, center_lon)
    return dist <= radius_meters

def is_point_in_polygon(
    lat: float, lon: float, polygon: List[Tuple[float, float]]
) -> bool:
    """
    Ray-casting algorithm to determine if a point (lat, lon) is inside a polygon.
    Polygon is defined as a list of (lat, lon) vertices.
    """
    if not polygon or len(polygon) < 3:
        return False

    num_vertices = len(polygon)
    inside = False

    p1_lat, p1_lon = polygon[0]
    for i in range(1, num_vertices + 1):
        p2_lat, p2_lon = polygon[i % num_vertices]
        if min(p1_lon, p2_lon) < lon <= max(p1_lon, p2_lon):
            if lat <= max(p1_lat, p2_lat):
                if p1_lon != p2_lon:
                    x_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                if p1_lat == p2_lat or lat <= x_inters:
                    inside = not inside
        p1_lat, p1_lon = p2_lat, p2_lon

    return inside
