from django.db import models
from geopy.geocoders import Nominatim
import requests
from datetime import datetime
from django.core import validators


# https://docs.djangoproject.com/en/5.0/howto/initial-data/#:~:text=You%20can%20load%20data%20by,and%20reloaded%20into%20the%20database to populate the list of generic clothes
# Must be loaded manually using python manage.py loaddata fixture_generic_clothes.json
# Credit to ChatGPT for generating the fixtures
class GenericClothes(models.Model):
  """
  A class holding information relating to generic clothing, such as t-shirt, cargo pants, jeans, etc. 
  The fields are broken into: 
  1. the type of clothing (headwear, shirts, pants, shoes, misc. for umbrellas or anything I missed)
  2. a comfort range based on the type of clothing (e.g. jeans, cargo pants, etc.) and a custom comfort calculation as follows:

  Comfort = {HI, T > 75, WC, T <= 75} - TOLERANCE_offset + WORKING_offset
  HI = 0.5 * {T + 61.0 + [(T-68.0)1.2] + (RH * 0.094)}
  WC = 35.74 + 0.6215T - 35.75v^{0.16} + 0.4275Tv^{0.16}, where v is the wind speed in MPH
  
  3. a waterproof rating.
  """

  # Enforces the category of clothing with choices, https://docs.djangoproject.com/en/5.0/ref/models/fields/#charfield
  CLOTHE_CHOICES = [
      ("HAT", "Hat"),
      ("SHR", "Shirts and Jackets"),
      ("PNT", "Pants"),
      ("SHO", "Shoes"),
      ("MIS", "Miscellaneous")
  ]


  name = models.CharField(max_length=50)
  clothing_type = models.CharField(max_length=3, choices=CLOTHE_CHOICES)
  comfort_low = models.IntegerField()
  comfort_high = models.IntegerField()
  waterproof_rating = models.IntegerField()  # percentage from 1-100

  def __str__(self):
    return self.name

  def clean(self, *args, **kwargs):
    """
    Django’s form (and model) fields support use of utility functions and classes known as validators. A validator is a callable object or function that takes a value and returns nothing if the value is valid or raises a ValidationError if not - https://docs.djangoproject.com/en/5.0/ref/validators/

    Here, we ensure that the comfort low is not greater than the high
    """
    super().clean(
        *args, **kwargs
    )  # see https://stackoverflow.com/questions/7366363/adding-custom-django-model-validation

    if self.comfort_low >= self.comfort_high:
      raise validators.ValidationError(
          "Comfort low must be less than or equal to comfort high.")

  @classmethod
  def calculate_comfort(cls, temperature, humidity, wind_speed,
                        tolerance_offset, working_offset):
    """
    Calculate the comfort level based on the temperature, humidity, and wind speed. Less of a comfort calculation and more of a adjusted feels-like temperature.

    Params:
    * Temperature in farenheit
    * Humidity in percentage from 0-100+ (technically humidity can go beyond 100%)
    * Wind speed in miles per hour
    """

    if humidity < 0:
      raise ValueError("Humidity must be greater than or equal to 0.")

    if wind_speed < 0:
      raise ValueError("Wind speed must be greater than or equal to 0.")

    if working_offset < 0:
      raise ValueError("Working offset must be greater than or equal to 0.")

    # Calculate the adjusted feels-like temperature
    if temperature > 75:
      # equation from https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
      heat_index = -42.379 + 2.04901523 * temperature + 10.14333127 * humidity - 0.22475541 * temperature * humidity - 0.00683783 * temperature * temperature - 0.05481717 * humidity * humidity + 0.00122874 * temperature * temperature * humidity + 0.00085282 * temperature * humidity * humidity - 0.00000199 * temperature * temperature * humidity * humidity
      return heat_index - tolerance_offset + working_offset

    # If the temperature is less than or equal to 75, use the wind chill
    else:
      # equation from https://en.wikipedia.org/wiki/Wind_chill NA wind chill index
      wind_chill = 35.74 + 0.6215 * temperature - 35.75 * (
          wind_speed**0.16) + 0.4275 * temperature * (wind_speed**0.16)
      return wind_chill - tolerance_offset + working_offset

  @classmethod
  def get_clothes_in_range(cls, comfort):
    """
    Function that, given a comfort value, iterates through the current clothes in the database and returns the first set of clothes that are within the comfort range.

    Comfort should be in range -460 (absolute zero) and 6100 (melting point of tungsten)

    Currently does not include an umbrella or waterproofing.
    """

    if comfort < -460 or comfort > 6100:
      raise ValueError(
          "Comfort must be in range -460 (absolute zero) and 6100 (melting point of tungsten)."
      )

    # comfort_low <= comfort <= comfort_high
    clothes = cls.objects.filter(comfort_low__lte=comfort,
                                 comfort_high__gte=comfort)
    # build the outfit, little bit of metaprogramming / syntactic sugar
    try:
      outfit = [
          clothes.filter(clothing_type=query)[0]
          for query in ["HAT", "SHR", "PNT", "SHO"]
      ]
    except:  # [0] throws error when filter returns nothing
      outfit = []

    return outfit


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

    if('status' not in location_data):
      weather_response = requests.get(
          location_data['properties']['forecastHourly'])
      weather_data = weather_response.json()
      return weather_data["properties"]["periods"]  # the actual weather forecast
    else:
      return None

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
        int(windSpeed["windSpeed"].split(" ")[0]) for windSpeed in weather_data
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
      else:
        return None
    return None
