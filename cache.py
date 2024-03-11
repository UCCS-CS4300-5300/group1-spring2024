import requests
import requests_cache
from datetime import datetime
from geopy.geocoders import Nominatim
import os
# Enable caching
requests_cache.install_cache('weather_cache', expire_after=3600)  # Cache expires after 1 hour

# Maps API is Nomination OpenSource



def get_location():
  app = Nominatim(user_agent="Weather App")
  location_input = input("Enter your location: ")

  location = app.geocode(location_input)

  latitude = location.latitude
  longitude = location.longitude

  return latitude, longitude

def get_hourly_weather_report(latitude, longitude):
    base_url = "https://api.weather.gov/points/{},{}".format(latitude, longitude)

    # Fetching forecast data
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Failed to fetch data from API")
        return

    data = response.json()
    forecast_url = data["properties"]["forecastHourly"]

    # Fetching hourly forecast data
    response = requests.get(forecast_url)
    if response.status_code != 200:
        print("Failed to fetch forecast data from API")
        return

    forecast_data = response.json()

    # Extracting and printing hourly weather report
    print("Hourly Weather Report for {}, {}".format(data["properties"]["relativeLocation"]["properties"]["city"],
                                                   data["properties"]["relativeLocation"]["properties"]["state"]))
    print("-" * 50)

    for forecast in forecast_data["properties"]["periods"]:
        forecast_time = datetime.strptime(forecast["startTime"], "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M")
        print("{}: {}".format(forecast_time, forecast["shortForecast"]))

latitude, longitude = get_location()
get_hourly_weather_report(latitude, longitude)
