"""Utility functions for school distance calculations"""
import math


def calculate_distance_between_pincodes(pincode1, pincode2):
    """
    Calculate approximate distance between two pin codes in kilometers.
    
    This is a simplified implementation. For production, you'd want to:
    - Use geocoding API to get coordinates from pin codes
    - Use Haversine formula for accurate distance calculation
    
    For now, we use a simple approximation based on pin code differences.
    """
    try:
        # Extract numeric parts from pin codes
        pin1 = ''.join(filter(str.isdigit, str(pincode1)))[:6]
        pin2 = ''.join(filter(str.isdigit, str(pincode2)))[:6]
        
        if not pin1 or not pin2:
            return None
        
        pin1_int = int(pin1)
        pin2_int = int(pin2)
        
        # Simple approximation: difference in pin codes
        # Indian pin codes are roughly organized geographically
        pin_diff = abs(pin1_int - pin2_int)
        
        # Rough approximation: 1 pin code unit ≈ 0.5-1 km (this is very approximate)
        # For more accuracy, use geocoding API
        distance = pin_diff * 0.01  # Very rough approximation
        
        # Cap at reasonable distances
        return min(distance, 1000)  # Max 1000km
    
    except (ValueError, TypeError):
        return None


def get_pincode_coordinates(pincode):
    """
    Get approximate coordinates for a pin code.
    This is a placeholder - in production, use a geocoding API.
    
    Returns (lat, lon) tuple or None
    
    Note: This is a simplified approximation. For accurate results, integrate with:
    - Google Geocoding API
    - OpenStreetMap Nominatim API  
    - India Post API
    - pincode database
    """
    try:
        pin = ''.join(filter(str.isdigit, str(pincode)))[:6]
        if not pin or len(pin) != 6:
            return None
        
        pin_int = int(pin)
        
        # Indian pin codes: first digit indicates region
        # This is a very rough approximation - not geographically accurate
        # For demo purposes only
        
        # Base coordinates for major Indian cities (approximate)
        # This is simplified - actual pin codes need proper geocoding
        
        # Use pin code as a rough indicator
        # Dividing by factors to spread across India's approximate bounds
        # India spans roughly 8-37°N, 68-97°E
        
        # Very rough conversion (NOT ACCURATE - just for demonstration)
        lat_range = 29  # Approximate range for Indian latitudes
        lon_range = 29  # Approximate range for Indian longitudes
        
        base_lat = 20.5  # Approximate southern boundary
        base_lon = 68.0  # Approximate western boundary
        
        # Spread pin codes across the range
        lat_offset = (pin_int % 10000) / 10000 * lat_range
        lon_offset = (pin_int // 100) % 10000 / 10000 * lon_range
        
        lat = base_lat + lat_offset
        lon = base_lon + lon_offset
        
        # Ensure within reasonable bounds for India
        lat = max(8.0, min(37.0, lat))
        lon = max(68.0, min(97.0, lon))
        
        return (lat, lon)
    
    except (ValueError, TypeError):
        return None


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def calculate_distance(user_pincode, school_pincode):
    """
    Calculate distance between user's pin code and school's pin code.
    
    Returns distance in kilometers or None if calculation fails.
    """
    if not user_pincode or not school_pincode:
        return None
    
    # Try to get coordinates
    user_coords = get_pincode_coordinates(user_pincode)
    school_coords = get_pincode_coordinates(school_pincode)
    
    if user_coords and school_coords:
        # Use Haversine formula for accurate distance
        return haversine_distance(
            user_coords[0], user_coords[1],
            school_coords[0], school_coords[1]
        )
    else:
        # Fallback to simple approximation
        return calculate_distance_between_pincodes(user_pincode, school_pincode)

