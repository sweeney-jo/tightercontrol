
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from django.conf import settings
#from django.contrib.auth.models import User


from django.db import models


class Input(models.Model):
   # user = models.ForeignKey(settings.AUTH_USER_MODEL, default = 1)
   # user = models.OneToOneField(User, primary_key=True)
    time = models.CharField(max_length=20, default = "datetimestamp")
    #time = models.DateTimeField(null=True)
   # record_type = models.CharField(max_length=5, null=True)
    record_type = models.FloatField(max_length=5, null=True)
   # historic_glucose = models.CharField(max_length=5,null=True)
    historic_glucose = models.FloatField(max_length=5,null=True)
   # scan_glucose = models.CharField(max_length=5, null=True)
    scan_glucose = models.FloatField(max_length=5, null=True)
   # rapid_acting_insulin = models.CharField(max_length=5, null=True)
    rapid_acting_insulin = models.FloatField(max_length=5, null=True)
    #carbohydrates = models.CharField(max_length=5, null=True)
    carbohydrates = models.FloatField(max_length=5, null=True)
    notes = models.CharField(max_length = 20, default = "Normal Day Shift")


    def __str__(self):
      return str(self.time)  #wrap with str if not string
