from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.gis.db import models as geomodels

# Create your models here.
class Profile(AbstractUser):
    location = geomodels.PointField()

    def __str__(self):
        return self.username


class Friends(models.Model):
    initiator = models.ForeignKey(Profile, related_name='initiator', on_delete=models.CASCADE)
    friend = models.ForeignKey(Profile, related_name='friend', on_delete=models.CASCADE)

    class Meta:
        unique_together = (("initiator", "friend"),)
