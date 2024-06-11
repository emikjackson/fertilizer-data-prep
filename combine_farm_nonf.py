# Data source: https://www.sciencebase.gov/catalog/item/5ebad56382ce25b51361806a

# Since only total data is available from the 1950-1982 time period as a combination of nonfarm and farm uses
# (see https://pubs.usgs.gov/of/2020/1153/ofr20201153.pdf page 3),
# we want to also provide a total estimate for total fertilizer usage for 1987 - 2017 period
# by combining the farm and nonfarm estimates.

import csv
import re

# Year fields can be itentified by ending in 4 digits
def is_year_field(field):
   return re.match('^.*(\d{4}|-)$', field)


# Return array of field names for 'total' csv columns, initialized from farm fields 
def convert_farm_fields_to_total(farm_fields):
  total_fields = []
  for field in farm_fields:
      # For year fields (e.g. 'farmfertN-kg-1987'), swap 'farm' with 'total'
      if is_year_field(field):
          total_fields.append(field.replace('farm', 'total'))
      else:
          total_fields.append(field)
  return total_fields



# Combine farm and nonfarm csvs into total csv
def combine_farm_nonf(farm_input_file, nonf_input_file, output_file):
  farm_fert_data_by_geoid = {}
  total_rows = []
  total_fields = None # column names for total csv

  # Create dictionary of farm fertilizer data keyed by GEOID/'STCOFIPS'
  with open(farm_input_file, encoding='utf-8') as csvf:
    csv_reader = csv.DictReader(csvf)
    for row in csv_reader:
        # Key on the FIPS ("GEOID" in counties data)
        farm_fert_data_by_geoid[row['STCOFIPS']] = row

  # Convert farm field names to total field names and save them
  with open(farm_input_file, encoding='utf-8') as csvf:
    csv_reader = csv.DictReader(csvf)
    csv_dict = dict(list(csv_reader)[0])
    total_fields = convert_farm_fields_to_total(csv_dict.keys())


  # Loop through the nonfarm input, combining with farm input and outputting to total output
  with open(nonf_input_file, encoding='utf-8') as csvf:
    empty_count = 0
    csv_reader = csv.DictReader(csvf)
    for nonf_row in csv_reader:
        farm_row = farm_fert_data_by_geoid[nonf_row['STCOFIPS']]
        total_row = dict.fromkeys(total_fields)

        # Copy values over to total row dictionary.
        # For year values, combine the farm and nonfarm values to create the total
        for farm_key in farm_row:
            total_key = farm_key
            total_value = farm_row[farm_key]

            if is_year_field(farm_key):
                nonf_key = farm_key.replace('farm', 'nonf')
                total_key = farm_key.replace('farm', 'total')
                if farm_row[farm_key] != '' and nonf_row[nonf_key] != '':
                  total_value = int(farm_row[farm_key]) + int(nonf_row[nonf_key])
                else:
                  total_value = ''
                  empty_count += 1
            total_row[total_key] = total_value
        
        total_rows.append(total_row)
    print("Couldn't add values for # rows:", empty_count)

    # Write total rows to total output csv
    with open(output_file, "w") as f:
        csv_writer = csv.DictWriter(f, total_fields)
        csv_writer.writeheader()
        csv_writer.writerows(total_rows)

combine_farm_nonf('fert-farm-1987-2017.txt', 'fert-nonfarm-1987-2017.txt', 'fert-total-1987-2017.txt')