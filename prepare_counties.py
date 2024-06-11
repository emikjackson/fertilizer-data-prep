# Remove states that are not part of the fertilizer study from counties geoJSON

import json

HAWAII_FP = '15'
ALASKA_FP = '02'

def prepare_counties(counties_input, counties_output):
    geojson_file = open(counties_input)
    counties_geojson = json.load(geojson_file)
    filtered_counties_geojson = dict(counties_geojson)
    filtered_features = []

    # Loop through features and only add features in continguous US
    for feature in counties_geojson['features']:
        if (feature['properties']['STATEFP'] not in [HAWAII_FP, ALASKA_FP]):
            filtered_features.append(feature)

    filtered_counties_geojson['features'] = filtered_features

    # Write filtered geoJSON to new file
    with open(counties_output, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(filtered_counties_geojson))


prepare_counties('counties.json', 'counties_filtered.json')