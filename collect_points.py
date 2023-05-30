import geopandas as gpd
import pandas as pd
import random
import requests
from shapely.geometry import Point

# Set the CRS explicitly
data_file = 'resources/IMPERVIOUS HUC-12.gpkg'
state_codes_file = 'resources/state_codes.txt'
parameter_id = '00095'


def get_usgs_stations_state(state_code):
    url = f'https://waterservices.usgs.gov/nwis/iv/?stateCd={state_code}&format=json'
    response = requests.get(url)
    data = response.json()
    stations = []

    for site in data['value']['timeSeries']:
        if parameter_id in site['variable']['variableCode'][0]['value']:
            station_id = site['sourceInfo']['siteCode'][0]['value']
            latitude = site['sourceInfo']['geoLocation']['geogLocation']['latitude']
            longitude = site['sourceInfo']['geoLocation']['geogLocation']['longitude']
            stations.append({'Station ID': station_id, 'Latitude': latitude, 'Longitude': longitude})

    return stations


def get_usgs_stations(sample_size):
    with open('resources/state_codes.txt', 'r') as file:
        state_codes = file.read().splitlines()

    stations = []

    for index, state_code in enumerate(state_codes):
        print(f"Processing state: {state_code} ({index + 1}/{len(state_codes)})")
        stations_state = get_usgs_stations_state(state_code)
        stations.extend(stations_state)
        print(f"Finished state: {state_code} ({index + 1}/{len(state_codes)})")

    return random.sample(stations, sample_size)


def get_impervious_surface_percentage(watershed_polygon):
    return watershed_polygon['_mean']


def main():
    sample_size = 1300
    stations = get_usgs_stations(sample_size)

    data = gpd.read_file(data_file, layer='zonal_statistics')

    csv_data = []

    for index, station in enumerate(stations):
        latitude = station['Latitude']
        longitude = station['Longitude']

        point = gpd.GeoSeries([Point(longitude, latitude)], crs='EPSG:4326')
        point = point.to_crs(data.crs)

        print(f"Processing station {index + 1}/{len(stations)}")

        for _, row in data.iterrows():
            if row.geometry.contains(point[0]):
                impervious_surface_percentage = get_impervious_surface_percentage(row)
                csv_data.append({
                    'Station ID': station['Station ID'],
                    'Latitude': latitude,
                    'Longitude': longitude,
                    'Impervious Surface Percentage': float(impervious_surface_percentage)/100
                })
                break

    csv_df = pd.DataFrame(csv_data)
    csv_df.to_csv('stations_impervious_surface.csv', index=False)
    print("CSV file generated successfully.")


if __name__ == '__main__':
    main()
