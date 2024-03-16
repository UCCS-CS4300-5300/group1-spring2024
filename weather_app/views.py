from django.shortcuts import render
from django.http import JsonResponse
from django.views import View, generic
from django.contrib import messages
from .models import Weather, GenericClothes
from datetime import datetime
from rest_framework import status

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import CreateUserForm
from typing import Any

class TemperatureView(View):
  """
  Class to manage the connection to the temperature recommendation service.
  """

  def get(self, request):
    """
    Using a get request since the action does not affect persistent data. Based on this tutorial with django   (https://docs.djangoproject.com/en/5.0/topics/forms/)
    """

    tolerance_offset = request.GET.get('tolerance_offset')
    working_offset = request.GET.get('working_offset')
    location = request.GET.get('location') # included in the sidebar?

    context = {}
    
    # User inputted the form
    if tolerance_offset and working_offset:
      try:
        
        tolerance_offset = int(tolerance_offset)
        working_offset = int(working_offset)
        
        weather_data = Weather.get_weather_forecast(location)

        # All of this is formatting the weather data to be calculated in the comfort, which then gets the outfits, which then is rendered.
        # Really no business logic is here, except getting the data in the proper form.
      
        current_weather_data = [
          int(weather_data[x][0]) for x in ['temperature', 'humidity', 'wind', 'precipitation']
        ]

        six_hours_weather_data = [
          int(weather_data[x][6]) for x in ['temperature', 'humidity', 'wind', 'precipitation']
        ]

        twelve_hours_weather_data = [
          int(weather_data[x][12]) for x in ['temperature', 'humidity', 'wind', 'precipitation']
        ]

        # asterisk unpacks the array
        comfort_current = GenericClothes.calculate_comfort(*current_weather_data[:3], tolerance_offset, working_offset)
        comfort_six_hours = GenericClothes.calculate_comfort(*six_hours_weather_data[:3], tolerance_offset, working_offset)
        comfort_twelve_hours = GenericClothes.calculate_comfort(*twelve_hours_weather_data[:3], tolerance_offset, working_offset)
        
        outfit_current, rain_outfit_current, avg_waterproofing_current = GenericClothes.get_clothes_in_range(comfort_current, current_weather_data[3])
        outfit_six_hours, rain_outfit_six_hours, avg_waterproofing_six_hours = GenericClothes.get_clothes_in_range(comfort_six_hours, six_hours_weather_data[3])
        outfit_twelve_hours, rain_outfit_twelve_hours, avg_waterproofing_twelve_hours = GenericClothes.get_clothes_in_range(comfort_twelve_hours, twelve_hours_weather_data[3])

        context["waterproofing_current"] = avg_waterproofing_current
        context["waterproofing_six_hours"] = avg_waterproofing_six_hours
        context["waterproofing_twelve_hours"] = avg_waterproofing_twelve_hours

        context["rain_outfit_current"] = rain_outfit_current
        context["rain_outfit_six_hours"] = rain_outfit_six_hours
        context["rain_outfit_twelve_hours"] = rain_outfit_twelve_hours
    
        context["outfit_current"] = [clothe.name for clothe in outfit_current]
        context["outfit_six_hours"] = [clothe.name for clothe in outfit_six_hours]
        context["outfit_twelve_hours"] = [clothe.name for clothe in outfit_twelve_hours]

        context["comfort_current"] = round(comfort_current, 2)
        context["comfort_six_hours"] = round(comfort_six_hours, 2)
        context["comfort_twelve_hours"] = round(comfort_twelve_hours, 2)
              
      except Exception as e:
        context["error"] = f"Error, please try again. Error message: {e}"
    
    return render(request, 'weather_app/recommendation.html', context)
  
class GenericClothesListView(generic.ListView):
  model = GenericClothes
      
class GenericClothesDetailView(generic.DetailView):
  model = GenericClothes

  def get_context_data(self, **kwargs):
    context = super(GenericClothesDetailView, self).get_context_data(**kwargs)
    context['genericclothes'] = GenericClothes.objects.filter(genericclothes=context['genericclothes'])
    return context 

# index home page
class WeatherView(View):

  def get(self, request):
    # get location from request, e.g. /?location=80918
    location = request.GET.get('location')

    # get weather data
    weather_data = Weather.get_weather_forecast(location)

    if(weather_data):
      # template is expecting dictionary with following values
      context = {
          'temp_forecast': weather_data['temperature'],
          'precipitation_forecast': weather_data['precipitation'],
          'humidity_forecast': weather_data['humidity'],
          'wind_forecast': weather_data['wind'],
          'day_forecast': weather_data['hours'][:24],
          'location' : weather_data['location']
      }
  
      return render(request, 'weather_app/index.html', context)
    else:
      return render(request, status=status.HTTP_206_PARTIAL_CONTENT, template_name='weather_app/index.html', context={'error_message': 'Please enter a valid zip code'})

#register for an account
class RegisterUser(View):
  #handle get request
  def get(self, request):
    #create a form instance and populate it with data from the request
    form = CreateUserForm()
    context = {'form': form} #context is used to pass data to the template
    return render(request, 'registration/register.html', context) #render request for html

  #handle post request
  def post(self, request):
    form = CreateUserForm()
    if request.method == 'POST':
      form = CreateUserForm(request.POST)
      if form.is_valid():
        user = form.save()
        username = form.cleaned_data.get('username')
        #create a new group for the user so that things can be admin access only
        group = Group.objects.get(name='user__role')
        user.groups.add(group) 

        messages.success(request, 'Account was created for ' + username)
        return redirect('login') #after successful registration, redirect to login page
    context = {'form': form}
    return render(request, 'registration/register.html', context) 

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
