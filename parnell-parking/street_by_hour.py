import csv
import pendulum
import json

time = {}

with open('parnell_str.csv') as csvfile:
    ticketreader = csv.DictReader(csvfile)
    for row in ticketreader:
        issue_time = row['Issue Time']
        issue_hour = pendulum.parse(issue_time, exact=True).hour
        issue_date = row['Issue Date']
        issue_day = pendulum.from_format(issue_date, 'MM/DD/YYYY').format('dddd')
        location = row['Location']
        if location not in time:
            time[location] = {}
        if issue_day not in time[location]:
            time[location][issue_day] = {}
        if issue_hour not in time[location][issue_day]:
            time[location][issue_day][issue_hour] = 1
        else:
            time[location][issue_day][issue_hour] += 1

with open('locs.json', 'w') as file:
    file.write(json.dumps(time, sort_keys=True, indent=2))
