import math

# -------------------------------
# Distance between 2 GPS points
# -------------------------------
def distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2 +
        math.cos(phi1) * math.cos(phi2) *
        math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# -------------------------------
# Check if waypoint reached
# -------------------------------
def reached_waypoint(curr_lat, curr_lng, wp_lat, wp_lng, threshold=5):
    """
    threshold = meters
    """
    return distance_meters(curr_lat, curr_lng, wp_lat, wp_lng) <= threshold

def generate_square_waypoints(center_lat, center_lng, size_m=20):
    """
    Generates 4-point square around target
    """
    delta = size_m / 111320  # meters to degrees approx

    return [
        (center_lat + delta, center_lng + delta),
        (center_lat + delta, center_lng - delta),
        (center_lat - delta, center_lng - delta),
        (center_lat - delta, center_lng + delta),
    ]
