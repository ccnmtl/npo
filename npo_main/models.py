from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
#from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic
#from django.utils import simplejson as json

class Case(models.Model):
    name = models.CharField(max_length=256,default="",blank=True)
    owner = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    parameters = models.TextField(blank=True,default="")
    stage_one_output = models.TextField(blank=True,default="")
    stage_two_output = models.TextField(blank=True,default="")

    def status(self):
        if self.stage_two_output != "":
            return "complete"
        if self.stage_one_output != "":
            return "stage 1"
        else:
            return "started"
