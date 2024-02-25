from django.db import models
from geopy.geocoders import Nominatim
import requests
from datetime import datetime


class Location(models.Model):
  name = models.CharField(max_length=30)

  def __str__(self):
    return self.name


class Weather(models.Model):

  location = models.ForeignKey(Location, on_delete=models.CASCADE)
  temperature = models.FloatField()
  humidity = models.IntegerField()  # Convert to percentage later
  wind_speed = models.FloatField()
  temperature_description = models.CharField(max_length=100)
  image = models.ImageField(upload_to='weather_images')
  date = models.DateTimeField()

  def __str__(self):
    return str(self.location)

  def _get_weather(latitude, longitude):
    """
    Leverages api.weather.gov, a free weather API providing forecasting services. URL: https://www.weather.gov/documentation/services-web-api
    Gets the 3 letter station closest to the user's location (location_data), and then calls that station to get the local forecast hourly (weather_data). 

    Example return of the function:

    "periods": [
    {
      "number": 1,
      "name": "",
      "startTime": "2024-02-24T18:00:00-07:00",
      "endTime": "2024-02-24T19:00:00-07:00",
      "isDaytime": false,
      "temperature": 54,
      "temperatureUnit": "F",
      "temperatureTrend": null,
      "probabilityOfPrecipitation": {
        "unitCode": "wmoUnit:percent",
        "value": 0
      },
      "dewpoint": {
        "unitCode": "wmoUnit:degC",
        "value": -11.666666666666666
      },
      "relativeHumidity": {
        "unitCode": "wmoUnit:percent",
        "value": 18
      },
      "windSpeed": "10 mph",
      "windDirection": "WNW",
      "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
      "shortForecast": "Mostly Cloudy",
      "detailedForecast": ""
    },
    """

    base_url = f"https://api.weather.gov/points/{latitude},{longitude}"
    location_response = requests.get(base_url)
    location_data = location_response.json()

    weather_response = requests.get(
        location_data['properties']['forecastHourly'])
    weather_data = weather_response.json()
    return weather_data["properties"]["periods"]  # the actual weather forecast

  def _format_response(weather_data):
    """
    Takes a format such as:

    "periods": [
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T18:00:00-07:00",
        "endTime": "2024-02-24T19:00:00-07:00",
        "isDaytime": false,
        "temperature": 54,
        "temperatureUnit": "F",
        "temperatureTrend": null,
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 0
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 18
        },
        "windSpeed": "10 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      },

    And converts it to:

    result = {
      "hours": [1-24],
      "temperature": [],
      "precipitation": [],
      "humidity": [],
      "wind": []
    }

    """

    hours = [
        datetime.fromisoformat(start_time["startTime"]).hour
        for start_time in weather_data
    ]
    temperature = [temp["temperature"] for temp in weather_data]
    precipitation = [
        prec["probabilityOfPrecipitation"]["value"] for prec in weather_data
    ]
    humidity = [humid["relativeHumidity"]["value"] for humid in weather_data]
    windSpeed = [
        windSpeed["windSpeed"].split(" ")[0] for windSpeed in weather_data
    ]

    result = {
        "hours": hours,
        "temperature": temperature,
        "precipitation": precipitation,
        "humidity": humidity,
        "wind": windSpeed
    }

    return result

  @staticmethod  # similar to static methods
  def get_weather_forecast(location):
    """
    Gets the hourly forecast for the next 24 hours based on the user's location, or defaults to UCCS main campus if none provided.
    """
    
    #Maps API is Nomination OpenSource
    #https://nominatim.org

    # Instantiate a new Nominatim client
    app = Nominatim(user_agent="Weather App")

    location_input = "80918" if not location else location  # 80918 is UCCS main campus

    # Get location raw data from the user
    location = app.geocode(location_input)
    if location:
      latitude = location.latitude
      longitude = location.longitude

      weather_data = Weather._get_weather(latitude, longitude)
      if weather_data:
        result = Weather._format_response(weather_data)
        return result
    return None
