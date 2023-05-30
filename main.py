import hydrofunctions as hf
import csv
import pandas as pd

data_file = 'stations_impervious_surface.csv'
start_date = "2017-01-01"
end_date = "2021-01-01"
parameter_id = "00095"

# Read station data from CSV
station_data = pd.read_csv(data_file, dtype={'Station ID': str})

location_ids = station_data['Station ID'].tolist()
city_imperv = station_data['Impervious Surface Percentage'].tolist()

compiled_data = []
csv_data = []

number_to_keep = 10000
number_in_result = 0

for location_id in location_ids:
    if number_in_result >= number_to_keep:
        break

    print("Trying site with ID " + location_id)
    try:
        data = hf.NWIS(location_id, "iv", start_date, end_date)
        compiled_data.append(data)
        median = data.df(parameter_id)[f'USGS:{location_id}:{parameter_id}:00000'].median()

        index = location_ids.index(location_id)
        imperv = city_imperv[index]

        csv_data.append({'Station ID': location_id, 'Impervious Surface Percentage': float(imperv), 'Median Conductivity': float(median)})

        number_in_result += 1
        print("Successfully found data!")
        print(str(number_in_result) + "/" + str(number_to_keep))
    except (hf.HydroNoDataError, ValueError):
        print("No data for this point")


csv_filename = 'dataset.csv'

with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['Station ID', 'Impervious Surface Percentage', 'Median Conductivity']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(csv_data)

print(f"Data saved to {csv_filename}")
