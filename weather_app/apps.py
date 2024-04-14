"""Custom settings for weather_app project."""

from django.apps import AppConfig


class WeatherAppConfig(AppConfig):
  """
  Settings for the weather app.
  """
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'weather_app'
