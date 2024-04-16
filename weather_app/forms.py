from django.forms import ModelForm
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
<<<<<<< HEAD
    class Meta:
        model = GenericClothes
        fields = ('name', 'clothing_type', 'comfort_low', 'comfort_high', 'waterproof_rating', 'photo', 'image_url')
=======
  """
  Forms for adding items to the inventory
  """
  class Meta:
    model = GenericClothes
    fields = ('name', 'clothing_type', 'comfort_low', 'comfort_high', 'waterproof_rating')
>>>>>>> eabd4f6504cc42318f24cee13260a2f0c2f7e6ac
