import os
import sqlite3

import herepy

conn = sqlite3.connect('towing.db')
c    = conn.cursor()

api_key  = os.environ.get("HERE_API_KEY")
api = herepy.GeocoderApi(api_key)

c.execute('''
    SELECT
        origin
    FROM
        events
    UNION
    SELECT
        destination
    FROM
        events
''')
addresses = c.fetchall()

unmatched_addresses = []

def create_address_table():
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS addresses
            (
                original_address text,
                match_relevance real,
                location_id text,
                latitude text,
                longitude text,
                full_address text,
                house_number text,
                street text,
                district text,
                city text,
                county text,
                state text,
                country text,
                postal_code text
            )
        ''')
        conn.commit()
        print('Created address table')
    except Exception:
        print('Skipping address table creation. Assuming it already exists')

def parse_geocoding_response(data, original_address):
    try:
        result = data.Response['View'][0]['Result'][0]
        location = result['Location']
        address = location['Address']
    except IndexError:
        unmatched_addresses.append(original_address)
        print(f'Found no results for {original_address}')
        raise IndexError
    except Exception as ex:
        print(f'Bad result for {original_address}: {ex}')
        print(data.Response)
        return

    response = {
        "original_address": original_address,
        "match_relevance": result['Relevance'],
        "location_id": location['LocationId'],
        "latitude": location['DisplayPosition']['Latitude'],
        "longitude": location['DisplayPosition']['Longitude'],
        "full_address": address['Label'],
        "house_number": address.get('HouseNumber'),
        "street": address.get('Street'),
        "district": address.get('District'),
        "city": address.get('City'),
        "county": address.get('County'),
        "state": address.get('State'),
        "country": address.get('Country'),
        "postal_code": address.get('PostalCode')
    }

    return tuple(response.values())

def insert_address(geocoded_data):
    try:
        c.execute(f'''
            INSERT INTO addresses
            VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
        ''', geocoded_data)
        conn.commit()
    except Exception as ex:
        print(f'Failed to save data: {ex}')

def perform_geocode_request(address):
    """
    http://bboxfinder.com/#-37.474858,174.309082,-36.558188,175.567017
    """
    padded_address = address + ' Auckland New Zealand'
    return api.address_with_boundingbox(padded_address,
                                        [174.309082, -37.474858],
                                        [175.567017, -36.558188])

create_address_table()
for address in addresses:
    try:
        address_text = address[0]
        response = perform_geocode_request(address_text)
        formatted_address = parse_geocoding_response(response, address_text)
        insert_address(formatted_address)
    except IndexError:
        pass
    except Exception as ex:
        print(f'Oh no: {ex}')

with open('unmatched_addresses.txt', 'w') as file:
    file.write(
        "\n".join(unmatched_addresses)
    )

conn.close()
