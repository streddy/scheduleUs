from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Profile(AbstractUser):
    location_city = models.CharField(max_length=50, blank=True, null=True)
    location_state = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username


class Friends(models.Model):
    initiator = models.ForeignKey(Profile, related_name='initiator', on_delete=models.CASCADE)
    friend = models.ForeignKey(Profile, related_name='friend', on_delete=models.CASCADE)
