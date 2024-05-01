"""
Django forms for creating a user and adding items to the inventory.
See https://docs.djangoproject.com/en/5.0/topics/forms/ for documentation.
"""

from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import GenericClothes

class CreateUserForm(UserCreationForm):
  """
  Form for creating a user (taking input from client)
  """
  class Meta:
    model = User
    fields = ['username', 'email', 'password1', 'password2']

class AddForm(ModelForm):
  """
  Forms for adding items to the inventory
  """
  class Meta:
    model = GenericClothes
    fields = ('name', 'clothing_type', 'comfort_low', 'comfort_high', 'waterproof_rating', 'image')
    widgets = {
      'name': forms.TextInput(
          attrs={
              'class': 'form-control'
          }
      ),
      'clothing_type': forms.Select(
          attrs={
              'class': 'form-control'
          }
      ),
      'comfort_low': forms.NumberInput(
          attrs={
              'class': 'form-control'
          }
      ),
      'comfort_high': forms.NumberInput(
          attrs={
              'class': 'form-control'
          }
      ),
      'waterproof_rating': forms.NumberInput(
          attrs={
              'class': 'form-control'
          }
      ),
      'image': forms.ClearableFileInput(
          attrs={
              'class': 'form-control'
          }
      )
    }
    