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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import WeatherView, TemperatureView, GenericClothesListView, RegisterUser, recommendation_reroll
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # The home page url assumes location is passed in the request
    path('', WeatherView.as_view(), name='home'),
    path('recommendation/', TemperatureView.as_view(), name='recommendation'),
    path('inventory/', GenericClothesListView.as_view(), name='inventory'),
    path('inventory/add_item', views.add_item, name='add_item'),
    path('inventory/delete_item/<int:id>', views.delete_item, name='delete_item'),
    path('recommendation/reroll/', recommendation_reroll, name='reroll'),
    #user auth paths
    path('accounts/profile/', WeatherView.as_view(), name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', RegisterUser.as_view(), name = 'register')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
