# Fertilizer Data Prep

Python scripts to prepare data for fertilizer map application.

## Sources

### Fertilizer Data (fertilizer estimates from 1950-2017 in contiguous U.S., 5 year periods)

https://www.sciencebase.gov/catalog/item/5ebad56382ce25b51361806a

### Counties Shapefile

https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.2018.html#list-tab-1556094155

## Scripts

1. `prepare_counties.py` filters counties geoJSON (`data/counties.json`) to only counties in contiguous United States.
2. `combine_farm_nonf.py` creates a `fert-total-1987-2017.txt` file by adding the nonfarm and farm fertilizer usage metrics from the same time period.
3. `create_geojson.py` combines all relevant fertilizer data sources and the filtered counties geoJSON into a single geoJSON with the fertilizer properties available by county for use in Leaflet map.

## Notes

- `fert-total-1950-1982-standardized.txt` is the same as `fert-total-1950-1982.txt` except column have been reformatted to match `totalfert<F>-kg-<year>` format.
