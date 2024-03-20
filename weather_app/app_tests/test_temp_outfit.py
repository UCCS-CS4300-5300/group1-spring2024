from typing import Generic
from django.test import TestCase
from ..models import GenericClothes
from datetime import datetime
from django.utils.timezone import make_aware
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from unittest.mock import patch, call
from django.urls import reverse
import json


class TestGenericClothesIntegration(TestCase):
  """
  Tests user story: Temperature Based Outfit Generation Per Data Set (Temp, Humidity, Precipitation, Wind) #38 and user story: Temperature Based Outfit Generation #14 at the integration level. 
  """

  fixtures = ['fixture_generic_clothes.json']

  def test_integration_temperature_generation_invalid_inputs(self):
    """
    Test that the movie list view returns our specific movie with the appropriate showtime. Have to stub API call since we need to determine what clothes should be worn to ensure the test is repeatable. 
    """

    # arrange
    context = {"tolerance_offset": "nan", "working_offset": 10, "location": 10001}

    # act
    with patch('weather_app.models.Weather.get_weather_forecast'
               ) as mock_get_weather_forecast:
      mock_weather = {
          'hours': [
              18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
              13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 3, 4, 5, 6, 7,
              8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0,
              1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
              19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
              14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7,
              8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0,
              1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
              19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6
          ],
          'temperature': [
              27, 26, 25, 24, 23, 22, 21, 21, 21, 20, 20, 20, 20, 22, 27, 33,
              36, 40, 43, 47, 48, 48, 48, 47, 41, 35, 32, 29, 26, 25, 24, 23,
              24, 23, 23, 23, 25, 29, 33, 39, 46, 51, 54, 55, 56, 57, 57, 55,
              51, 46, 42, 39, 37, 36, 35, 34, 34, 33, 33, 34, 36, 38, 41, 45,
              49, 53, 55, 56, 57, 58, 57, 56, 53, 49, 45, 43, 41, 40, 39, 38,
              37, 36, 34, 34, 35, 37, 40, 44, 48, 51, 53, 54, 55, 55, 55, 54,
              51, 48, 45, 43, 41, 40, 39, 39, 38, 37, 36, 36, 37, 38, 40, 42,
              45, 47, 48, 48, 47, 46, 45, 43, 41, 39, 37, 35, 34, 33, 32, 32,
              32, 31, 30, 30, 30, 30, 31, 32, 33, 34, 35, 36, 36, 36, 36, 35,
              34, 32, 31, 30, 29, 28, 28, 27, 27, 26, 25, 25
          ],
          'precipitation': [
              13, 11, 10, 8, 6, 4, 3, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 2, 2, 2, 2, 2, 2, 13, 13, 13, 13, 13, 13, 17, 17, 17, 17,
              17, 17, 27, 27, 27, 27, 27, 27, 57, 57, 57, 57, 57, 57, 73, 73,
              73, 73, 73, 73, 70, 70, 70, 70, 70, 70, 65, 65, 65, 65, 65, 65,
              52, 52, 52, 52, 52, 52, 37, 37, 37, 37, 37, 37, 23, 23, 23, 23,
              23, 23, 23
          ],
          'humidity': [
              76, 78, 81, 81, 84, 84, 88, 88, 84, 88, 84, 81, 81, 77, 63, 49,
              42, 36, 32, 26, 25, 26, 27, 31, 39, 49, 56, 63, 68, 71, 74, 77,
              74, 71, 68, 65, 60, 51, 43, 32, 23, 18, 16, 15, 16, 16, 16, 18,
              22, 28, 34, 39, 42, 43, 45, 45, 45, 47, 47, 45, 43, 40, 37, 32,
              26, 23, 21, 20, 20, 20, 21, 22, 26, 30, 36, 39, 42, 44, 46, 48,
              50, 52, 54, 54, 52, 50, 44, 38, 31, 28, 26, 26, 25, 25, 24, 25,
              29, 34, 40, 45, 50, 52, 54, 54, 57, 59, 61, 61, 59, 59, 55, 48,
              41, 37, 34, 34, 35, 37, 38, 43, 48, 52, 59, 66, 69, 72, 75, 72,
              72, 75, 75, 75, 75, 72, 69, 63, 58, 56, 54, 54, 54, 54, 52, 54,
              56, 58, 61, 63, 69, 71, 68, 71, 68, 71, 74, 74
          ],
          'wind': [
              10, 10, 10, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
              10, 10, 10, 10, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10,
              10, 5, 5, 5, 5, 10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5, 10, 10, 10,
              10, 10, 10, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15,
              15, 15, 15, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 15,
              15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 10, 10, 10, 10, 10,
              10, 10, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15, 15,
              15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 20,
              20, 20, 20, 20, 20, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
              15, 10
          ]
      }
      mock_get_weather_forecast.return_value = mock_weather

      response = self.client.get(reverse('recommendation'), context)
      context_data = response.context

    # assert
    self.assertEqual(response.status_code, 200)
    self.assertNotIn('outfit_current', context_data)
    self.assertNotIn('outfit_six_hours', context_data)
    self.assertNotIn('outfit_twelve_hours', context_data)
    self.assertNotIn('rain_outfit_current', context_data)
    self.assertNotIn('rain_outfit_six_hours', context_data)
    self.assertNotIn('rain_outfit_twelve_hours', context_data)


  # happy paths
  def test_integration_temperature_generation(self):
    """
    Test that the movie list view returns our specific movie with the appropriate showtime. Have to stub API call since we need to determine what clothes should be worn to ensure the test is repeatable. 
    """

    # arrange
    context = {"tolerance_offset": 5, "working_offset": 10, "location": 10001}

    # act
    with patch('weather_app.models.Weather.get_weather_forecast'
               ) as mock_get_weather_forecast:
      mock_weather = {
          'hours': [
              18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
              13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 3, 4, 5, 6, 7,
              8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0,
              1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
              19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
              14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7,
              8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0,
              1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
              19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6
          ],
          'temperature': [
              27, 26, 25, 24, 23, 22, 21, 21, 21, 20, 20, 20, 20, 22, 27, 33,
              36, 40, 43, 47, 48, 48, 48, 47, 41, 35, 32, 29, 26, 25, 24, 23,
              24, 23, 23, 23, 25, 29, 33, 39, 46, 51, 54, 55, 56, 57, 57, 55,
              51, 46, 42, 39, 37, 36, 35, 34, 34, 33, 33, 34, 36, 38, 41, 45,
              49, 53, 55, 56, 57, 58, 57, 56, 53, 49, 45, 43, 41, 40, 39, 38,
              37, 36, 34, 34, 35, 37, 40, 44, 48, 51, 53, 54, 55, 55, 55, 54,
              51, 48, 45, 43, 41, 40, 39, 39, 38, 37, 36, 36, 37, 38, 40, 42,
              45, 47, 48, 48, 47, 46, 45, 43, 41, 39, 37, 35, 34, 33, 32, 32,
              32, 31, 30, 30, 30, 30, 31, 32, 33, 34, 35, 36, 36, 36, 36, 35,
              34, 32, 31, 30, 29, 28, 28, 27, 27, 26, 25, 25
          ],
          'precipitation': [
              100, 11, 10, 8, 6, 4, 3, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 2, 2, 2, 2, 2, 2, 13, 13, 13, 13, 13, 13, 17, 17, 17, 17,
              17, 17, 27, 27, 27, 27, 27, 27, 57, 57, 57, 57, 57, 57, 73, 73,
              73, 73, 73, 73, 70, 70, 70, 70, 70, 70, 65, 65, 65, 65, 65, 65,
              52, 52, 52, 52, 52, 52, 37, 37, 37, 37, 37, 37, 23, 23, 23, 23,
              23, 23, 23
          ],
          'humidity': [
              76, 78, 81, 81, 84, 84, 88, 88, 84, 88, 84, 81, 81, 77, 63, 49,
              42, 36, 32, 26, 25, 26, 27, 31, 39, 49, 56, 63, 68, 71, 74, 77,
              74, 71, 68, 65, 60, 51, 43, 32, 23, 18, 16, 15, 16, 16, 16, 18,
              22, 28, 34, 39, 42, 43, 45, 45, 45, 47, 47, 45, 43, 40, 37, 32,
              26, 23, 21, 20, 20, 20, 21, 22, 26, 30, 36, 39, 42, 44, 46, 48,
              50, 52, 54, 54, 52, 50, 44, 38, 31, 28, 26, 26, 25, 25, 24, 25,
              29, 34, 40, 45, 50, 52, 54, 54, 57, 59, 61, 61, 59, 59, 55, 48,
              41, 37, 34, 34, 35, 37, 38, 43, 48, 52, 59, 66, 69, 72, 75, 72,
              72, 75, 75, 75, 75, 72, 69, 63, 58, 56, 54, 54, 54, 54, 52, 54,
              56, 58, 61, 63, 69, 71, 68, 71, 68, 71, 74, 74
          ],
          'wind': [
              10, 10, 10, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
              10, 10, 10, 10, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10,
              10, 5, 5, 5, 5, 10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5, 10, 10, 10,
              10, 10, 10, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15,
              15, 15, 15, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 15,
              15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 10, 10, 10, 10, 10,
              10, 10, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15, 15,
              15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 20,
              20, 20, 20, 20, 20, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
              15, 10
          ]
      }
      mock_get_weather_forecast.return_value = mock_weather

      response = self.client.get(reverse('recommendation'), context)
      context_data = response.context

    # assert
    self.assertEqual(response.status_code, 200)
    self.assertEqual(context_data['outfit_current'], 
                     ["Thermal Running Hat", "Insulated Long Sleeve", "Fleece-Lined Softshell Pants", "Waterproof Hiking Boots"])
    self.assertEqual(context_data['rain_outfit_current'], ["Umbrella", "Raincoat"])

    self.assertEqual(context_data['outfit_six_hours'], 
                     ["Thermal Running Hat", "Heavy Wool Sweater", "Thermal Wool Trousers", "Waterproof Hiking Boots"])
    self.assertEqual(context_data['rain_outfit_six_hours'], [])

    self.assertEqual(context_data['outfit_twelve_hours'], 
                     ["Thermal Running Hat", "Heavy Wool Sweater", "Thermal Wool Trousers", "Waterproof Hiking Boots"])
    self.assertEqual(context_data['rain_outfit_twelve_hours'], [])

  

class TestGenericClothesViewUnit(TestCase):
  """
  Tests user story: 
  1. Temperature Based Outfit Generation Per Data Set (Temp, Humidity, Precipitation, Wind) #38 
  2. Temperature Based Outfit Generation #14 
  3. Location Based Weather Generation Matching #33
  4. Precipitation Based Outfit Generation #44

  for the view unit.

  Note that the unit tests overlap a lot between these stories since the same code satisfies all of them. 
  """

  fixtures = ['fixture_generic_clothes.json']

  def test_view_calls_model_without_location(self):
    """
    Tests that the view calls the model get_weather function without a location.
    """

    with patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather:
      response = self.client.get(reverse('recommendation'), {"working_offset": "0", "tolerance_offset": "0"})

      self.assertEqual(response.status_code, 200)
      mock_get_weather.assert_called_once_with(None)
  
  def test_view_calls_model_with_location(self):
    """
    Tests that the view call the model get_weather function with the correct location. Must have other parameters included to call.
    """

    with patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather:
      response = self.client.get(reverse('recommendation'), {"working_offset": "0", "tolerance_offset": "0", "location": "10001"})
  
      self.assertEqual(response.status_code, 200)
      mock_get_weather.assert_called_once_with('10001')
  
  def test_view_get_should_not_call_model(self):
    """
    Tests that the view returns 200 when user input is not provided and does not call the model methods.
    """

    with patch('weather_app.models.GenericClothes.calculate_comfort'
               ) as mock_calculate_comfort:
      with patch('weather_app.models.GenericClothes.get_clothes_in_range'
                 ) as mock_get_clothes_in_range:
        response = self.client.get(reverse('recommendation'), {})

        self.assertEqual(response.status_code, 200)
        mock_calculate_comfort.assert_not_called()
        mock_get_clothes_in_range.assert_not_called()

  def test_view_get_with_params_should_call_model(self):
    """
    Tests that the view returns 200 when correct user input is provided and calls the model methods with stubbed parameters from the get_weather_forcecast function. 
    """

    with patch('weather_app.models.Weather.get_weather_forecast'
               ) as mock_get_weather_forecast:
      with patch('weather_app.models.GenericClothes.calculate_comfort'
                 ) as mock_calculate_comfort:
        with patch('weather_app.models.GenericClothes.get_clothes_in_range'
                   ) as mock_get_clothes_in_range:
          mock_weather = {
              'hours': [
                  18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                  12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 3, 4,
                  5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                  21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                  15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7,
                  8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                  0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                  18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                  12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3,
                  4, 5, 6
              ],
              'temperature': [
                  27, 26, 25, 24, 23, 22, 21, 21, 21, 20, 20, 20, 20, 22, 27,
                  33, 36, 40, 43, 47, 48, 48, 48, 47, 41, 35, 32, 29, 26, 25,
                  24, 23, 24, 23, 23, 23, 25, 29, 33, 39, 46, 51, 54, 55, 56,
                  57, 57, 55, 51, 46, 42, 39, 37, 36, 35, 34, 34, 33, 33, 34,
                  36, 38, 41, 45, 49, 53, 55, 56, 57, 58, 57, 56, 53, 49, 45,
                  43, 41, 40, 39, 38, 37, 36, 34, 34, 35, 37, 40, 44, 48, 51,
                  53, 54, 55, 55, 55, 54, 51, 48, 45, 43, 41, 40, 39, 39, 38,
                  37, 36, 36, 37, 38, 40, 42, 45, 47, 48, 48, 47, 46, 45, 43,
                  41, 39, 37, 35, 34, 33, 32, 32, 32, 31, 30, 30, 30, 30, 31,
                  32, 33, 34, 35, 36, 36, 36, 36, 35, 34, 32, 31, 30, 29, 28,
                  28, 27, 27, 26, 25, 25
              ],
              'precipitation': [
                  13, 11, 10, 8, 6, 4, 3, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 13, 13, 13,
                  13, 13, 13, 17, 17, 17, 17, 17, 17, 27, 27, 27, 27, 27, 27,
                  57, 57, 57, 57, 57, 57, 73, 73, 73, 73, 73, 73, 70, 70, 70,
                  70, 70, 70, 65, 65, 65, 65, 65, 65, 52, 52, 52, 52, 52, 52,
                  37, 37, 37, 37, 37, 37, 23, 23, 23, 23, 23, 23, 23
              ],
              'humidity': [
                  76, 78, 81, 81, 84, 84, 88, 88, 84, 88, 84, 81, 81, 77, 63,
                  49, 42, 36, 32, 26, 25, 26, 27, 31, 39, 49, 56, 63, 68, 71,
                  74, 77, 74, 71, 68, 65, 60, 51, 43, 32, 23, 18, 16, 15, 16,
                  16, 16, 18, 22, 28, 34, 39, 42, 43, 45, 45, 45, 47, 47, 45,
                  43, 40, 37, 32, 26, 23, 21, 20, 20, 20, 21, 22, 26, 30, 36,
                  39, 42, 44, 46, 48, 50, 52, 54, 54, 52, 50, 44, 38, 31, 28,
                  26, 26, 25, 25, 24, 25, 29, 34, 40, 45, 50, 52, 54, 54, 57,
                  59, 61, 61, 59, 59, 55, 48, 41, 37, 34, 34, 35, 37, 38, 43,
                  48, 52, 59, 66, 69, 72, 75, 72, 72, 75, 75, 75, 75, 72, 69,
                  63, 58, 56, 54, 54, 54, 54, 52, 54, 56, 58, 61, 63, 69, 71,
                  68, 71, 68, 71, 74, 74
              ],
              'wind': [
                  10, 10, 10, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                  5, 5, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10,
                  10, 10, 10, 10, 5, 5, 5, 5, 10, 10, 10, 10, 10, 5, 5, 5, 5,
                  5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 15, 15, 15,
                  15, 15, 15, 15, 15, 15, 15, 15, 10, 10, 10, 10, 10, 10, 10,
                  10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
                  15, 15, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 15,
                  15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
                  15, 15, 15, 15, 15, 15, 15, 15, 20, 20, 20, 20, 20, 20, 15,
                  15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 10
              ]
          }

          mock_comfort = 50
          tolerance_offset = -10
          working_offset = 10

          mock_get_weather_forecast.return_value = mock_weather
          mock_calculate_comfort.return_value = mock_comfort
          mock_get_clothes_in_range.return_value = ([], [], 0)

          response = self.client.get(
              reverse('recommendation'), {
                  "working_offset": working_offset,
                  "tolerance_offset": tolerance_offset
              })

          self.assertEqual(response.status_code, 200)

          expected_calculate_comfort_calls = [
              call(mock_weather['temperature'][0], mock_weather['humidity'][0],
                   mock_weather['wind'][0], tolerance_offset, working_offset),
              call(mock_weather['temperature'][6], mock_weather['humidity'][6],
                   mock_weather['wind'][6], tolerance_offset, working_offset),
              call(mock_weather['temperature'][12],
                   mock_weather['humidity'][12], mock_weather['wind'][12],
                   tolerance_offset, working_offset)
          ]

          expected_get_clothes_in_range_calls = [
              call(mock_comfort, 13),
              call(mock_comfort, 3),
              call(mock_comfort, 0)
          ]

          mock_calculate_comfort.assert_has_calls(
              expected_calculate_comfort_calls, any_order=False)
          mock_get_clothes_in_range.assert_has_calls(
              expected_get_clothes_in_range_calls, any_order=False)

  def test_view_get_with_invalid_params_should_throw_error(self):
    """
    Tests that the view returns 200 when incorrect user input is provided and includes an error passed to the template.
    """

    with patch('weather_app.models.Weather.get_weather_forecast'
               ) as mock_get_weather_forecast:
      with patch('weather_app.models.GenericClothes.calculate_comfort'
                 ) as mock_calculate_comfort:
        with patch('weather_app.models.GenericClothes.get_clothes_in_range'
                   ) as mock_get_clothes_in_range:
          tolerance_offset = 'not an integer'
          working_offset = 'not even close'

          response = self.client.get(
              reverse('recommendation'), {
                  "working_offset": working_offset,
                  "tolerance_offset": tolerance_offset
              })
          self.assertEqual(response.status_code, 200)
          self.assertEqual(
              response.context['error'],
              "Error, please try again. Error message: invalid literal for int() with base 10: 'not an integer'"
          )


class TestGenericClothesModelUnit(TestCase):
  """
  Tests user story: Temperature Based Outfit Generation Per Data Set (Temp, Humidity, Precipitation, Wind) #38 and user story: Temperature Based Outfit Generation #14.

  Note that the unit tests overlap entirely with both of these stories.
  """

  fixtures = ['fixture_generic_clothes.json']

  def test_get_clothes_in_range_normal(self):
    """
    Tests that a set of clothes is returned when the comfort is something reasonable (e.g. 11, 60, 105 degrees). Happy.
    """

    # Arrange
    comfort = 11
    precipitation_chance = 0

    outfit, rain_outfit, avg = GenericClothes.get_clothes_in_range(comfort, precipitation_chance)
    outfit_names = [clothes.name for clothes in outfit]

    self.assertEqual(len(outfit), 4)
    self.assertEqual(outfit_names, [
        "Thermal Running Hat", "Heavy Wool Sweater", "Thermal Wool Trousers",
        "Waterproof Hiking Boots"
    ])
    self.assertEqual(avg, 46.25)
    self.assertEqual(rain_outfit, [])

  def test_get_clothes_in_range_wet(self):
    """
    Tests that a set of clothes is returned when the comfort is something reasonable (e.g. 11, 60, 105 degrees). Happy.
    """
    # Arrange
    comfort = 60
    precipitation_chance = 85
  
    outfit, rain_outfit, avg = GenericClothes.get_clothes_in_range(comfort, precipitation_chance)
    outfit_names = [clothes.name for clothes in outfit]

    self.assertEqual(len(outfit), 4)
    self.assertEqual(outfit_names, [
        "Ventilated Bucket Hat", "Breathable Long Sleeve",
        "Convertible Cargo Pants", "Breathable Trail Running Shoes"
    ])
    self.assertEqual(rain_outfit, ["Umbrella", "Raincoat"])
    self.assertEqual(avg, 20.0)

  def test_get_clothes_in_range_hot(self):
    """
    Tests that a set of clothes is returned when the comfort is something reasonable (e.g. 11, 60, 105 degrees). Happy.
    """
  
    # Arrange
    comfort = 105
    precipitation_chance = 0
  
    outfit, rain_outfit, avg = GenericClothes.get_clothes_in_range(comfort, precipitation_chance)
    outfit_names = [clothes.name for clothes in outfit]

    self.assertEqual(len(outfit), 4)
    self.assertEqual(outfit_names, [
        "Ultra-Light Solar Shield Hat", "Mesh Ventilated Running Shirt",
        "Ventilated Mesh Shorts", "Ventilated Mesh Sandals"
    ])
    self.assertEqual(avg, 10)
    self.assertEqual(rain_outfit, [])

  def test_get_clothes_in_range_invalid_temp(self):
    """
    Tests that no set of clothes is returned when the comfort is something unreasonable (e.g. 20000 degrees). Sad.
    """

    with self.assertRaises(ValueError):
      GenericClothes.get_clothes_in_range(20000, 0)
      GenericClothes.get_clothes_in_range(-5000, 0)
  
  def test_get_clothes_in_range_invalid_prec(self):
    """
    Tests that no set of clothes is returned when the precipitation is something unreasonable (e.g. 110%). Sad.
    """

    with self.assertRaises(ValueError):
      GenericClothes.get_clothes_in_range(70, 110)
      GenericClothes.get_clothes_in_range(70, -10)

  def test_calculate_comfort_invalid_working_tolerance(self):
    """
    Test working_offset is not less than 0. Sad
    """

    with self.assertRaises(ValueError):
      GenericClothes.calculate_comfort(temperature=75,
                                       humidity=1,
                                       wind_speed=10,
                                       tolerance_offset=10,
                                       working_offset=-10)

    with self.assertRaises(ValueError):
      GenericClothes.calculate_comfort(temperature=75,
                                       humidity=1,
                                       wind_speed=10,
                                       tolerance_offset=-10,
                                       working_offset=-10)

  def test_calculate_comfort_invalid_windspeed(self):
    """
    Test that wind speed is not less than 0. Sad
    """

    with self.assertRaises(ValueError):
      GenericClothes.calculate_comfort(temperature=75,
                                       humidity=1,
                                       wind_speed=-10,
                                       tolerance_offset=0,
                                       working_offset=0)

  def test_calculate_comfort_invalid_humidity(self):
    """
    Test that humidity is not less than 0. Sad
    """

    with self.assertRaises(ValueError):
      GenericClothes.calculate_comfort(temperature=75,
                                       humidity=-1,
                                       wind_speed=10,
                                       tolerance_offset=0,
                                       working_offset=0)

  def test_calculate_comfort_low_temp(self):
    """
    Test that calculate_comfort uses the wind chill calculation when the temperature is less than or equal to 75. Happy
    """

    # in format of (temperature, humidity, wind_speed, tolerance_offset, working_offset, expected comfort)
    # https://gist.github.com/aipi/99ed2c992be41be437bb9506de73cb44
    test_data = [(70, 50, 10, 5, 3, 68.825), (40, 0, 20, 1, 2, 31.481)]

    for test_params in test_data:
      with self.subTest():
        comfort_params = test_params[0:5]
        expected = test_params[5]
        comfort = GenericClothes.calculate_comfort(*comfort_params)
        self.assertAlmostEqual(comfort, expected, places=2)

  def test_calculate_comfort_high_temp(self):
    """
    Test that calculate_comfort uses the wind chill calculation when the temperature is less than or equal to 75. Happy
    """

    # in format of (temperature, humidity, wind_speed, tolerance_offset, working_offset, expected comfort)
    # https://gist.github.com/aipi/99ed2c992be41be437bb9506de73cb44
    test_data = [(80, 60, 5, 0, 0, 81.811), (76, 65, 15, 2, 4, 79.869)]

    for test_params in test_data:
      with self.subTest():
        comfort_params = test_params[0:5]
        expected = test_params[5]
        comfort = GenericClothes.calculate_comfort(*comfort_params)
        self.assertAlmostEqual(comfort, expected, places=2)

  def test_clean_range_low_less_high(self):
    """
    Tests to ensure that the comfort low is not greater than the comfort high. Sad
    """

    clothe = GenericClothes(name="test_name",
                            clothing_type="HAT",
                            comfort_low=100,
                            comfort_high=50,
                            waterproof_rating=100)

    with self.assertRaises(ValidationError):
      clothe.clean()
      clothe.save()

  def test_clean_range_low_eq_high(self):
    """
    Tests to ensure that the comfort low is not equal to the comfort high. Sad
    """

    clothe = GenericClothes(name="test_name",
                            clothing_type="HAT",
                            comfort_low=50,
                            comfort_high=50,
                            waterproof_rating=100)

    with self.assertRaises(ValidationError):
      clothe.clean()
      clothe.save()

  def test_clean_range_low_greater_high(self):
    """
    Tests to ensure that the comfort low is greater than the comfort high. Happy
    """

    clothe = GenericClothes(name="test_name",
                            clothing_type="HAT",
                            comfort_low=50,
                            comfort_high=60,
                            waterproof_rating=100)

    clothe.clean()
    clothe.save()

    self.assertEqual(clothe.comfort_low, 50)


def test_get_clothes_in_prec_out_of_range(self):
  """
  Tests to ensure that, when the precipitation is above 100%, get_clothes_in_prec returns an error.
  """

  # Arrange
  precipitation_chance = 110
  average_waterproofing = 20

  # Act / Assert
  with self.assertRaises(ValueError):
    outfit = GenericClothes._get_clothes_in_prec(precipitation_chance, average_waterproofing)

def test_get_clothes_in_prec_wet(self):
  """
  Tests to ensure that, when the precipitation is above average waterproofing, get_clothes_in_prec returns an umbrella and raincoat.
  """

  # Arrange
  precipitation_chance = 50
  average_waterproofing = 20

  # Act
  outfit = GenericClothes._get_clothes_in_prec(precipitation_chance, average_waterproofing)

  # Assert
  self.assertEqual(outfit, ["Umbrella", "Raincoat"])

def test_get_clothes_in_prec_middle(self):
  """
  Tests to ensure that, when the precipitation is the same as average waterproofing, get_clothes_in_prec returns an umbrella and raincoat.
  """

  # Arrange
  precipitation_chance = 50
  average_waterproofing = 50

  # Act
  outfit = GenericClothes._get_clothes_in_prec(precipitation_chance, average_waterproofing)

  # Assert
  self.assertEqual(outfit, ["Umbrella", "Raincoat"])

def test_get_clothes_in_prec_dry(self):
  """
  Tests to ensure that, when the precipitation is below average waterproofing, get_clothes_in_prec does not return an umbrella and raincoat.
  """

  # Arrange
  precipitation_chance = 10
  average_waterproofing = 60

  # Act
  outfit = GenericClothes._get_clothes_in_prec(precipitation_chance, average_waterproofing)

  # Assert
  self.assertEqual(outfit, [])