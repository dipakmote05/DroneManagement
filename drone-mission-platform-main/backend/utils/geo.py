import math

# =================================================
# CONSTANTS
# =================================================
EARTH_RADIUS_M = 6378137  # meters (WGS84)


# =================================================
# HAVERSINE DISTANCE (meters)
# =================================================
def haversine_distance(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c


# =================================================
# REMOVE DUPLICATE / STATIC POINTS
# =================================================
def _filter_points(coords, min_distance=0.3):
    """
    Removes points which are too close to each other
    """
    if not coords:
        return []

    filtered = [coords[0]]

    for lat, lng in coords[1:]:
        last_lat, last_lng = filtered[-1]
        dist = haversine_distance(last_lat, last_lng, lat, lng)

        if dist >= min_distance:
            filtered.append((lat, lng))

    return filtered


# =================================================
# CLOSE POLYGON IF NOT CLOSED
# =================================================
def _close_polygon(coords):
    """
    Ensure polygon is closed (last point == first point)
    """
    if len(coords) < 3:
        return coords

    first = coords[0]
    last = coords[-1]

    if haversine_distance(first[0], first[1], last[0], last[1]) > 0.3:
        coords.append(first)

    return coords


# =================================================
# POLYGON AREA (ANY SHAPE, ROBUST)
# =================================================
def calculate_polygon_area(coords):
    """
    Calculate area of ANY polygon formed by GPS points.
    Handles:
    - duplicate points
    - static GPS
    - open polygon

    Returns:
        area in square meters
    """

    if not coords or len(coords) < 3:
        return 0.0

    # 🔥 STEP 1: Remove duplicate / static points
    coords = _filter_points(coords)

    if len(coords) < 3:
        return 0.0

    # 🔥 STEP 2: Close polygon
    coords = _close_polygon(coords)

    # 🔥 STEP 3: Local projection
    lat0 = math.radians(coords[0][0])
    lng0 = math.radians(coords[0][1])

    points = []

    for lat, lng in coords:
        lat = math.radians(lat)
        lng = math.radians(lng)

        x = EARTH_RADIUS_M * (lng - lng0) * math.cos(lat0)
        y = EARTH_RADIUS_M * (lat - lat0)

        points.append((x, y))

    # 🔥 STEP 4: Shoelace formula
    area = 0.0
    n = len(points)

    for i in range(n - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        area += (x1 * y2) - (x2 * y1)

    return abs(area) / 2.0
