import csv
import json
import re

# Fields in the fertilizer data that are already represented in the county level data
UNNECESSARY_KEYS_TO_TRANSFER = ['STCOFIPS', 'fips-int', 'CountyName']

def remove_unnecessary_keys(dict):
    for key in UNNECESSARY_KEYS_TO_TRANSFER:
        dict.pop(key, None)
    return dict

# Check fertilizer amount value against current max & mins, updating when needed
def update_max_mins(val, data_max_mins, key):
    summary_type = 'farm'
    fert_type = 'P'
    if 'nonf' in key:
        summary_type = 'nonf'
    elif 'total' in key:
        summary_type = 'total'
    if 'N' in key:
        fert_type = 'N'
    if data_max_mins[summary_type][fert_type]['min'] > val:
        data_max_mins[summary_type][fert_type]['min'] = val
    if data_max_mins[summary_type][fert_type]['max'] < val:
        data_max_mins[summary_type][fert_type]['max'] = val
    return data_max_mins

# Convert fertilizer year data value strings to integers, remove unnecessary keys, and track data max & mins
def prep_fertilizer_properties(dict, data_max_mins, data_years):
    fert_dict = remove_unnecessary_keys(dict)

    for key in fert_dict:
        # If this is a year data property (string ending in 4 digits, e.g. "farmN1988") ... 
        if re.match('^.*(\d{4}|-)$', key):
            data_years.add(key[-4:]) # year is last four characters
            # Convert the property value to a number
            if fert_dict[key] != '':
                int_value = int(fert_dict[key])
                fert_dict[key] = int_value
                # Check if this value is a min or max for dataset, updating dictionary if so
                data_max_mins = update_max_mins(int_value, data_max_mins, key)
            else:
                fert_dict[key] = 'N/A'
    return [fert_dict, data_max_mins, data_years]

# Get dictionary of maxs and mins for each summary type / fertilizer type combination
def get_initialized_max_mins():
    min_max = {
        'max': -1,
        'min': float('inf')
    }
    return {
        'total': {
            'P': dict(min_max),
            'N': dict(min_max)
        },
        'farm': {
            'P': dict(min_max),
            'N': dict(min_max)
        },
        'nonf': {
            'P': dict(min_max),
            'N': dict(min_max)
        }
    }         

# Populate counties geoJSON with yearly fertilizer data from fertilizer CSV
# CSV to JSON code from https://www.geeksforgeeks.org/convert-csv-to-json-using-python/
def create_combined_geojson(counties_input_file, fertilizer_input_files, data_output_file, summary_output_file):
    
    # For displaying our colors, create dict to note max & mins for each fertilizer.
    data_max_mins = get_initialized_max_mins()
     
    # 1. Create dictionary keyed by FIPS/GEOID and initialize summary data holders
    fert_data_by_geoid = {}
    missing_geoids = set([])
    data_years = set([])

    # 2. Load counties geoJSON file
    geojson_file = open(counties_input_file)
    counties_geojson = json.load(geojson_file)
     
    for fertilizer_file in fertilizer_input_files:
      # Populate dictionary with CSV data
      with open(fertilizer_file, encoding='utf-8') as csvf:
          csv_reader = csv.DictReader(csvf)
          for row in csv_reader:
              # Key on the FIPS ("GEOID" in counties data)
              fert_data_by_geoid[row['STCOFIPS']] = row

      # Using 'fert_data_by_geoid', add fetilizer data to counties geoJSON
      for index, feature in enumerate(counties_geojson['features']):
          # Fetch properties & GEOID
          existing_properties = feature['properties']
          geoid = existing_properties['GEOID']

          # Get data from fertilizer dictionary to add to county geoJSON
          if (geoid in fert_data_by_geoid):
              prep_results = prep_fertilizer_properties(fert_data_by_geoid[geoid], data_max_mins, data_years)
              properties_to_transfer = prep_results[0]
              data_max_mins = prep_results[1]
              data_years = prep_results[2]
              # Add fert data to county geoJSON properties dictionary
              new_properties = existing_properties | properties_to_transfer
              # Write new properties to parent object
              counties_geojson['features'][index]['properties'] = new_properties
          else:
              missing_geoids.add(geoid)

    # Write geojson data to output file
    with open(data_output_file, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(counties_geojson))

    data_summary = {
        'max_mins': data_max_mins,
        'years': list(data_years),
        'missing_geoids': list(missing_geoids),
        'missing_geoids_len': len(missing_geoids)
    }

    # Write data summary to output file
    with open(summary_output_file, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data_summary))

# Call function to combine counties geojson with fertilizer CSV data
# Will write output to 'counties_with_fertilizer.json' and 'counties_with_fertilizer_summary.json'
fertilizer_input_files = ['fert-farm-1987-2017.txt', 'fert-nonfarm-1987-2017.txt', 'fert-total-1987-2017.txt',  'fert-total-1950-1982-standardized.txt']
create_combined_geojson('counties_filtered.json', fertilizer_input_files, 'counties_with_fertilizer.json', 'counties_with_fertilizer_summary.json')
