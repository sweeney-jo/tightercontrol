
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from django.conf import settings
#from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
#from personal.models import Profile
#from .current_user import get_current_user
from django.contrib.auth.models import User
from django.db import models
from .middleware.current_user import get_current_user


class Input(models.Model):
   # user = models.ForeignKey(settings.AUTH_USER_MODEL, default = 1)
   # user = models.OneToOneField(User, primary_key=True)
  #  user = models.ForeignKey(
   #     settings.AUTH_USER_MODEL,
   #     null=True, blank=True, 
   #     on_delete=models.SET_NULL
    #    )
    time = models.CharField(max_length=20, default = "datetimestamp")

    record_type = models.FloatField(max_length=5, null=True)
   
    historic_glucose = models.FloatField(max_length=5,null=True)
   
    scan_glucose = models.FloatField(max_length=5, null=True)
   
    rapid_acting_insulin = models.FloatField(max_length=5, null=True)
    
    carbohydrates = models.FloatField(max_length=5, null=True)
    notes = models.CharField(max_length = 20, default = "Normal Day Shift")

   # created_by = models.ForeignKey('auth.User',on_delete=models.SET_NULL, default=get_current_user,null = True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
        )


    def save_model(self, request, obj, form, change):
        obj.added_by = request.user
        super().save_model(request, obj, form, change)


    def __str__(self):
      return str(self.time)  #wrap with str if not string

  #  def save_model(self, request, obj, form, change):
    #   obj.user = request.user
    #   super().save_model(request, obj, form, change)
