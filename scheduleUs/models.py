from django.db import models
from django.contrib.gis.db import models as geomodels

class Event(models.Model):
    organizer = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    location = geomodels.PointField()
    is_public = models.BooleanField(default=False)
    description = models.CharField(max_length=150, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    poll_timeframe_start = models.DateTimeField('start of poll timeframe')
    poll_timeframe_end = models.DateTimeField('end of poll timeframe')
    poll_end = models.DateTimeField('poll closing time')
    def __str__ (self):
        return self.name

class UserInvited(models.Model):
    invited_user = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_invited = models.BooleanField(verbose_name="Invite?", default=False)

    class Meta:
        unique_together = (("invited_user", "event"),)


class PollResponse(models.Model):
    responder = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    responder_start = models.DateTimeField()
    responder_end = models.DateTimeField()
