import logging
from itertools import zip_longest
from rest_framework import status
import boto3

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib import messages
from .models import Weather, GenericClothes, AppUser
from .forms import CreateUserForm, AddForm
from .decorators import allowed_users
from datetime import datetime

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import logging
logger = logging.getLogger("test_logger")

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
    location = request.GET.get('location') # included in the sidebar
    color_selected = request.GET.get('checkbox_colors')

    context = {}

    # User inputted the form
    if tolerance_offset and working_offset:
      try:

        tolerance_offset = int(tolerance_offset)
        working_offset = int(working_offset)
        
        weather_data = Weather.get_weather_forecast(location)

        if not weather_data:
          return render(request, status=status.HTTP_206_PARTIAL_CONTENT, template_name='weather_app/recommendation.html', context={'error': 'Please enter a valid location'})

        
        # All of this is formatting the weather data to be calculated in the comfort, which then gets the outfits, which then is rendered.
        # Really no business logic is here, except getting the data in the proper form.

        current_weather_data = [
          int(weather_data[x][0]) for x in ['temperature', 'humidity', 'wind', 'precipitation']
        ]

        next_weather_data = [
          int(weather_data[x][24]) for x in ['temperature', 'humidity', 'wind', 'precipitation']
        ]

        final_hours_weather_data = [
          int(weather_data[x][48]) for x in ['temperature', 'humidity', 'wind', 'precipitation']
        ]

        current = GenericClothes.get_outfit_recommendation(*current_weather_data, tolerance_offset, working_offset)
        next = GenericClothes.get_outfit_recommendation(*next_weather_data, tolerance_offset, working_offset)
        final = GenericClothes.get_outfit_recommendation(*final_hours_weather_data, tolerance_offset, working_offset)

        context["waterproofing_current"] = current['waterproofness']
        context["waterproofing_six_hours"] = next['waterproofness']
        context["waterproofing_twelve_hours"] = final['waterproofness']

        context["comfort_current"] = round(current['comfort'], 2)
        context["comfort_six_hours"] = round(next['comfort'], 2)
        context["comfort_twelve_hours"] = round(final['comfort'], 2)

        context["outfit"] = [(c0a, c6a, c12a) for c0a, c6a, c12a in zip(current['outfit'], next['outfit'], final['outfit'])]

        context["rain_outfit"] = [(c0a, c6a, c12a) for c0a, c6a, c12a in zip_longest(current['precipitation_outfit'], next['precipitation_outfit'], final['precipitation_outfit'], fillvalue="Missing...")]

        if color_selected:
          context["colors_current"] = current['colors']

      except Exception as e:
        context["error"] = f"Error, please try again. Error message: {e}"

    return render(request, 'weather_app/recommendation.html', context)


class GenericClothesListView(View):
  """
  Class to manage the inventory view for the GenericClothes model
  """
  model = GenericClothes

  def transform_field_name(self, field_name):
    return field_name.capitalize().replace("_", " ")
    
  @method_decorator(login_required(login_url='login'), name='dispatch')
  @method_decorator(allowed_users(allowed_roles=['user']))
  def get(self, request, *args, **kwargs): # previously def get(self, request, *args, **kwargs): 
    # user = get_object_or_404(AppUser, pk=user_id)
    
    """
    Get inventory data
    """
    #DATA FOR TESTING
    # test_cloth = self.model(name="nade", clothing_type="SHO", comfort_low=10, comfort_high=20, waterproof_rating=400)
    # test_cloth.save()
    
    # Get field model names for the context so frontend knows what options we can query clothing by
    context = {}
    field_name = request.GET.get('filterBy')
    if field_name == None:
      field_name = "name" # If no filter is provided sort by name by default
    logger.debug(field_name)
    fields = self.model._meta.get_fields()
    
    context["generic_clothes_fields"] = [field.name for field in fields] # Only send field names to make filtering easier on frontend
    context['genericclothes'] = self.model.objects.all().order_by(field_name)
    return render(request, 'weather_app/genericclothes_list.html', context)
      
# class GenericClothesDetailView(generic.DetailView):
#   model = GenericClothes
#   template = "/weather_app/generic_clothes_detail.html"
#   context_object_name = "objects"

#   def get_queryset(self):
#     filter_param = request.GET.get('filterBy')
#     queryset = super().get_queryset()
#     if filter_param:
#       queryset = queryset.filter(your_field=filter_param)
#     return queryset

# index home page
class WeatherView(View):

  def get(self, request):
    
    # get location from request, e.g. /?location=80918
    location = request.GET.get('location')

    # get weather data
    weather_data = Weather.get_weather_forecast(location)

    if weather_data:
      # template is expecting dictionary with following values
      context = {
          'temp_forecast': weather_data['temperature'],
          'precipitation_forecast': weather_data['precipitation'],
          'humidity_forecast': weather_data['humidity'],
          'wind_forecast': weather_data['wind'],
          'day_forecast': weather_data['hours'][:24],
          'location' : weather_data['location'],
      }

      return render(request, 'weather_app/index.html', context)
    else:
      return render(request, status=status.HTTP_206_PARTIAL_CONTENT, template_name='weather_app/index.html', context={'error_message': 'Please enter a valid location'})

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
        group = Group.objects.get_or_create(name='user')[0] # used to be user__role
        user.groups.add(group)

        app_user = AppUser.objects.create(username=username)

        messages.success(request, 'Account was created for ' + username)
        return redirect('login') #after successful registration, redirect to login page
    context = {'form': form}
    return render(request, 'registration/register.html', context) 

#adds items to inventory
def addItem(request):
    form = AddForm()

    if request.method == 'POST':

      form = AddForm(request.POST,  request.FILES)
      
      if form.is_valid():
        image_file = request.FILES['photo']
        timestamp = datetime.now().strftime('%Y%m%d')

        # Upload the image to S3
        s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        image_path = f'inventory/photos/{image_file.name}_{timestamp}'

        try:
            s3.upload_fileobj(image_file, os.getenv('AWS_STORAGE_BUCKET_NAME'), image_path)
        except Exception as e:
            # Handle the exception, perhaps log it
            print(f"Error uploading image to S3: {e}")
            return render(request, 'weather_app/error.html', {'message': 'Error uploading image. Please try again.'})

        # Generate the image URL
        image_url = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/{image_path}"

        # Save the image URL to the form
        form.instance.image_url = image_url
        form.instance.photo = None
        post = form.save(commit=False)
        post.save()

        return redirect('inventory')

    context = {'form': form}
    return render(request, 'weather_app/add_item.html', context)

#deletes an item from the inventory
def deleteItem(request, id):
  post = GenericClothes.objects.get(id = id)

  if request.method == 'POST':
    post.delete()
    return redirect('inventory')

  context = {'item': post}
  return render(request, 'weather_app/delete_item.html', context)


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
