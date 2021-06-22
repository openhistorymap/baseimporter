import shapefile 
import fiona
import os
import json
import requests
import csv

FORMAT = os.environ.get('FORMAT', 'geojson')
URL = os.environ.get('URL')
OHM_SERVER = os.environ.get('OHM_SERVER')
mapping = json.load(open('mapping.json'))

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

rows = []

if FORMAT in ['csv']:
    fin = requests.get(URL)
    with csv.DictReader(fin.content) as cin:
        rows = [{"properties": row} for row in cin.rows]


if FORMAT in ['geojson']:
    fin = requests.get(URL, allow_redirects=True).json()
    #fin = json.load(open('NYC.geojson'))
    rows = fin['features']

if FORMAT in ['shapefile']:
    r = requests.get(URL, allow_redirects=True)
    open('fout', 'wb').write(r.content)


    unlink('fout')



out_list = []

for m in mapping['mappings']:
    print(m)
    out = {}
    if m['filter'] == '*':
        filtered = rows
    else:
        filtered = filter(lambda x: True, rows)
    for r in filtered:
        fout = {"type": "Feature", "geometry": r['geometry'], "properties":{}}
        for f in m['fixed_fields']:
            fout['properties'][f] = m['fixed_fields'][f]
        fout['properties']['layer'] = m['target_layer']
        for f in m['mapped_fields']:
            if f in r['properties']:
                for mf1 in m['mapped_fields'][f]:
                    fout['properties'][mf1['to']] = float(r['properties'][f])
        out_list.append(fout)

for chunk in divide_chunks(out_list, 100):
    print('sending 100')
    requests.post(OHM_SERVER+'/items', json=chunk )
        
