# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from mapwidgets.widgets import GooglePointFieldWidget


class ProfileCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = Profile
        fields = ('username', 'email', 'first_name', 'last_name', 'location')
        widgets = {
            'location': GooglePointFieldWidget,
        }

class ProfileChangeForm(UserChangeForm):

    class Meta:
        model = Profile
        fields = ('username', 'email', 'location')
        widgets = {
            'location': GooglePointFieldWidget,
        }


class FriendForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(FriendForm, self).__init__(*args, **kwargs)
        
        potentialFriends = Profile.objects.exclude(id=self.request.user.id)
        alreadyFriends = Friends.objects.filter(initiator=self.request.user).values('friend')
        if alreadyFriends:
            potentialFriends = potentialFriends.exclude(id__in=alreadyFriends)
        
        self.fields['friend'] = forms.ModelChoiceField(queryset=potentialFriends)
    
    class Meta:
        model = Friends
        fields = ['friend']
        labels = {
            "friend": "Choose a friend:"
        }

