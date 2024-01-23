from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth.models import User
#from .models import User


class RoomForm(ModelForm):
    class Meta:
        model = Room
        # what fields to be included from the Room model
        fields = '__all__'
        # below fields are excluded fromt he form
        exclude = ['host','participants']

class userForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar','name','username','email','bio']


class myUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']
