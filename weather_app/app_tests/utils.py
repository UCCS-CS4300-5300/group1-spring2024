"""Holds some mocking classes needed for a few of the color tests."""

import datetime

class NewDate(datetime.date):
  """Mocks datetime.date.today to return specified date"""
  @classmethod
  def today(cls, date):
    """
    Ex date is [2022, 7, 22]
    """
    return cls(2022, 7, 22)

class NewDatetime(datetime.datetime):
  """Mocks datetime.date.now to always return specified date and time"""
  @classmethod
  def now(cls):
    """
    Ex time is [2022, 7, 22, 12, 0, 0, 0] for July 22, 2022 at 12:00:00
    """
    return cls(2022, 7, 22, 12, 0, 0, 0)
