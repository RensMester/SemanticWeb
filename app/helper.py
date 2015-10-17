from math import *
import os
R = 6371000


def step_point(point1, point2, fraction):
    lat1, lon1 = map(radians, point1)
    lat2, lon2 = map(radians, point2)
    '''
    lat1, lon1 = point1
    lat2, lon2 = point2
    '''
    distance = calculate_distance((lat1, lon1), (lat2, lon2)) / R
    a = cos(lat1) * cos(lat2)
    b = sin(fraction * distance) / sin(distance)
    x = a * cos(lat1) * cos(lon1) + b * cos(lat2) * \
        cos(lon2)
    y = a * cos(lat1) * sin(lon1) + b * cos(lat2) * \
        sin(lon2)
    z = a * sin(lat1) + b * sin(lat2)
    lat_point = atan2(z, sqrt(x**2 + y**2))
    lon_point = atan2(y, x)
    lat_point, lon_point = map(degrees, (lat_point, lon_point))
    '''
    #  better version
    a = sin((1-fraction) * d) / sin(d)
    b = sin(fraction*d) / sin(d)
    x = a * cos(lat1) * cos(lon1) + b * cos(lat2) * cos(lon2)
    y = a * cos(lat1) * sin(lon1) + b * cos(lat2) * sin(lon2)
    z = a * sin(lat1)
    lat_point = atan2(z, sqrt(x**2 + y**2))
    lon_point = atan2(y, x)
    '''
    return lat_point, lon_point


def calculate_distance(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = sin(delta_lat / 2) * sin(delta_lat/2) + \
        cos(lat1) * cos(lat2) * sin(delta_lon/2) * \
        sin(delta_lon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def in_circle(center_x, center_y, radius, x, y):
    center_x, center_y, x, y = map(float, (center_x, center_y, x, y))
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2


def route(point1, point2):
    command = 'router --dir=data --prefix=am --lat1=%s --lon1=%s --lat2=%s ' + \
              '--lon2=%s --output-text --output-stdout --transport=bicycle'
    route = os.popen(command % (point1[0], point[1], point2[0],
                                point[1])).readlines()[6:]
    points = [r.split() for r in route]
    if points:
        return [{'lat': float(point[0]), 'lon':float(point[1])} for point in
                points]
    else:
        print(points)
        return []
