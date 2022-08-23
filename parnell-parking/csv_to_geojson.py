import csv
import sys
from geojson import LineString, MultiLineString, Feature, GeometryCollection, FeatureCollection, dumps
import json

csv.field_size_limit(sys.maxsize)

def cleanup_coord_string(shape):
    if 'MULTILINESTRING' in shape:
        shape = shape.replace('MULTILINESTRING', '')
    else:
        shape = shape.replace('LINESTRING', '')
    shape = shape.replace('(', '').replace(')', '')
    return shape.strip()

def transform_line_string_pairs(pair_string, TYPE=LineString):
    line_string = []
    pairs = pair_string.split(',')
    for pair in pairs:
        subpair = pair.split(' ')
        pairing = []
        for item in subpair:
            pairing.append(float(item))
        line_string.append(tuple(pairing))
    return TYPE(line_string)


def save_geojson(feature_set):
    with open('streets.geojson', 'w') as file:
        mapdata = FeatureCollection(feature_set)
        file.write(dumps(mapdata, indent=2))
        print('Saved streets.json')

def build_props(row, day, hour, tickets):
    return {
        'full_road_name': row['full_road_name'],
        'hour': int(hour),
        'tickets': int(tickets),
        'day': day.lower()
    }

with open('locs.json') as file:
    locations = json.load(file)

with open('parnell-addressing.csv') as csvfile:
    address_reader = csv.DictReader(csvfile)
    features = []
    for row in address_reader:
        shape = row['\ufeffWKT']
        shape = cleanup_coord_string(shape)
        item = transform_line_string_pairs(shape)
        location = row['full_road_name'].upper()
        if location in locations:
            for day in locations[location]:
                for hour in locations[location][day]:
                    tickets = locations[location][day][hour]
                    feature = Feature(geometry=item, properties=build_props(row, day, hour, tickets))
                    features.append(feature)
    save_geojson(features)
    