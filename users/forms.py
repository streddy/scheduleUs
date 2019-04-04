# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *


class ProfileCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = Profile
        fields = ('username', 'email', 'first_name', 'last_name', 'location_city', 'location_state')


class ProfileChangeForm(UserChangeForm):

    class Meta:
        model = Profile
        fields = ('username', 'email', 'location_city', 'location_state')


class FriendForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(FriendForm, self).__init__(*args, **kwargs)
        self.fields['friend'] = forms.ModelChoiceField(queryset=Profile.objects.exclude(id=self.request.user.id))
    
    class Meta:
        model = Friends
        fields = ['friend']
        labels = {
            "friend": "Choose a friend:"
        }

