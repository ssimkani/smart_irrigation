# import openmeteo_requests

# import pandas as pd
# import requests_cache
# from retry_requests import retry

# # Setup the Open-Meteo API client with cache and retry on error
# cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
# retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
# openmeteo = openmeteo_requests.Client(session = retry_session)

# # Make sure all required weather variables are listed here
# # The order of variables in hourly or daily is important to assign them correctly below
# url = "https://api.open-meteo.com/v1/forecast"
# params = {
# 	"latitude": 42.27075250858827,
# 	"longitude": -83.58226485882234,
# 	"hourly": ["soil_moisture_1_to_3cm", "precipitation", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "soil_moisture_0_to_1cm"],
# }
# responses = openmeteo.weather_api(url, params=params)

# # Process first location. Add a for-loop for multiple locations or weather models
# response = responses[0]
# print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
# print(f"Elevation: {response.Elevation()} m asl")
# print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# # Process hourly data. The order of variables needs to be the same as requested.
# hourly = response.Hourly()
# hourly_soil_moisture_1_to_3cm = hourly.Variables(0).ValuesAsNumpy()
# hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
# hourly_soil_moisture_3_to_9cm = hourly.Variables(3).ValuesAsNumpy()
# hourly_soil_moisture_9_to_27cm = hourly.Variables(4).ValuesAsNumpy()
# hourly_soil_moisture_0_to_1cm = hourly.Variables(5).ValuesAsNumpy()

# hourly_data = {"date": pd.date_range(
# 	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
# 	end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
# 	freq = pd.Timedelta(seconds = hourly.Interval()),
# 	inclusive = "left"
# )}
# average_soil_moisture = (hourly_soil_moisture_1_to_3cm + hourly_soil_moisture_3_to_9cm + hourly_soil_moisture_0_to_1cm + hourly_soil_moisture_9_to_27cm) / 4
# hourly_data["soil_moisture(m^3/m^3)"] = average_soil_moisture
# hourly_data["precipitation"] = hourly_precipitation

# hourly_dataframe = pd.DataFrame(data = hourly_data)
# print("\nHourly data\n", hourly_dataframe)


# hourly_dataframe.to_csv("./data.csv")

import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 42.27075250858827,
	"longitude": -83.58226485882234,
	"hourly": ["soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "precipitation"],
	"timezone": "auto",
	"start_date": "2025-11-26",
	"end_date": "2026-03-14",
}

from datetime import date

ALLOWED_MIN = date(2025, 12, 19)
ALLOWED_MAX = date(2026, 3, 3)

start = max(date.fromisoformat(params["start_date"]), ALLOWED_MIN)
end   = min(date.fromisoformat(params["end_date"]),   ALLOWED_MAX)

params["start_date"] = start.isoformat()
params["end_date"]   = end.isoformat()

responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_soil_moisture_0_to_1cm = hourly.Variables(0).ValuesAsNumpy()
hourly_soil_moisture_1_to_3cm = hourly.Variables(1).ValuesAsNumpy()
hourly_soil_moisture_3_to_9cm = hourly.Variables(2).ValuesAsNumpy()
hourly_soil_moisture_9_to_27cm = hourly.Variables(3).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
	end =  pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

average_soil_moisture = (hourly_soil_moisture_1_to_3cm + hourly_soil_moisture_3_to_9cm + hourly_soil_moisture_0_to_1cm + hourly_soil_moisture_9_to_27cm) / 4
hourly_data["soil_moisture(m^3/m^3)"] = average_soil_moisture
hourly_data["precipitation"] = hourly_precipitation

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("\nHourly data\n", hourly_dataframe)

hourly_dataframe.to_csv("./data.csv")