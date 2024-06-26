"""
Tests for the Weather model, View, and API calls.
"""

from unittest.mock import patch, call
from django.test import TestCase
from django.urls import reverse
from requests import ConnectTimeout, Response
import json
from ..models import Weather
from ..views import WeatherView
from .. import models

class TestWeatherUnitTest(TestCase):
  """
  Tests epics Weather #31  
  """

  # --------------------------- _get_weather ---------------------------

  def test__get_weather(self):
    """
    Tests function _get_weather(latitude, longitute).
    * Tests that _get_weather formats the correct call to the API 
    and returns data if correctly formatted
    * Happy Test
    """

    # Arrange
    latitude = "40.7128"
    longitude = "-74.0060"

    example_response = {
      "properties": {"forecastHourly": "test_url", "periods": "test_weather_data"}
    }
    
    mock_get_return = Response()
    mock_get_return.status_code = 200
    mock_get_return.json = lambda : example_response

    # url, timeout
    expected_weather_calls = [
      call('https://api.weather.gov/points/40.7128,-74.0060', timeout=20),
      call('test_url', timeout=20),
    ]
  
    # Act
    with patch('requests.get') as mock_get:
      mock_get.return_value = mock_get_return
      weather_data = Weather._get_weather(latitude, longitude)
      
      # Assert
      self.assertEqual(weather_data, "test_weather_data")
      mock_get.assert_has_calls(expected_weather_calls, any_order=False)
  
  def test__get_weather_failed_api(self):
    """
    Tests function _get_weather(latitude, longitute).
    * Tests that _get_weather returns none if API fails (e.g., returns bad response)
    * Sad Test
    """

    # Arrange
    latitude = "40.7128"
    longitude = "-74.0060"

    example_response = {
      "properties": {"forecastHourly": "test_url", "periods": "test_weather_data"},
      "status": "failed"
    }

    mock_get_return = Response()
    mock_get_return.status_code = 500
    mock_get_return.json = lambda : example_response

    # Act
    with patch('requests.get') as mock_get:
      mock_get.return_value = mock_get_return
      weather_data = Weather._get_weather(latitude, longitude)

      # Assert
      self.assertEqual(weather_data, None)

  
  def test__get_weather_bad_inputs(self):
    """
    Tests function _get_weather(latitude, longitute).
    * Tests that _get_weather returns none if the inputs are not formatted correctly
    * Here we simulate bad input by timing out the request
    * Sad Test
    """
  
    # Arrange
    latitude = "40.7128"
    longitude = "-74.0060"
    
    example_response = {
      "properties": {"forecastHourly": "test_url", "periods": "test_weather_data"}
    }
    
    mock_get_return = Response()
    mock_get_return.status_code = 200
    # https://stackoverflow.com/questions/8294618/define-a-lambda-expression-that-raises-an-exception
    # lambda expressions do not allow raise statements
    mock_get_return.json = lambda : exec('raise ConnectTimeout') # requests.get throws error when times out
    
    # Act
    with patch('requests.get') as mock_get:
      mock_get.return_value = mock_get_return

      # Assert
      with self.assertRaises(ConnectTimeout):
        weather_data = Weather._get_weather(latitude, longitude)    
      
  # ---------------------------------------------------------------------------------

  # --------------------------- _format_response ---------------------------

  def test__format_response(self):
    """
    Tests _format_response(weather_data, location)
    * Ensures it can correctly format data
    """

    input_data = [
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T18:00:00-07:00",
        "endTime": "2024-02-24T19:00:00-07:00",
        "temperature": 10,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 90
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 30
        },
        "windSpeed": "10 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      },
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T19:00:00-07:00",
        "endTime": "2024-02-24T20:00:00-07:00",
        "temperature": 20,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 100
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 40
        },
        "windSpeed": "25 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      }
    ]

    expected_output = {
      "hours": [18, 19],
      "temperature": [10, 20],
      "precipitation": [90, 100],
      "humidity": [30, 40],
      "wind": [10, 25],
      "location": "New York"
    }

    output = Weather._format_response(input_data, "New York")
    self.assertEqual(output, expected_output)
  
  def test__format_response_bad_inputs(self):
    """
    Tests _format_response(weather_data, location)
    * Should return [] given no input
    """

    output = Weather._format_response(None, None)
    self.assertEqual(output, {})

  # ---------------------------------------------------------------------------------

  # --------------------------- get_weather_forecast ---------------------------

  def test_get_weather_forecast(self):
    """
    Tests get_weather_forecast(location)
    * Ensures it can correctly get latitude and longitude then call 
    * _get_weather and _format_response
    """

    location = "New York"

    mock_get_weather_return = [
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T18:00:00-07:00",
        "endTime": "2024-02-24T19:00:00-07:00",
        "temperature": 10,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 90
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 30
        },
        "windSpeed": "10 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      },
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T19:00:00-07:00",
        "endTime": "2024-02-24T20:00:00-07:00",
        "temperature": 20,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 100
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 40
        },
        "windSpeed": "25 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      }
    ]

    mock_format_response = {
      "hours": [18, 19],
      "temperature": [10, 20],
      "precipitation": [90, 100],
      "humidity": [30, 40],
      "wind": [10, 25],
      "location": "New York"
    }

    class MockLocation():
      def __init__(self, address, coords, raw):
        self.address = address
        self.latitude = coords[0]
        self.longitude = coords[1]
        self.raw = raw

    mock_geocode_return = MockLocation("New Work", (40.7127281, -74.0060152), "raw")
    
    expected_get_weather_calls = [
      call(40.7127281, -74.0060152)
    ]

    expected_get_format_response_calls = [
      call(mock_get_weather_return, mock_geocode_return)
    ]
    
    with (
      patch('weather_app.models.Weather._get_weather') as mock_get_weather,
      patch('weather_app.models.Weather._format_response') as mock_format_response,
      patch('geopy.geocoders.Nominatim.geocode') as mock_geocode
    ):
      mock_get_weather.return_value = mock_get_weather_return
      mock_format_response.return_value = mock_format_response
      mock_geocode.return_value = mock_geocode_return

      forecast = Weather.get_weather_forecast(location)

      mock_get_weather.assert_has_calls(expected_get_weather_calls)
      mock_format_response.assert_has_calls(expected_get_format_response_calls)
      self.assertEqual(forecast, mock_format_response.return_value)

  def test_get_weather_forecast_invalid_input(self):
    """
    Tests get_weather_forecast(location)
    * Ensures it returns none if poorly formatted input (e.g., canada)
    """

    location = "Canada"
    output = Weather.get_weather_forecast(location)
    self.assertEqual(output, None)

  def test_get_weather_forecast_default_input(self):
    """
    Tests get_weather_forecast(location)
    * Ensures it uses default location if none provided
    """
  
    location = ""

    mock_get_weather_return = [
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T18:00:00-07:00",
        "endTime": "2024-02-24T19:00:00-07:00",
        "temperature": 10,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 90
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 30
        },
        "windSpeed": "10 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      },
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T19:00:00-07:00",
        "endTime": "2024-02-24T20:00:00-07:00",
        "temperature": 20,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 100
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 40
        },
        "windSpeed": "25 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      }
    ]

    mock_format_response = {
      "hours": [18, 19],
      "temperature": [10, 20],
      "precipitation": [90, 100],
      "humidity": [30, 40],
      "wind": [10, 25],
      "location": "80918"
    }

    class MockLocation():
      def __init__(self, address, coords, raw):
        self.address = address
        self.latitude = coords[0]
        self.longitude = coords[1]
        self.raw = raw

    mock_geocode_return = MockLocation("80918", (40.7127281, -74.0060152), "raw")

    expected_get_weather_calls = [
      call(40.7127281, -74.0060152)
    ]

    expected_get_format_response_calls = [
      call(mock_get_weather_return, mock_geocode_return)
    ]

    with (
      patch('weather_app.models.Weather._get_weather') as mock_get_weather,
      patch('weather_app.models.Weather._format_response') as mock_format_response,
      patch('geopy.geocoders.Nominatim.geocode') as mock_geocode
    ):
      mock_get_weather.return_value = mock_get_weather_return
      mock_format_response.return_value = mock_format_response
      mock_geocode.return_value = mock_geocode_return

      forecast = Weather.get_weather_forecast(location)

      mock_get_weather.assert_has_calls(expected_get_weather_calls)
      mock_format_response.assert_has_calls(expected_get_format_response_calls)
      self.assertEqual(forecast, mock_format_response.return_value)


  # ---------------------------------------------------------------------------------

class TestWeatherViewUnitTest(TestCase):
  """
  Tests epics Weather #31 for the WeatherView class
  """
  
  def test_get(self):
    """
    Tests function get(self, request).
    * Tests that get calls the model function _get_weather with appropriate input
    and returns its formatted output
    * Happy Test
    """
  
    context = {
      "location": "Nueva York"
    }

    mock_weather_data = {
      "temperature": 10,
      "precipitation": 11,
      "humidity": 12,
      "wind": 13,
      "hours": [1,2,3],
      "location": "Nueva York"
    }

    expected_response = {
      'temp_forecast': mock_weather_data['temperature'],
      'precipitation_forecast': mock_weather_data['precipitation'],
      'humidity_forecast': mock_weather_data['humidity'],
      'wind_forecast': mock_weather_data['wind'],
      'day_forecast': mock_weather_data['hours'][:24],
      'location' : mock_weather_data['location']
    }

    expected_get_weather_forecast_calls = [
      call("Nueva York")
    ]

    with patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather_forecast:
      mock_get_weather_forecast.return_value = mock_weather_data

      response = self.client.get(reverse('home'), context)
      response_context = response.context
      mock_get_weather_forecast.assert_has_calls(expected_get_weather_forecast_calls)


    self.assertEqual(response.status_code, 200)
    self.assertEqual(expected_response['temp_forecast'], response_context['temp_forecast'])
    self.assertEqual(expected_response['precipitation_forecast'], response_context['precipitation_forecast'])
    self.assertEqual(expected_response['humidity_forecast'], response_context['humidity_forecast'])
    self.assertEqual(expected_response['wind_forecast'], response_context['wind_forecast'])
    self.assertEqual(expected_response['day_forecast'], response_context['day_forecast'])
    self.assertEqual(expected_response['location'], response_context['location'])

  def test_get_invalid_location(self):
    """
    Tests function get(self, request).
    * Tests that get returns an error when weather data is not returned
    * Sad Test
    """
  
  
    mock_weather_data = None
    context = {"location": "Nueva York"}
    expected_response = {'error_message': 'Please enter a valid location'}
  
    expected_get_weather_forecast_calls = [
      call("Nueva York")
    ]
  
    with patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather_forecast:
      mock_get_weather_forecast.return_value = mock_weather_data
  
      response = self.client.get(reverse('home'), context)
      response_context = response.context
      mock_get_weather_forecast.assert_has_calls(expected_get_weather_forecast_calls)
  
  
    self.assertEqual(response.status_code, 206)
    self.assertEqual(expected_response['error_message'], response_context['error_message'])


class TestWeatherIntegration(TestCase):
  """
  Tests epics Weather #31 for the WeatherView class at the integration level.
  """

  def test_integration_weather(self):
    """
    Tests that the user can access the weather when they provide location.
    """

    context = {
      "location": "Nueva York"
    }
  
    mock_weather_api_response = [
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T18:00:00-07:00",
        "endTime": "2024-02-24T19:00:00-07:00",
        "temperature": 10,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 90
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 30
        },
        "windSpeed": "10 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      },
      {
        "number": 1,
        "name": "",
        "startTime": "2024-02-24T19:00:00-07:00",
        "endTime": "2024-02-24T20:00:00-07:00",
        "temperature": 20,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": {
          "unitCode": "wmoUnit:percent",
          "value": 100
        },
        "dewpoint": {
          "unitCode": "wmoUnit:degC",
          "value": -11.666666666666666
        },
        "relativeHumidity": {
          "unitCode": "wmoUnit:percent",
          "value": 40
        },
        "windSpeed": "25 mph",
        "windDirection": "WNW",
        "icon": "https://api.weather.gov/icons/land/night/bkn,0?size=small",
        "shortForecast": "Mostly Cloudy",
        "detailedForecast": ""
      }
    ]

    with (
      patch('weather_app.models.Weather._get_weather') as mock__get_weather
    ):
      mock__get_weather.return_value = mock_weather_api_response
  
      response = self.client.get(reverse('home'), context)
      response_context = response.context  
  
    self.assertEqual(response.status_code, 200)
    self.assertIn('temp_forecast', response_context)
    self.assertIn('precipitation_forecast', response_context)
    self.assertIn('humidity_forecast', response_context)
    self.assertIn('wind_forecast', response_context)
    self.assertIn('day_forecast', response_context)
    self.assertIn('location', response_context)


  
  def test_integration_weather_invalid_location(self):
    """
    Test the user gets error when they provide an invalid location.
    """

    context = {
      "location": "Nueva York"
    }
    
    mock_weather_api_response = []
    
    with (
      patch('weather_app.models.Weather._get_weather') as mock__get_weather
    ):
      mock__get_weather.return_value = mock_weather_api_response
    
      response = self.client.get(reverse('home'), context)
      response_context = response.context  
    
    self.assertEqual(response.status_code, 206)
    self.assertIn('error_message', response_context)