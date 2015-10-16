import math
import os
R = 6371000


def step_point(point1, point2, fraction):
    lat1, lon1 = map(math.radians, point1)
    lat2, lon2 = map(math.radians, point2)
    distance = calculate_distance((lat1, lon1), (lat2, lon2)) / R
    a = math.cos(lat1) * math.cos(lat2)
    b = math.sin(fraction * distance) / math.sin(distance)
    x = a * math.cos(lat1) * math.cos(lon1) + b * math.cos(lat2) * \
        math.cos(lon2)
    y = a * math.cos(lat1) * math.sin(lon1) + b * math.cos(lat2) * \
        math.sin(lon2)
    z = a * math.sin(lat1) + b * math.sin(lat2)
    lat_point = math.atan2(z, math.sqrt(x**2 + y**2))
    lon_point = math.atan2(y, x)
    lat_point, lon_point = map(math.degrees, (lat_point, lon_point))
    return round(lat_point, 7), round(lon_point, 7)


def calculate_distance(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = math.sin(delta_lat / 2) * math.sin(delta_lat/2) + \
        math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon/2) * \
        math.sin(delta_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def in_circle(center_x, center_y, radius, x, y):
    center_x, center_y, x, y = map(float, (center_x, center_y, x, y))
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2


def route(point1, point2):
    command = 'router --dir=data --prefix=am --lat1=%s --lon1=%s --lat2=%s ' + \
              '--lon2=%s --output-text --output-stdout --transport=foot'
    route = os.popen(command % (*point1, *point2)).readlines()[6:]
    points = [r.split() for r in route]
    print(points)
    return [{'lat': point[0], 'lon':point[1]} for point in points]
