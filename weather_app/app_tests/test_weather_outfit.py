from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from unittest.mock import patch, call
import random
import json
from ..models import GenericClothes
from .. import models
from .. import utils
from .utils import NewDate, NewDatetime

class TestGenericClothesIntegration(TestCase):
  """
  Tests user story: Temperature Based Outfit Generation Per Data Set (Temp, Humidity, Precipitation, Wind) #38 and user story: Temperature Based Outfit Generation #14 at the integration level. 
  """

  maxDiff=None
  fixtures = ['fixture_generic_clothes.json']

  def test_integration_temperature_generation_invalid_inputs(self):
    """
    Have to stub API call since we need to determine what clothes should be worn to ensure the test is repeatable. 
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
    self.assertNotIn('colors_current', context_data)


  # happy paths
  def test_integration_temperature_generation(self):
    """
    Have to stub API call since we need to determine what clothes should be worn to ensure the test is repeatable. 

    Also have to stub the dates since they can change the result of the tests over time.
    """
  
    # arrange
    context = {"tolerance_offset": 5, "working_offset": 10, "location": 10001, "checkbox_colors": "on"}

    # act
    with (
      patch.object(models, 'date', NewDate),
      patch.object(models, 'datetime', NewDatetime),
      patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather_forecast
    ):
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

    expect_outfit = [
      (
        {"image": c0image, "name": c0name}, {"image": c24image, "name": c24name}, {"image": c48image, "name": c48name}
      ) 
          for c0name, c0image, c24name, c24image, c48name, c48image in zip(
        ["Lightweight Rain Hat", "Insulated Long Sleeve", "Fleece-Lined Softshell Pants", "Waterproof Hiking Boots"], 
        ["/media/generic_clothes/Lightweight_Rain_Hat.jpeg", "/media/generic_clothes/Insulated_Long_Sleeve.jpg", "/media/generic_clothes/Fleece-Lined_Softshell_Pants.jpg", "/media/generic_clothes/Waterproof_Hiking_Boots.jpeg"],
        ["Lightweight Rain Hat", "Insulated Long Sleeve", "Fleece-Lined Softshell Pants", "Waterproof Hiking Boots"], 
        ["/media/generic_clothes/Lightweight_Rain_Hat.jpeg", "/media/generic_clothes/Insulated_Long_Sleeve.jpg", "/media/generic_clothes/Fleece-Lined_Softshell_Pants.jpg", "/media/generic_clothes/Waterproof_Hiking_Boots.jpeg"],
        ["Breathable Sun Hat", "Breathable Long Sleeve", "Convertible Cargo Pants", "Breathable Trail Running Shoes"], 
        ["/media/generic_clothes/Breathable_Sun_Hat.jpeg", "/media/generic_clothes/Breathable_Long_Sleeve.jpeg", "/media/generic_clothes/Convertible_Cargo_Pants.jpeg", "/media/generic_clothes/Breathable_Trail_Running_Shoes.jpeg"],
          )
    ]

    expect_rain_outfit = [("Umbrella"), ("Waterproof Tarp")]

    # assert
    self.assertEqual(response.status_code, 200)
    self.assertEqual(context_data['outfit'], expect_outfit)
    self.assertEqual(context_data['colors_current'], ["yellow", "aqua", "skyblue", "coral", "limegreen"])

  
  def test_normal_get_outfit_recommendation(self):
    """
    Tests function get_outfit_recommendation(cls, temperature, humidity, wind, precipitation, tolerance_offset, working_offset).
    * More of a functional or modular test than integration.
    * Happy Test    
    """

    # need to patch to avoid API calls and ensure dates are repeatable
    with (
      patch.object(models, 'date', NewDate),
      patch.object(models, 'datetime', NewDatetime),
      patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather_forecast
    ):
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
      
      # Arrange
      temp = 50
      humidity = 55
      wind = 10
      precipitation = 13
      tolerance_offset = 0
      working_offset = 0
  
      expected_return = {
        "comfort": 46.04,
        "waterproofness": 88.75,
        "outfit": [{"name": name, "image": url} for name, url in zip(['Lightweight Rain Hat', 'Water-Resistant Softshell', 'Water-Resistant Hiking Pants', 'Waterproof Hiking Boots'], ["/media/generic_clothes/Lightweight_Rain_Hat.jpeg", "/media/generic_clothes/Water-Resistant_Softshell.jpeg", "/media/generic_clothes/Water-Resistant_Hiking_Pants.jpeg","/media/generic_clothes/Waterproof_Hiking_Boots.jpeg"])],
        "precipitation_outfit": [],
        "colors": ["yellow", "aqua", "skyblue", "coral", "limegreen"]
      }
  
      # Act
      outfit_recommendation = GenericClothes.get_outfit_recommendation(temp, humidity, wind, precipitation, tolerance_offset, working_offset)
      outfit_recommendation['comfort'] = round(outfit_recommendation['comfort'], 2)
      
      # Assert
      self.assertEqual(outfit_recommendation, expected_return)
  
    
    def test_invalid_get_outfit_recommendation(self):
      """
      Tests function get_outfit_recommendation(cls, temperature, humidity, wind, precipitation, tolerance_offset, working_offset).
      * More of a functional or modular test than integration.
      * Tests with invalid parameters
      * Happy Test    
      """
    
      # Arrange
      temp = 5000
      humidity = 5000
      wind = 10
      precipitation = 13
      tolerance_offset = -10
      working_offset = -10
    
      # Act / Assert
      with self.assertRaises(ValueError):
        outfit_recommendation = GenericClothes.get_outfit_recommendation(temp, humidity, wind, precipitation, tolerance_offset, working_offset)

class TestGenericClothesViewUnit(TestCase):
  """
  Tests user story: 
  1. Temperature Based Outfit Generation Per Data Set (Temp, Humidity, Precipitation, Wind) #38 
  2. Temperature Based Outfit Generation #14 
  3. Location Based Weather Generation Matching #33
  4. Precipitation Based Outfit Generation #44
  5. Rerolling Clothing Recommendations #53

  for the view unit.

  Note that the unit tests overlap a lot between these stories since the same code satisfies all of them. 
  """

  fixtures = ['fixture_generic_clothes.json']

  # ------------------------- recommendation_reroll -------------------------

  def test_view_recommendation_reroll(self):
    """
    Tests that the view calls model function and returns the expected output.
    Assumes valid inputs
    """

    context = {
      "reroll_article": "HAT",
      "comfort_current": "30",
      "comfort_tomorrow": "60",
      "comfort_two_days": "90"
    }

    exptected_temp_reroll_calls = [
      call(30.0, 'HAT'),
      call(60.0, 'HAT'),
      call(90.0, 'HAT')
    ]      

    with patch('weather_app.models.GenericClothes.get_clothes_in_temp_reroll') as mock_temp_reroll:
      mock_temp_reroll.return_value = "Maraqueen Marauder Hat"

      json_response = self.client.get(reverse('reroll'), context)
      json_load_response = json.loads(json_response.content) # converts bytes to dictionary
      
      self.assertEqual(json_response.status_code, 200)      
      self.assertEqual(json_load_response["article_reroll_current"], "Maraqueen Marauder Hat")
      self.assertEqual(json_load_response["article_reroll_tomorrow"], "Maraqueen Marauder Hat")
      self.assertEqual(json_load_response["article_reroll_two_days"], "Maraqueen Marauder Hat")      
      
      mock_temp_reroll.assert_has_calls(exptected_temp_reroll_calls, any_order=False)
  
  def test_view_recommendation_reroll_invalid_inputs(self):
    """
    Tests that the view throws an error.
    Assumes inputs are invalid but all there
    """

    context = {
      "reroll_article": "HAT",
      "comfort_current": "Not a number",
      "comfort_tomorrow": "60",
      "comfort_two_days": "90"
    }

    with patch('weather_app.models.GenericClothes.get_clothes_in_temp_reroll') as mock_temp_reroll:
      mock_temp_reroll.side_effect = ValueError("Invalid temperature")

      json_response = self.client.get(reverse('reroll'), context)
      json_load_response = json.loads(json_response.content) # converts bytes to dictionary

      self.assertEqual(json_response.status_code, 400)      
      self.assertIn("Invalid parameters, error", json_load_response["error"]) 
  
  def test_view_recommendation_reroll_missing_inputs(self):
    """
    Tests that the view has invalid parameters.
    Assumes not all inputs are provided
    """

    context = {
      "reroll_article": "HAT",
      "comfort_current": "30",
      "comfort_tomorrow": "60",
    }

    json_response = self.client.get(reverse('reroll'), context)
    json_load_response = json.loads(json_response.content) # converts bytes to dictionary

    self.assertEqual(json_response.status_code, 400)      
    self.assertIn("Missing parameters", json_load_response["error"]) 
  
  # ---------------------------------------------------------------------------
  
  def test_view_returns_color_when_selected(self):
    """
    Tests that the view returns the colors when the setting is chosen
    """

    with patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather:
      response = self.client.get(reverse('recommendation'), {"working_offset": "0", "tolerance_offset": "0", "checkbox_colors": "on"})

      context_data = response.context
        
      self.assertEqual(response.status_code, 200)
      self.assertIn("colors_current", context_data)
  
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

    with patch('weather_app.models.GenericClothes._calculate_comfort'
               ) as mock_calculate_comfort:
      with patch('weather_app.models.GenericClothes.get_outfit_recommendation'
                 ) as mock_get_clothes_in_range:
        response = self.client.get(reverse('recommendation'), {})

        self.assertEqual(response.status_code, 200)
        mock_calculate_comfort.assert_not_called()
        mock_get_clothes_in_range.assert_not_called()

  def test_view_get_with_params_should_call_model(self):
    """
    Tests that the view returns 200 when correct user input is provided and calls the model methods with stubbed parameters from the get_weather_forcecast function. Also ensures the model has the correct location passed into it.
    """

    with patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather_forecast, patch('weather_app.models.GenericClothes.get_outfit_recommendation') as mock_get_outfit_recommendation:
      mwr = {
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
      
      # Arrange
      mock_get_weather_forecast.return_value = mwr
      tolerance_offset = -10
      working_offset = 10
      
      expected_recommendation_calls = [
        call(mwr['temperature'][x], mwr['humidity'][x], mwr['wind'][x], mwr['precipitation'][x], tolerance_offset, working_offset) for x in range(0, 24, 48)
      ]
      
      expected_weather_calls = [
        call('10001')
      ]
      
      # Act
      response = self.client.get(
          reverse('recommendation'), {
              "working_offset": working_offset,
              "tolerance_offset": tolerance_offset,
              "location": '10001'
          })
      
      self.assertEqual(response.status_code, 200)
      mock_get_outfit_recommendation.assert_has_calls(expected_recommendation_calls, any_order=False)
      mock_get_weather_forecast.assert_has_calls(expected_weather_calls, any_order=False)

  
  def test_view_get_with_invalid_params_should_throw_error(self):
    """
    Tests that the view returns 200 when incorrect user input is provided and includes an error passed to the template.
    """

    # Patching to prevent API calls, don't care about anything else
    with patch('weather_app.models.Weather.get_weather_forecast') as mock_get_weather_forecast:
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
  Tests user stories: 
  * Temperature Based Outfit Generation Per Data Set (Temp, Humidity, Precipitation, Wind) #38 
  * Temperature Based Outfit Generation #14
  * Precipitation Based Outfit Generation #44
  * Rerolling Clothing Recommendations #53

  Note that the unit tests overlap with the model so it did not make much sense to separate the classes. 
  """

  fixtures = ['fixture_generic_clothes.json']


  # --------------------------- get_outfit_recommendation ---------------------------

  def get_clothes_in_temp_reroll(self):
    """
    Tests that the get_clothes_in_temp_reroll(cls, comfort, type)
    function returns a correct outfit reroll based on the type.
    """

    comfort = 50
    type = 'HAT'
    expected_return = (
      {
        "image": "/media/generic_clothes/Cotton_Baseball_Cap.jpeg",
        "name": "Cotton Baseball Cap"
      }, 10
    )

    with patch('random.randint') as mock_randit:
      mock_randit.return_value = lambda : 1
      
      rerolled_outfit = get_clothes_in_temp_reroll(comfort, type)
      self.assertEqual(rerolled_outfit, expected_return)

  def get_clothes_in_temp_comfort_out_of_range(self):
    """
    Tests that the get_clothes_in_temp_reroll(cls, comfort, type)
    function returns a ValueError when the comfort is invalid.
    """

    comfort = 50000000
    type = 'HAT'
    
    with self.assertRaises(ValueError):
      rerolled_outfit = get_clothes_in_temp_reroll(comfort, type)

  def get_clothes_in_temp_wrong_type(self):
    """
    Tests that the get_clothes_in_temp_reroll(cls, comfort, type)
    function returns a correct outfit reroll based on the type.
    """

    comfort = 50
    type = 'NOT'

    with self.assertRaises(ValueError):
      rerolled_outfit = get_clothes_in_temp_reroll(comfort, type)
  
  # ---------------------------------------------------------------------------------
  
  
  # --------------------------- save ---------------------------

  def test_save(self):
    """
    Tests that the save method properly assigns a default image.
    """

    # Arrange
    new_clothes = GenericClothes(name="Logan's Shirt", clothing_type="SHR", comfort_low=60, comfort_high=100, waterproof_rating=60)

    # Act
    new_clothes.save()

    # Assert
    self.assertEqual(new_clothes.image, 'generic_clothes/default-shirt.png')

  
  def test_save_default(self):
    """
    Tests that the save method properly assigns a default image.
    """

    # Arrange
    new_clothes = GenericClothes(name="Logan's Shirt", clothing_type="MSC", comfort_low=60, comfort_high=100, waterproof_rating=60)

    # Act
    new_clothes.save()

    # Assert
    self.assertEqual(new_clothes.image, 'generic_clothes/default.png')
  
  # --------------------------- get_outfit_recommendation ---------------------------
  
  def test_get_outfit_recommendation(self):
    """
    Tests function get_outfit_recommendation(cls, temperature, humidity, wind, precipitation, tolerance_offset, working_offset).
    * Tests that the leaf functions are correctly called and returns the correct returned information
    * This function really doesn't have much functionality, so only 1 test
    * Happy Test    
    """

    # https://stackoverflow.com/questions/43130969/are-multiple-with-statements-on-one-line-equivalent-to-nested-with-statement
    with (
      patch('weather_app.models.GenericClothes._calculate_comfort') as mock_cc,
      patch('weather_app.models.GenericClothes._get_clothes_in_temp') as mock_temp,
      patch('weather_app.models.GenericClothes._get_clothes_in_prec') as mock_prec,
      patch('weather_app.models.GenericClothes._get_color_palette') as mock_color
    ):

      # Arrange
      temp = 50
      humidity = 55
      wind = 10
      precipitation = 13
      tolerance_offset = 0
      working_offset = 0

      test_clothe_1 = GenericClothes(name="test_clothe_1", clothing_type = "HAT", comfort_low = 10, comfort_high = 20, waterproof_rating = 10)
      test_clothe_1.save()

      test_clothe_2 = GenericClothes(name="test_clothe_2", clothing_type = "MSC", comfort_low = 10, comfort_high = 20, waterproof_rating = 100)
      test_clothe_2.save()
      
      test_outfit_1 = GenericClothes.objects.filter(id=test_clothe_1.id) # needs to be queryset, not object
      test_outfit_2 = GenericClothes.objects.filter(id=test_clothe_2.id)

      mock_cc.return_value = 10
      mock_temp.return_value = (test_outfit_1, 100)
      mock_prec.return_value = test_outfit_2
      mock_color.return_value = ['some colors']

      mock_cc_calls = [call(temp, humidity, wind, tolerance_offset, working_offset)]
      mock_temp_calls = [call(mock_cc.return_value)]
      mock_prec_calls = [call(precipitation, mock_temp.return_value[1])]
      expected_return = {
        "comfort": mock_cc.return_value,
        "waterproofness": mock_temp.return_value[1],
        "outfit": [{"name": test_clothe_1.name, "image": "/media/generic_clothes/default-hat.png"}],
        "precipitation_outfit": [{"name": test_clothe_2.name, "image": "/media/generic_clothes/default.png"}],
        "colors": ['some colors']
      }
      
      # Act
      outfit_recommendation = GenericClothes.get_outfit_recommendation(temp, humidity, wind, precipitation, tolerance_offset, working_offset)

      # Assert
      self.assertEqual(outfit_recommendation, expected_return)
      mock_cc.assert_has_calls(mock_cc_calls, any_order=False)
      mock_temp.assert_has_calls(mock_temp_calls, any_order=False)
      mock_prec.assert_has_calls(mock_prec_calls, any_order=False)
      mock_color.assert_called()
  
  # ---------------------------------------------------------------------------------

  # --------------------------- _get_clothes_in_temp ---------------------------
  
  def test_cold__get_clothes_in_temp(self):
    """
    Tests function _get_clothes_in_temp(cls, comfort, precipitation_chance).
    * Tests that a set of clothes is returned when the comfort is cold (11 degrees)
    * Happy Test
    """

    # Arrange
    comfort = 11

    # Act
    outfit, water_avg = GenericClothes._get_clothes_in_temp(comfort)
    outfit_names = [clothes.name for clothes in outfit]

    # Assert
    self.assertEqual(len(outfit), 4)
    self.assertEqual(outfit_names, [
        "Wool Beanie", "Heavy Wool Sweater", "Thermal Wool Trousers",
        "Waterproof Hiking Boots"
    ])
    self.assertEqual(water_avg, 51.25)

  
  def test_normal__get_clothes_in_temp(self):
    """
    Tests function _get_clothes_in_temp(cls, comfort, precipitation_chance).
    * Tests that a set of clothes is returned when the comfort is normal (60 degrees) with chance of rain
    * Happy Test    
    """
    
    # Arrange
    comfort = 60
  
    outfit, water_avg = GenericClothes._get_clothes_in_temp(comfort)
    outfit_names = [clothes.name for clothes in outfit]

    self.assertEqual(len(outfit), 4)
    self.assertEqual(outfit_names, [
        "Breathable Sun Hat", "Breathable Long Sleeve",
        "Convertible Cargo Pants", "Breathable Trail Running Shoes"
    ])
    self.assertEqual(water_avg, 21.25)

  
  def test_hot__get_clothes_in_temp(self):
    """
    Tests function _get_clothes_in_temp(cls, comfort, precipitation_chance).
    * Tests that a set of clothes is returned when the comfort is hot (105 degrees) with chance of rain
    * Happy Test    
    """
  
    # Arrange
    comfort = 105
  
    outfit, water_avg = GenericClothes._get_clothes_in_temp(comfort)
    outfit_names = [clothes.name for clothes in outfit]

    self.assertEqual(len(outfit), 4)
    self.assertEqual(outfit_names, [
        "Ultra-light Running Cap", "Mesh Ventilated Running Shirt",
        "Ventilated Mesh Shorts", "Ventilated Mesh Sandals"
    ])
    self.assertEqual(water_avg , 10)

  
  def test_invalid_temp__get_clothes_in_temp(self):
    """
    Tests function _get_clothes_in_temp(cls, comfort, precipitation_chance).
    * Tests that no set of clothes is returned when the comfort is something unreasonable (e.g. 20000 degrees).
    * Sad Test    
    """

    with self.assertRaises(ValueError):
      GenericClothes._get_clothes_in_temp(20000)
      GenericClothes._get_clothes_in_temp(-5000)

  # ---------------------------------------------------------------------------------

  # --------------------------- _get_clothes_in_prec ---------------------------

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
    outfit_names = [clothes.name for clothes in outfit]
    
    # Assert
    self.assertEqual(outfit_names, ["Umbrella", "Waterproof Tarp"])

  def test_get_clothes_in_prec_middle(self):
    """
    Tests to ensure that, when the precipitation is the same as average waterproofing, get_clothes_in_prec returns an umbrella and raincoat.
    """

    # Arrange
    precipitation_chance = 50
    average_waterproofing = 50

    # Act
    outfit = GenericClothes._get_clothes_in_prec(precipitation_chance, average_waterproofing)
    outfit_names = [a.name for a in outfit]
    
    # Assert
    self.assertEqual(outfit_names, ["Umbrella", "Waterproof Tarp"])

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
  
  # ---------------------------------------------------------------------------------

  # --------------------------- _calculate_comfort ---------------------------
  
  def test_calculate_comfort_modular_test(self):
    """
    Modular test for _calculate_comfort
    Tests to ensure it calls the utils functions
    """
    test_data = [70, 50, 10, 5, 3, 68.825]
    comfort_params = test_data[0:5]
    expected = test_data[5]
    comfort = GenericClothes._calculate_comfort(*comfort_params)
    self.assertAlmostEqual(comfort, expected, places=2)
  
  def test_calculate_comfort_invalid_working_tolerance(self):
    """
    Test working_offset is not less than 0. Sad
    """

    with patch('utils.calculate_heat_index') as chi, self.assertRaises(ValueError):
      chi.side_effect = ValueError()
      GenericClothes._calculate_comfort(temperature=76,
                                       humidity=1,
                                       wind_speed=10,
                                       tolerance_offset=10,
                                       working_offset=-10)

  def test_calculate_comfort_invalid_windspeed(self):
    """
    Test that wind speed is not less than 0. Sad
    """

    with self.assertRaises(ValueError):
      GenericClothes._calculate_comfort(temperature=70,
                                       humidity=1,
                                       wind_speed=-10,
                                       tolerance_offset=0,
                                       working_offset=0)

  def test_calculate_comfort_invalid_humidity(self):
    """
    Test that humidity is not less than 0. Sad
    Why are we not patching the helper function?
    Modular test
    """
    
    with self.assertRaises(ValueError):
      GenericClothes._calculate_comfort(temperature=76,
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

    with patch('utils.calculate_windchill') as cwc:
      for test_params in test_data:
        cwc.return_value = test_params[5]
        with self.subTest():
          comfort_params = test_params[0:5]
          expected = test_params[5]
          comfort = GenericClothes._calculate_comfort(*comfort_params)
          self.assertAlmostEqual(comfort, expected, places=2)

  def test_calculate_comfort_high_temp(self):
    """
    Test that calculate_comfort uses the heat index calculation 
    * when the temperature is greater than 75. 
    * Happy
    """

    # in format of (temperature, humidity, wind_speed, tolerance_offset, working_offset, expected comfort)
    # https://gist.github.com/aipi/99ed2c992be41be437bb9506de73cb44
    test_data = [(80, 60, 5, 0, 0, 81.811), (76, 65, 15, 2, 4, 79.869)]

    with patch('utils.calculate_heat_index') as chi:
      for test_params in test_data:
        chi.return_value = test_params[5]
        with self.subTest():
          comfort_params = test_params[0:5]
          expected = test_params[5]
          comfort = GenericClothes._calculate_comfort(*comfort_params)
          self.assertAlmostEqual(comfort, expected, places=2)

  # ---------------------------------------------------------------------------------

  # --------------------------- clean ---------------------------
  
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

  # ---------------------------------------------------------------------------------

 