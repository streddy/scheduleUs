from django import forms
from django.forms import widgets
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from .models import Event, PollResponse
from mapwidgets.widgets import GooglePointFieldWidget

class EventCreationForm(forms.ModelForm):
    poll_timeframe_start = forms.DateTimeField(
        widget = widgets.DateTimeInput(format="%m/%d/%Y %H:%M:%S", attrs={'placeholder':"MM/DD/YYYY HH:MM:SS"}),
    )

    poll_timeframe_end = forms.DateTimeField(
        widget = widgets.DateTimeInput(format="%m/%d/%Y %H:%M:%S", attrs={'placeholder':"MM/DD/YYYY HH:MM:SS"}),
    )

    poll_end = forms.DateTimeField(
        widget = widgets.DateTimeInput(format="%m/%d/%Y %H:%M:%S", attrs={'placeholder':"MM/DD/YYYY HH:MM:SS"}),
    )
    class Meta:
        model = Event
        fields = ('name', 'location', 'description', 'poll_timeframe_start', 'poll_timeframe_end', 'poll_end', 'event_length', 'is_public', 'allow_flex', 'on_time_attendees')
        labels = {
            "is_public": "Do you want to make this a public event?",
            "allow_flex": "Are you willing to shorten the event by up to 20 minutes to maximize attendance?",
            "on_time_attendees": "Can attendees arrive late or leave early?"
        }
        widgets = {
            'location': GooglePointFieldWidget,
        }



class EventResponseForm(forms.ModelForm):
    responder_start = forms.DateTimeField( 
        widget = widgets.DateTimeInput(format="%m/%d/%Y %H:%M:%S", attrs={'placeholder':"MM/DD/YYYY HH:MM:SS"}),
    )
    responder_end = forms.DateTimeField(
        widget = widgets.DateTimeInput(format="%m/%d/%Y %H:%M:%S", attrs={'placeholder':"MM/DD/YYYY HH:MM:SS"}),
    )
    class Meta:
        model = PollResponse
        fields = ('responder_start', 'responder_end') #still have to figure out declining poll
