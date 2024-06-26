"""
Tests the utils.py function in the application. This is not test utilities.
"""

from django.test import TestCase
from .. import utils

class TestUtilsUnit(TestCase):
  """
  Tests the utils.py function.
  """

  def test_calculate_heat_index(self):
    """
    Tests function calculate_heat_index(temperature, humidity)
    * Tests that calculate_heat_index returns the correct value
    * Tests 2 param combinations
    """

    # Arrange
    expected_combos = [
      (80, 60, 81.810922),
      (76, 65, 77.868598)
    ]
  
    # Act 
    for combo in expected_combos:
      result = utils.calculate_heat_index(combo[0], combo[1])

      # Assert
      self.assertAlmostEqual(result, combo[2], places=3)
      
  
  def test_calculate_heat_index_invalid_inputs(self):
    """
    Tests function calculate_heat_index(temperature, humidity)
    * Tests that calculate_heat_index throws error with invalid input
    """

    temperature = 80
    humidity = -1
    
    with self.assertRaises(ValueError):
      utils.calculate_heat_index(temperature, humidity)
  
  def test_calculate_windchill(self):
    """
    Tests function calculate_windchill(temperature, wind_speed)
    * Tests that calculate_windchill returns the correct value 
    * Test 2 param combinations
    """
  
    # Arrange
    expected_combos = [
      (41, 10, 34.881974),
      (51, 10, 47.276229)
    ]

    # Act 
    for combo in expected_combos:
      result = utils.calculate_windchill(combo[0], combo[1])

      # Assert
      self.assertAlmostEqual(result, combo[2], places=3)
      

  def test_calculate_windchill_invalid_inputs(self):
    """
    Tests function calculate_windchill(temperature, wind_speed)
    * Tests that calculate_windchill throws errow with invalid input 
    """

    temperature = 80
    wind_speed = -1

    with self.assertRaises(ValueError):
      utils.calculate_windchill(temperature, wind_speed)

  def test_get_xth_hour_weather(self):
    """
    Tests function get_xth_hour_weather(hour, weather_data)
    """

    weather_data = {
      "temperature": [80, 81, 82, 83, 84],
      "humidity": [60, 61, 62, 63, 64],
      "wind": [10, 11, 12, 13, 14], 
      "precipitation": [1, 2, 3, 4, 5]
    }

    results = utils.get_xth_hour_weather(2, weather_data)

    self.assertEqual(results, [82, 62, 12, 3])

  def test_get_xth_hour_weather_invalid_inputs(self):
    """
    Tests function get_xth_hour_weather(hour, weather_data)
    """
  
    weather_data = {
      "temperature": [80, 81, 82, 83, 84],
      "humidity": [60, 61, 62, 63, 64],
      "wind": [10, 11, 12, 13, 14], 
      "precipitation": [1, 2, 3, 4, 5]
    }

    with self.assertRaises(ValueError):
      results = utils.get_xth_hour_weather(20, weather_data)
  