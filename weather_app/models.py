from datetime import date, datetime
import random
import requests
import requests_cache
from django.core import validators
from django.db import models
from django.urls import reverse
from geopy.geocoders import Nominatim
from django_resized import ResizedImageField
from .utils import calculate_heat_index, calculate_windchill

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

  I am not putting a color parameter in the GenericClothes model since they can be any color. 
  """

  # Enforces the category of clothing with choices, https://docs.djangoproject.com/en/5.0/ref/models/fields/#charfield
  CLOTHE_CHOICES = [("HAT", "Hat"), ("SHR", "Shirts and Jackets"),
                    ("PNT", "Pants"), ("SHO", "Shoes"),
                    ("MIS", "Miscellaneous")]

  name = models.CharField(max_length=50)
  clothing_type = models.CharField(max_length=3, choices=CLOTHE_CHOICES)
  comfort_low = models.IntegerField()
  comfort_high = models.IntegerField()
  waterproof_rating = models.IntegerField()  # percentage from 1-100
  image = ResizedImageField(size=[300, 300], upload_to='generic_clothes', blank=True)
  photo = models.ImageField(upload_to='inventory/photos/')
  image_url = models.CharField(max_length=500, blank='True')

  def __str__(self):
    return self.name

  
  def clean(self, *args, **kwargs):
    """
    Here, we ensure that the comfort low is not greater than the high
    """
    # see https://stackoverflow.com/questions/7366363/adding-custom-django-model-validation
    super().clean(*args, **kwargs)  

    if self.comfort_low >= self.comfort_high:
      raise validators.ValidationError(
          "Comfort low must be less than or equal to comfort high.")

  
  def save(self, *args, **kwargs):
    """
    Here, we set default images based on the clothing types. Based on 
    https://stackoverflow.com/questions/34128251/how-to-pass-django-model-field-value-as-an-argument-to-callable-which-is-default.
    """

    default_clothe_image = {
      "HAT": "generic_clothes/default-hat.png",
      "PNT": "generic_clothes/default-pants.png",
      "SHR": "generic_clothes/default-shirt.png",
      "SHO": "generic_clothes/default-shoe.png",
      "MIS": "generic_clothes/default.png"
    }
    
    if not self.pk:  # if object is new
      self.image.name = default_clothe_image[str(self.clothing_type)]
      super().save(*args, **kwargs)

  
  @classmethod
  def _calculate_comfort(cls, temperature, humidity, wind_speed,
                         tolerance_offset, working_offset):
    """
    Calculate the comfort level based on the temperature, humidity, and wind speed. Less of a comfort calculation and more of a adjusted feels-like temperature.

    Params:
    * Temperature in farenheit
    * Humidity in percentage from 0-100+ (technically humidity can go beyond 100%)
    * Wind speed in miles per hour

    Returns the adjusted feels-like temperature in farenheit.
    """

    if working_offset < 0:
      raise ValueError("Working offset must be greater than or equal to 0.")

    # Calculate the adjusted 'feels-like' temperature
    if temperature > 75:
      heat_index = calculate_heat_index(temperature, humidity)
      return heat_index - tolerance_offset + working_offset

    wind_chill = calculate_windchill(temperature, wind_speed)
    return wind_chill - tolerance_offset + working_offset

  
  @classmethod 
  def get_clothes_in_temp_reroll(cls, comfort, type):
    """
    Function that, given a comfort level, returns a random 
    article of clothing of a specified type (Hat, Shirt, etc)
    and its waterproofness

    Comfort should be in range -460 (absolute zero) and 6100 (melting point of tungsten)
    """

    context = {}
    
    if comfort < -460 or comfort > 6100:
      raise ValueError("Comfort must be in range -460 (absolute zero) and 6100 (melting point of tungsten).")

    if type not in ["HAT", "SHR", "PNT", "SHO", "MIS"]:
      raise ValueError("Type must be one of the following: HAT, SHR, PNT, SHO, MIS.")

    clothes = cls.objects.filter(clothing_type=type, comfort_low__lte=comfort, comfort_high__gte=comfort)

    if len(clothes) == 0:
        return None

    random_clothe = clothes[random.randint(0, len(clothes) - 1)]

    context["image"] = random_clothe.image.url
    context["name"] = random_clothe.name
    
    return (context, random_clothe.waterproof_rating)
    
  @classmethod
  def _get_clothes_in_temp(cls, comfort):
    """
    Function that, given a comfort value, iterates through the current clothes in the database.
    Returns:
    * The first set of clothes that are within the comfort range with the maximum waterproofing.
    * The average waterproofing of the clothes.

    Comfort should be in range -460 (absolute zero) and 6100 (melting point of tungsten)
    """

    # Define defaults in the case of errors
    outfit = []
    waterproof_average = 0

    # Ensure comfort is in range
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
          clothes.filter(clothing_type=query).order_by('-waterproof_rating')[0]
          for query in ["HAT", "SHR", "PNT", "SHO"]
      ]

      waterproof_average = sum([outfit.waterproof_rating
                                for outfit in outfit]) / 4

    except Exception as e:  # [0] throws error when filter returns nothing
      print(f"Error in getting clothes, {e}")

    return (outfit, waterproof_average)

  
  @classmethod
  def _get_clothes_in_prec(cls, precipitation_chance, average_waterproof):
    """
    Simple function that determines if waterproofing layers are needed based on the precipitation chance.

    Returns the waterproofing layers if needed
    """

    if precipitation_chance < 0 or precipitation_chance > 100:
      raise ValueError("Precipitation chance must be in range 0-100.")

    if average_waterproof > precipitation_chance:
      return []

    outfit = cls.objects.filter(clothing_type="MIS")
    return list(outfit)

  
  @classmethod
  def get_outfit_recommendation(cls, temperature, humidity, wind,
                                precipitation, tolerance_offset,
                                working_offset):
    """
    Function that combines the functionality of:
    * _get_clothes_in_prec
    * get_clothes_in_range
    * calculate_comfort
    * _get_color_palette
    
    This is to give the View a much cleaner model abstraction.

    Returns the following on a per outfit basis.
    {
      "comfort": INT,
      "waterproofness": INT,
      "outfit": [{"image": image, "name": name}],
      "precipitation_clothes": ["Strings"],
      "colors": ["Strings"] (e.g., "red")
    }
    """

    context = {}

    comfort = cls._calculate_comfort(temperature, humidity, wind,
                                     tolerance_offset, working_offset)
    outfit, waterproofness = cls._get_clothes_in_temp(comfort)
    precipitation_clothes = cls._get_clothes_in_prec(precipitation,
                                                     waterproofness)
    colors = cls._get_color_palette()

    context['comfort'] = comfort
    context['waterproofness'] = waterproofness
    context['outfit'] = [{"image": clothes.image.url, "name": clothes.name} for clothes in outfit]
    context['precipitation_outfit'] = [{"image": clothes.image.url, "name": clothes.name} for clothes in precipitation_clothes]
    context['colors'] = colors

    return context

  
  @classmethod
  def _get_color_palette(cls):
    """
    Function that takes into account the current season and returns up to 5 colors.
    """

    # courtesy of ChatGPT
    colors = {
        "winter": ["silver", "blue", "gray", "white", "darkgreen"],
        "spring": ["pink", "lightgreen", "lavender", "yellow", "turquoise"],
        "summer": ["yellow", "aqua", "skyblue", "coral", "limegreen"],
        "autumn": ["orange", "red", "brown", "goldenrod", "olive"]
    }

    try:
      year = datetime.now().year

      # https://stackoverflow.com/questions/16139306/determine-season-given-timestamp-in-python-using-datetime
      seasons = [('winter', (date(year, 1, 1), date(year, 3, 20))),
                 ('spring', (date(year, 3, 21), date(year, 6, 20))),
                 ('summer', (date(year, 6, 21), date(year, 9, 22))),
                 ('autumn', (date(year, 9, 23), date(year, 12, 20))),
                 ('winter', (date(year, 12, 21), date(year, 12, 31)))]

      today = date.today()
      season = [
          season for season, (start, end) in seasons if start <= today <= end
      ][0]
      return colors[season]

    except Exception as e:  # should be impossible
      print(f"Error {e}")
      return colors["winter"]


class Location(models.Model):
  """
  I don't actually think this is used.
  """
  
  name = models.CharField(max_length=30)

  def __str__(self):
    return self.name


class Weather(models.Model):
  """
  This might have a lot of unecessary fields.
  """

  location = models.ForeignKey(Location, on_delete=models.CASCADE)
  temperature = models.FloatField()
  humidity = models.IntegerField()  # Convert to percentage later
  wind_speed = models.FloatField()
  temperature_description = models.CharField(max_length=100)
  image = models.ImageField(upload_to='weather_images')
  date = models.DateTimeField()

  def __str__(self):
    """
    Returns a string of the location
    """
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
    requests_cache.install_cache(
        'weather_cache', expire_after=3600)  # Cache expires after 1 hour
    base_url = f"https://api.weather.gov/points/{latitude},{longitude}"
    location_response = requests.get(base_url, timeout=20) # added 20 seconds timeout
    location_data = location_response.json()

    # If we don't get an invalid location
    if 'status' not in location_data:
      weather_response = requests.get(location_data['properties']['forecastHourly'], timeout=20)
      # If the api doesn't randomly break continue
      # This occurs when a location is valid but the server just fails for some reason
      if weather_response.status_code == 500:
        return None
      weather_data = weather_response.json()
      return weather_data["properties"][
          "periods"]  # the actual weather forecast
    
    return None

  def _format_response(weather_data, location):
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

    if weather_data is None:
      return {}

    result = {
      "hours": [],
      "temperature": [], 
      "precipitation": [],
      "humidity": [],
      "wind": [],
      "location": location
    }

    for period in weather_data:
      result["hours"].append(datetime.fromisoformat(period["startTime"]).hour)
      result["temperature"].append(period["temperature"])
      result["precipitation"].append(period["probabilityOfPrecipitation"]["value"])
      result["humidity"].append(period["relativeHumidity"]["value"])
      result["wind"].append(int(period["windSpeed"].split(" ")[0]))

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
    result = None
    
    # Get location raw data from the user
    location = app.geocode(location_input)
    if location:
      latitude = location.latitude
      longitude = location.longitude
      weather_data = Weather._get_weather(latitude, longitude)
      if weather_data:
        result = Weather._format_response(weather_data, location)
        return result

    return None

class AppUser(models.Model):
  username = models.CharField(max_length=30, unique=True)
  # inventory = models.ManyToManyField(GenericClothes, related_name='users')
  
  def __str__(self):
    """ Return user name """
    return self.name
    
  def get_absolute_url(self):
    return reverse('user-detail', args=[str(self.id)])
    