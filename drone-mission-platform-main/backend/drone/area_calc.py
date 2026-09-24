import math

def calculate_polygon_area(coords):
    """
    coords = [(lat, lng), (lat, lng), ...]
    returns area in square meters
    """

    if len(coords) < 3:
        return 0.0

    # Earth radius in meters
    R = 6378137

    # reference point (first GPS point)
    lat0 = math.radians(coords[0][0])
    lng0 = math.radians(coords[0][1])

    points = []

    for lat, lng in coords:
        lat = math.radians(lat)
        lng = math.radians(lng)

        x = R * (lng - lng0) * math.cos(lat0)
        y = R * (lat - lat0)

        points.append((x, y))

    # Shoelace formula
    area = 0
    n = len(points)

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += (x1 * y2) - (x2 * y1)

    return abs(area) / 2
