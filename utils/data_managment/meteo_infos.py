import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"

def get_meteo (lat, long, date_start, date_stop):
    """
    Get meteo informations from open-meteo API
    """
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": date_start,
        "end_date": date_stop,
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", 
                   "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", 
                   "et0_fao_evapotranspiration", "soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm", 
                   "soil_temperature_28_to_100cm", "soil_temperature_100_to_255cm", "soil_moisture_0_to_7cm", 
                   "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm", "soil_moisture_100_to_255cm", "is_day", 
                   "sunshine_duration"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation {response.Elevation()} m asl")
    # print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
    hourly_rain = hourly.Variables(3).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
    hourly_cloud_cover_low = hourly.Variables(5).ValuesAsNumpy()
    hourly_cloud_cover_mid = hourly.Variables(6).ValuesAsNumpy()
    hourly_cloud_cover_high = hourly.Variables(7).ValuesAsNumpy()
    hourly_et0_fao_evapotranspiration = hourly.Variables(8).ValuesAsNumpy()
    hourly_soil_temperature_0_to_7cm = hourly.Variables(9).ValuesAsNumpy()
    hourly_soil_temperature_7_to_28cm = hourly.Variables(10).ValuesAsNumpy()
    hourly_soil_temperature_28_to_100cm = hourly.Variables(11).ValuesAsNumpy()
    hourly_soil_temperature_100_to_255cm = hourly.Variables(12).ValuesAsNumpy()
    hourly_soil_moisture_0_to_7cm = hourly.Variables(13).ValuesAsNumpy()
    hourly_soil_moisture_7_to_28cm = hourly.Variables(14).ValuesAsNumpy()
    hourly_soil_moisture_28_to_100cm = hourly.Variables(15).ValuesAsNumpy()
    hourly_soil_moisture_100_to_255cm = hourly.Variables(16).ValuesAsNumpy()
    hourly_is_day = hourly.Variables(17).ValuesAsNumpy()
    hourly_sunshine_duration = hourly.Variables(18).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["rain"] = hourly_rain
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
    hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
    hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
    hourly_data["et0_fao_evapotranspiration"] = hourly_et0_fao_evapotranspiration
    hourly_data["soil_temperature_0_to_7cm"] = hourly_soil_temperature_0_to_7cm
    hourly_data["soil_temperature_7_to_28cm"] = hourly_soil_temperature_7_to_28cm
    hourly_data["soil_temperature_28_to_100cm"] = hourly_soil_temperature_28_to_100cm
    hourly_data["soil_temperature_100_to_255cm"] = hourly_soil_temperature_100_to_255cm
    hourly_data["soil_moisture_0_to_7cm"] = hourly_soil_moisture_0_to_7cm
    hourly_data["soil_moisture_7_to_28cm"] = hourly_soil_moisture_7_to_28cm
    hourly_data["soil_moisture_28_to_100cm"] = hourly_soil_moisture_28_to_100cm
    hourly_data["soil_moisture_100_to_255cm"] = hourly_soil_moisture_100_to_255cm
    hourly_data["is_day"] = hourly_is_day
    hourly_data["sunshine_duration"] = hourly_sunshine_duration

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    return hourly_dataframe
