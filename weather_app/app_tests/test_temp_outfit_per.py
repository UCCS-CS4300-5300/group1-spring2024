from typing import Generic
from django.test import TestCase
from ..models import GenericClothes
from datetime import datetime
from django.utils.timezone import make_aware
from django.core.exceptions import ObjectDoesNotExist, ValidationError


# Based on https://docs.djangoproject.com/en/5.0/topics/testing/tools/#provided-test-case-classes
# TestCase is based on unittest
class TestGenericClothes(TestCase):
  fixtures = ['fixture_generic_clothes.json']

  def test_get_clothes_in_range_normal(self):
    """
    Tests that a set of clothes is returned when the comfort is something reasonable (e.g. 60 degrees). Happy.
    """

    outfit = GenericClothes.get_clothes_in_range(60)
    outfit_names = [clothes.name for clothes in outfit]
    
    self.assertEqual(len(outfit), 4)
    self.assertEqual(outfit_names, ["Cotton Baseball Cap", "Breathable Long Sleeve", "Convertible Cargo Pants", "Breathable Trail Running Shoes"])

  def test_get_clothes_in_range_invalid(self):
    """
    Tests that no set of clothes is returned when the comfort is something unreasonable (e.g. 2000 degrees) Sad.
    """

    outfit = GenericClothes.get_clothes_in_range(2000)
    outfit_names = [clothes.name for clothes in outfit]

    self.assertEqual(len(outfit), 0)
    self.assertEqual(outfit_names, [])
  
  def test_calculate_comfort_invalid_tolerances(self):
    """
    Test that some combination of the tolerance_offset or working_offset is not less than 0. Sad
    """

    with self.assertRaises(ValueError):
      GenericClothes.calculate_comfort(temperature=75,
                                       humidity=1,
                                       wind_speed=10,
                                       tolerance_offset=-10,
                                       working_offset=10)

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
