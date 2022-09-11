import csv
import sqlite3

con = sqlite3.connect("towing.db")
con.row_factory = sqlite3.Row

cur = con.cursor()

streets = set()

def normalise_addr(address):
    if address.lower().split(' ')[0] == 'opp':
        address = address.lower().replace('opp ', '')
    if address.lower().split(' ')[-1] == 'st':
        return address.lower().replace(' st', ' street')
    if address.lower().split(' ')[-1] == 'pl':
        return address.lower().replace(' pl', ' place')
    if address.lower().split(' ')[-1] == 'dr':
        return address.lower().replace(' dr', ' drive')
    if address.lower().split(' ')[-1] == 'ave':
        return address.lower().replace(' ave', ' avenue')
    if address.lower().split(' ')[-1] == 'rd':
        return address.lower().replace(' rd', ' road')
    if address.lower().split(' ')[-1] == 'ln':
        return address.lower().replace(' ln', ' lane')
    if address.lower().split(' ')[-1] == 'cres':
        return address.lower().replace(' cres', ' crescent')
    if address.lower().split(' ')[-1] == 'tce':
        return address.lower().replace(' tce', ' terrace')
    if address.lower().split(' ')[-1] == 'av':
        return address.lower().replace(' av', ' avenue')
    if address.lower().split(' ')[-1] == 'nort':
        return address.lower().replace(' nort', ' north')
    if address.lower().split(' ')[-1] == 'crt':
        return address.lower().replace(' crt', ' court')
    if address.lower().split(' ')[-1] == 'esp':
        return address.lower().replace(' esp', ' esplanade')
    if address.lower().split(' ')[-1] == 'sq':
        return address.lower().replace(' sq', ' square')
    return address.lower()

def get_coords(row):
    if row == '230 SYMONDS ST':
        return -36.8646979, 174.759153
    new_cur = con.cursor()
    clean_row = row.strip()
    addr = normalise_addr(clean_row)
    contains_numbers = any(char.isdigit() for char in addr)
    if contains_numbers:
        addr_num = addr.split(' ')[0]
        addr_body = ' '.join(addr.split(' ')[1:])
        res = new_cur.execute("SELECT * FROM addresses WHERE full_address_number = ? COLLATE NOCASE AND full_road_name = ? COLLATE NOCASE AND town_city = 'Auckland'", (addr_num, addr_body,))
        row = res.fetchone()
        if row is not None:
            return float(row['gd2000_ycoord']), float(row['gd2000_xcoord'])
    if not contains_numbers:
        res = new_cur.execute("SELECT * FROM addresses WHERE full_road_name = ? COLLATE NOCASE AND town_city = 'Auckland'", (addr,))
        row = res.fetchone()
        if row is not None:
            return float(row['gd2000_ycoord']), float(row['gd2000_xcoord'])
    return None

with open('trips.csv', 'w') as csvfile:
    fieldnames = ['originx', 'originy', 'origin', 'destinationx', 'destinationy', 'destination']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    with open('failures.txt', 'w') as file:
        for row in cur.execute("SELECT DISTINCT Destination, Origin FROM events"):
            destination = get_coords(row['Destination'])
            origin = get_coords(row['Origin'])
            if destination is None or origin is None:
                file.write(f"No res for {row['Origin'].strip()} -> {row['Destination'].strip()}\n")
                continue
            print(destination)
            print(origin)
            writer.writerow({
                'originx': origin[0],
                'originy': origin[1],
                'origin': row['Origin'],
                'destinationx': destination[0],
                'destinationy': destination[1],
                'destination': row['Destination'] 
            })
            # print(destination)
            # print(origin)

con.close()