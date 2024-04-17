"""Sets up admin site for weather app (I want pylint to like this file)."""

from django.contrib import admin
from .models import GenericClothes

# Models that allow admin to input data.
admin.site.register(GenericClothes)
