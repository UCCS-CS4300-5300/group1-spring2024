from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import Weather, GenericClothes
from datetime import datetime

class TemperatureView(View):
  """
  Class to manage the connection to the temperature recommendation service.
  """

  def get(self, request):
    """
    Using a get request since the action does not affect persistent data
    """

    tolerance_offset = int(request.GET.get('tolerance_offset'))
    working_offset = int(request.GET.get('working_offset'))
    location = request.GET.get('location') # included in the sidebar?

    context = {
      "outfit": [], 
      "comfort": []
    }
    
    # User inputted the form
    if tolerance_offset and working_offset:
      # TODO - Change this out to get the cached current weather data for the user's location
      weather_data = Weather.get_weather_forecast(location)

      if weather_data:
        current_temp = int(weather_data['temperature'][0])
        current_humidity = int(weather_data['humidity'][0])
        current_wind_speed = int(weather_data['wind'][0])
        current_precipitation = int(weather_data['precipitation'][0])

        comfort = GenericClothes.calculate_comfort(current_temp, current_humidity, current_wind_speed, tolerance_offset, working_offset)
        outfit = GenericClothes.get_clothes_in_range(comfort)

        context["outfit"] = outfit
        context["comfort"] = comfort
        context["tolerance_offset"] = tolerance_offset  # used as "caches" for the templates
        context["working_offset"] = working_offset      

    print(f"here {context}")
    
    return render(request, 'weather_app/recommendation.html', context)
      

    
    

# index home page
class WeatherView(View):

  def get(self, request):
    # get location from request, e.g. /?location=80918
    location = request.GET.get('location')

    # get weather data
    weather_data = Weather.get_weather_forecast(location)

    # template is expecting dictionary with following values
    context = {
        'temp_forecast': weather_data['temperature'],
        'precipitation_forecast': weather_data['precipitation'],
        'humidity_forecast': weather_data['humidity'],
        'wind_forecast': weather_data['wind'],
        'day_forecast': weather_data['hours'][:24],
    }

    return render(request, 'weather_app/index.html', context)

    # # I COMMENTED THIS OUT FOR THE TIME BEING, CHANGE IT BACK WHEN YOU WORK ON IT

  # # I DO NOT THINK THIS FUNCTIONALITY IS NEEDED FOR SPRINT0-3, BUT MAY BE INTERESTING FOR ITERATION 1 :)!
  # def get(self, request):
  #   # filter by day and location
  #   # day is implied to be today
  #   # location depends on how the frontend sends it

  #   photo_path = weather.photo.path # path to image folder
  #   # switch for pulling images of the weather
  #   match weather_type:
  #     case "Sunny":
  #       weather.photo.name = "images/sunny.jpg"
  #     case "Cloudy":
  #       weather.photo.name = "images/cloudy.jpg"
  #     case "Partly Cloudy":
  #       weather.photo.name = "images/partly-cloudy.jpg"
  #     case "Rain":
  #       weater.photo.name = "images/rain.jpg"
  #     case "Snow":
  #       weather.photo.name = "images/snow.jpg"
  #     case "Thunderstorm":
  #       weather.photo.name = "images/thunderstorm.jpg"
  #     case "Hail":
  #       weather.photo.name = "images/hail.jpg"
  #     case "Fog":
  #       weather.photo.name = "images/fog.jpg"

  #   new_path = settings.MEDIA.ROOT + weather.photo.name
  #   os.rename(photo_path, new_path) # moves the file on the file system
  #   weather.save()
  #   weather.photo.path == new_path

  #   #location = request.GET.get('location') # Get location from request body
  #   # Parse it into whatever format we need to filter our weather by

  #   # Below assumes we pull weather for the whole day but we can modify it later as needed by changing the timedelta values
  #   # idk how to filter location yet since we don't know how it'll be stored
  #   weather_lower_bound = datetime.date.today()
  #   weather_upper_bound = datetime.date.today() + datetime.datetime.timedelta(days=1)
  #   weather_list = Weather.objects.filter(date__range=(weather_lower_bound, weather_upper_bound).filter(location=location))

  #   return render(request, 'weather_app/templates/weather_app/weather.html', {'weather_list': weather_list})
