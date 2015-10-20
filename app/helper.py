from math import *  # noqa
import random
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


def is_in_circle(center_x, center_y, radius, x, y):
    center_x, center_y, x, y = map(float, (center_x, center_y, x, y))
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2


def router(point1, point2):
    command = 'router --dir=data --prefix=am --lat1=%s --lon1=%s --lat2=%s ' +\
              '--lon2=%s --output-text --output-stdout --transport=bicycle'
    route = os.popen(command % (point1[0], point1[1], point2[0],
                                point2[1])).readlines()[6:]
    print(command % (point1[0], point1[1], point2[0], point2[1]))
    points = [r.split() for r in route]
    if points:
        return [{'lat': float(point[0]), 'lon':float(point[1])} for point in
                points]
    else:
        print(points)
        return []


def get_in_area(steps, places, r):
    step_points = []
    interesting = []
    start_latlon = steps[0]['start_location']['lat'], steps[0]['start_location']['lng']
    interesting = [{'lat': {'value': str(start_latlon[0])},
                    'lon': {'value': str(start_latlon[1])}}]

    for step in steps:
        start, end = step['start_location'], step['end_location']
        start_latlon = start['lat'], start['lng']
        end_latlon = end['lat'], end['lng']

        distance = step['distance']['value']
        if distance > 200:
            num_circles = int(distance / 200)
            print('############################')
            print(num_circles)
            for i in range(0, num_circles + 1):
                #    print(i/(num_circles + 1))
                fraction = i/(num_circles + 1)
                lat, lon = step_point(start_latlon, end_latlon, fraction)
                in_circle = [p for p in places if
                             is_in_circle(lat, lon, r, p['lat']['value'],
                                          p['lon']['value'])]
                step_points.append((lat, lon))
                in_circle = list(in_circle)
                print(len(in_circle))
                if len(in_circle) > 5:
                    random.shuffle(in_circle)

                interesting.extend(in_circle[:1])
            print('############################')
    interesting.append({'lat': {'value': str(end_latlon[0])},
                        'lon': {'value': str(end_latlon[1])}})
    return interesting, step_points


def calculate_scenic_route(interesting, steps):
    route = []
    for i, p in enumerate(interesting):
        lat, lon = p['lat']['value'], p['lon']['value']
        if i == len(interesting) - 1:
            print(i, len(interesting)-1)
            n_lat, n_lon = interesting[-1]['lat']['value'], interesting[i-1]['lon']['value']
        else:
            n_lat, n_lon = interesting[i+1]['lat']['value'], interesting[i+1]['lon']['value']
        route.extend(router((lat, lon), (n_lat, n_lon)))
    end_latlon = steps[-1]['end_location']['lat'], steps[-1]['end_location']['lng']
    route.extend(router((lat, lon), end_latlon))
    return route
