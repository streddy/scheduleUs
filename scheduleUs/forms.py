from django import forms
from django.forms import widgets
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from .models import Event, PollResponse

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
        fields = ('name', 'location', 'description', 'poll_timeframe_start', 'poll_timeframe_end', 'poll_end')
