"""
Utility functions for calculating generic weather information.
"""

def calculate_heat_index(temperature, humidity):
  """
  Calculates the heat index.
  * Equation: https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
  * Humidity must be >= 0
  * Temperature in F, humidity in %
  """
  
  if humidity < 0:
    raise ValueError("Humidity must be greater than or equal to 0.")
  
  return -42.379 + 2.04901523 * temperature + 10.14333127 * humidity - 0.22475541 * temperature * humidity - 0.00683783 * temperature * temperature - 0.05481717 * humidity * humidity + 0.00122874 * temperature * temperature * humidity + 0.00085282 * temperature * humidity * humidity - 0.00000199 * temperature * temperature * humidity * humidity


def calculate_windchill(temperature, wind_speed):
  """
  Calculates the windchill.
  * Equation: https://en.wikipedia.org/wiki/Wind_chill NA wind chill index
  * Wind speed must be >= 0
  * Temperature in F, wind speed in mph
  """

  if wind_speed < 0:
    raise ValueError("Wind speed must be greater than or equal to 0.")
  
  return 35.74 + 0.6215 * temperature - 35.75 * (
    wind_speed**0.16) + 0.4275 * temperature * (wind_speed**0.16)