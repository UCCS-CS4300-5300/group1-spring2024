"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import WeatherView, TemperatureView, RegisterUser


urlpatterns = [
    path('admin/', admin.site.urls),
    # The url below assumes location is passed in request body or something
    # If we pass in url we will extract location based on url params
    # But for now I think we'll extract from body since its easier
    path('', WeatherView.as_view(), name='home'),
    path('recommendation', TemperatureView.as_view(), name='recommendation'),
    path('inventory', WeatherView.as_view(), name='inventory'),

    #user auth paths
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', RegisterUser.as_view(), name = 'register'),
]
