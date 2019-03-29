from django.forms import ModelForm, DateTimeField, widgets
from .models import Event, PollResponse
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

class EventCreationForm(ModelForm):
    poll_timeframe_start = DateTimeField(
            widget = widgets.DateTimeInput(format="%m/%d/%Y %H:%M:%S", attrs={'placeholder':"MM/DD/YYYY HH:MM:SS"}),
    )

    poll_timeframe_end = DateTimeField(
            widget = widgets.DateTimeInput(format="%m/%d/%Y %H:%M:%S", attrs={'placeholder':"MM/DD/YYYY HH:MM:SS"}),
    )

    poll_end = DateTimeField(
            widget = widgets.DateTimeInput(format="%m/%d/%Y %H:%M:%S", attrs={'placeholder':"MM/DD/YYYY HH:MM:SS"}),
    )

    class Meta:
        model = Event
        fields = ('name', 'location', 'description', 'poll_timeframe_start', 'poll_timeframe_end', 'poll_end')
