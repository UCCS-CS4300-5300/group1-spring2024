from django.test import TestCase
from ..models import GenericClothes
import datetime
from unittest.mock import patch, call, Mock
from .. import models

class TestColorGenerationUnit(TestCase):
  """
  Tests user story: Color Based Outfit Generation #46 
  """

  fixtures = ['fixture_generic_clothes.json']

  # --------------------------- _get_color_palette ---------------------------

  def test_summer__get_color_palette(self):
    """
    Tests function _get_color_palette(cls).
    * Tests that it returns the correct list based on the season
    * Happy Test    

    This test took me 5x as long to write the actual function.
    """

    class NewDate(datetime.date):
      @classmethod
      def today(cls):
        return cls(2022, 7, 22)

    class NewDatetime(datetime.datetime):
      @classmethod
      def now(cls):
        mock_datetime = cls(2022, 7, 22, 12, 0, 0, 0)
        return mock_datetime
    
    expected_color = ["yellow", "aqua", "skyblue", "coral", "limegreen"]

    # https://stackoverflow.com/questions/16134281/python-mocking-a-function-from-an-imported-module
    # https://docs.python.org/3/library/unittest.mock.html#patch-object
    # https://stackoverflow.com/questions/4481954/trying-to-mock-datetime-date-today-but-not-working/25652721#25652721
    # Need the patch to avoid "Error '<=' not supported between instances of 'MagicMock' and 'datetime.date'"
    
    with (
      patch.object(models, 'date', NewDate),
      patch.object(models, 'datetime', NewDatetime)
    ):

      color = GenericClothes._get_color_palette()
      self.assertEqual(color, expected_color)

  def test_autumn__get_color_palette(self):
    """
    Tests function _get_color_palette(cls).
    * Tests that it returns the correct list based on the season
    * Happy Test    

    This test took me 5x as long to write the actual function.
    """

    class NewDate(datetime.date):
      @classmethod
      def today(cls):
        return cls(2022, 10, 22)

    class NewDatetime(datetime.datetime):
      @classmethod
      def now(cls):
        mock_datetime = cls(2022, 10, 22, 12, 0, 0, 0)
        return mock_datetime

    expected_color = ["orange", "red", "brown", "goldenrod", "olive"]

    # https://stackoverflow.com/questions/16134281/python-mocking-a-function-from-an-imported-module
    # https://docs.python.org/3/library/unittest.mock.html#patch-object
    # https://stackoverflow.com/questions/4481954/trying-to-mock-datetime-date-today-but-not-working/25652721#25652721
    # Need the patch to avoid "Error '<=' not supported between instances of 'MagicMock' and 'datetime.date'"

    with (
      patch.object(models, 'date', NewDate),
      patch.object(models, 'datetime', NewDatetime)
    ):

      color = GenericClothes._get_color_palette()
      self.assertEqual(color, expected_color)
    
  # ---------------------------------------------------------------------------------