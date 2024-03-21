from geopy.geocoders import Nominatim
from pprint import pprint
import requests
import os
#Maps API is Nomination OpenSource
#https://nominatim.org

# Instantiate a new Nominatim client
app = Nominatim(user_agent="Weather App")

# Get location raw data from the user
your_loc = input("Enter your location: ")
location = app.geocode(your_loc)

# latitude longitude
latitude = location.latitude
longitude = location.longitude

#weather data Weatherbit free tier
#https://www.weatherbit.io/api/weather-current
api_key = "c8d6780e0157465998a469c3a9cd7b5e"


def get_weather(api_key, latitude, longitude):
  #base_url = "https://api.weatherbit.io/v2.0/forcast/daily"
  #above code is for the daily forcast which is paid
  base_url = "https://api.weatherbit.io/v2.0/current"
  params = {"lat": latitude, "lon": longitude, "key": api_key}
  response = requests.get(base_url, params=params)
  weather_data = response.json()
  return weather_data


result = get_weather(api_key, latitude, longitude)
print(result)

# test
