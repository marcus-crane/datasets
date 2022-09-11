import csv
import json
import requests

trips = []

with open('trips.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        trips.append(row)

segments = trips

routes = []

for trip in segments:
    url = f"http://192.168.1.111:8080/ors/v2/directions/driving-car?start={trip['originy']},{trip['originx']}&end={trip['destinationy']},{trip['destinationx']}"
    r = requests.get(url)
    data = r.json()

    timestamps = [0]
    duration = 0

    coords = data['features'][0]['geometry']['coordinates']

    for entry in coords:
        duration += 200
        timestamps.append(duration)

    routes.append({
        "vendor": 0,
        "path": coords,
        "timestamps": timestamps
    })

with open('routes.json', 'w') as file:
    json.dump(routes, file)