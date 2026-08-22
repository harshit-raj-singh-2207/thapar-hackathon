import re
from typing import Tuple

def validate_coordinates(lat: float, lon: float) -> Tuple[bool, str]:
    """
    Validate that latitude is between -90 and 90, and longitude between -180 and 180.
    """
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return False, "Coordinates must be numeric values."
    if lat < -90.0 or lat > 90.0:
        return False, f"Latitude {lat} is out of bounds (-90 to +90)."
    if lon < -180.0 or lon > 180.0:
        return False, f"Longitude {lon} is out of bounds (-180 to +180)."
    return True, ""

def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Validate standard international or local phone numbers.
    """
    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone)
    if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
        return False, "Invalid phone number format."
    return True, ""

def validate_safe_zone_radius(radius: float, min_val: float = 10.0, max_val: float = 50000.0) -> Tuple[bool, str]:
    """
    Validate safe zone radius within reasonable human boundary limits.
    """
    if radius < min_val:
        return False, f"Safe zone radius must be at least {min_val} meters."
    if radius > max_val:
        return False, f"Safe zone radius cannot exceed {max_val} meters."
    return True, ""
