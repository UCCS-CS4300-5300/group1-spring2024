from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

#Form for creating a user (taking input from client)
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AddForm(ModelForm):
    class Meta:
        model = GenericClothes
        fields = ('name', 'clothing_type', 'comfort_low', 'comfort_high', 'waterproof_rating', 'photo', 'image_url')