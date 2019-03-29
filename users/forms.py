# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile


class ProfileCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = Profile
        fields = ('username', 'email', 'first_name', 'last_name', 'location_city', 'location_state')


class ProfileChangeForm(UserChangeForm):

    class Meta:
        model = Profile
        fields = ('username', 'email', 'location_city', 'location_state')
