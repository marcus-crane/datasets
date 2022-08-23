import sqlite3
import sys

import pandas as pd

workbook = pd.ExcelFile("towing.xlsx")
df = pd.DataFrame()

print('Parsing sheets')
for sheet_name in workbook.sheet_names:
    sheet = workbook.parse(sheet_name=sheet_name)
    df = df.append(sheet, sort=False)

# Let's get rid of the unused columns
print('Dropping unused columns')
df = df.drop(
        columns=[
            'Unnamed: 0',
            'Unnamed: 6',
            'Unnamed: 7',
            'Unnamed: 8',
            'Unnamed: 9',
            'Unnamed: 10'
        ]
    )

# and we'll give the remaining ones more sensible names
print('Renaming remaining columns')
df = df.rename(
        columns={
            'Unnamed: 5': 'Suburb',
            'Date and Time ': 'Date',
            'Towed From ': 'Origin',
            'Towed Too ': 'Destination',
            'Vehicle ': 'Vehicle'
        }
    )

# Let's also give the suburbs human readable names
print('Humanising suburbs')
df['Suburb'] = df['Suburb'].replace(55, 'CENTRAL')
df['Suburb'] = df['Suburb'].replace(66, 'NORTHERN')
df['Suburb'] = df['Suburb'].replace(77, 'WESTERN')
df['Suburb'] = df['Suburb'].replace(88, 'SOUTHERN')
df['Suburb'] = df['Suburb'].replace(99, 'CBD')
df['Suburb'] = df['Suburb'].replace('Romeo', 'RURAL')
df['Suburb'] = df['Suburb'].replace('Romeo ', 'RURAL')
df['Suburb'] = df['Suburb'].replace('ROMEO', 'RURAL')

# Data fixes
# """
print('Applying data fixes')
df = df.replace('Sunda, 28 Aug 2016', 'Sunday, 28 Aug 2016')
df = df.replace('Satruday, 06 Jan 2017', 'Saturday, 06 Jan 2017')
df = df.replace('Tuesday, 28th Nov ', 'Tuesday, 28 Nov 2017')
df = df.replace('4.40pm', '4:40pm')
df = df.replace('5.08pm', '5:08pm')
df = df.replace('14:55 pm', '2:55pm')
df = df.replace('4.37 p.m.', '4:37pm')
df = df.replace('17:01 p.m', '5:01pm')
df = df.replace('4.22 p.m.', '4:22pm')
df = df.replace('4.32 p.m.', '4:32pm')
# """

required_data_fixes = []
current_date = ''

print('Restructuring dataset for easier parsing')
for idx, entry in enumerate(df['Date']):
    item = str(entry)

    if 'day' in item:
        current_date = item
    if 'day' not in item and item != 'nan':
        try:
            df.iloc[idx]['Date'] = pd.to_datetime(f'{current_date} {item}')
        except Exception:
            required_data_fixes.append(idx)

if required_data_fixes:
    print('Data fixes are required for the following locations')
    for defect in required_data_fixes:
        print(f'Index {defect}: {df.iloc[defect]["Date"]}')
    sys.exit()

print('Dropping empty cells')
df = df.dropna()

"""
print('Trimming excess whitespace')
df['Origin'] = df['Origin'].str.strip()
df['Destination'] = df['Destination'].str.strip()
"""

print('Setting timestamp as dataframe index')
df = df.set_index('Date')

with sqlite3.connect('towing.db') as conn:
    print('Exporting dataset to sqlite file')
    df.to_sql('events', conn)
