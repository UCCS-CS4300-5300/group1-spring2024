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
    * Tests 3 param combinations
    """

    # Arrange
    expected_combos = [
      
    ]
  
    # Act 

    # Assert

  
  def test_calculate_heat_index_invalid_inputs(self):
    """
    Tests function calculate_heat_index(temperature, humidity)
    * Tests that calculate_heat_index throws error with invalid input
    """

    pass
  
  def test_calculate_windchill(self):
    """
    Tests function calculate_windchill(temperature, wind_speed)
    * Tests that calculate_windchill returns the correct value 
    * Test 3 param combinations
    """
  
    # Arrange 

    # Act

    # Assert

    pass

  def test_calculate_heat_index_invalid_inputs(self):
    """
    Tests function calculate_windchill(temperature, wind_speed)
    * Tests that calculate_windchill throws errow with invalid input 
    """

    pass