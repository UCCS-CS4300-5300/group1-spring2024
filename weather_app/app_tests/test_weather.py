"""
Tests for the Weather model, View, and API calls.
"""

from unittest.mock import patch, call
from django.test import TestCase
from requests import ConnectTimeout, Response
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

    pass

  def test_get_invalid_location(self):
    """
    Tests function get(self, request).
    * Tests that get returns an error when an invalid location is entered
    * Sad Test
    """
  
    pass