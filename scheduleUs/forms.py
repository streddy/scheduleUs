from django.forms import ModelForm, DateTimeField, widgets
from .models import Event, PollResponse


class EventCreationForm(ModelForm):
    poll_timeframe_start = DateTimeField(
        widget = widgets.DateTimeInput(attrs={'type':'datetime-local'}),
    )

    poll_timeframe_end = DateTimeField(
        widget = widgets.DateTimeInput(attrs={'type':'datetime-local'}),
    )

    class Meta:
        model = Event
        fields = ('name', 'location', 'description', 'poll_timeframe_start', 'poll_timeframe_end', 'poll_end')

