from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
#from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic
from django.utils.simplejson import loads
#from sample_data.params import params
from backend import expand_param_names
from backend import request as backend_request
from django.conf import settings
import os

datasets = dict(default=("demographics.csv","networks.zip"),
                leona=("LeonaVillages.zip","LeonaNetworks.zip"),
    )

class Case(models.Model):
    name = models.CharField(max_length=256,default="",blank=True)
    owner = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.now,auto_now_add=True)
    updated = models.DateTimeField(default=datetime.now,auto_now=True)
    parameters = models.TextField(blank=True,default="")
    stage_one_output = models.TextField(blank=True,default="")
    stage_two_output = models.TextField(blank=True,default="")

    @models.permalink
    def get_absolute_url(self):
        return ('npo_main.views.case',[str(self.id)])

    def status(self):
        if self.stage_two_output != "":
            return "complete"
        if self.stage_one_output != "":
            return "stage 1"
        else:
            return "started"

    def run(self,host):
        # this is where we tell the backend that we'd like
        # it to process these parameters and hit us back later
        # with a result
        params = loads(self.parameters)
        (demographicsfile,networksfile) = datasets[params['dataset']]
        del params['dataset']
        demographics = open(os.path.join(settings.SAMPLE_PATH,demographicsfile)).read()
        networks = open(os.path.join(settings.SAMPLE_PATH,networksfile)).read()

        demographics_extension = demographicsfile.split(".")[-1].lower()

        params['callback_url'] = "http://" + host + "/api" + self.get_absolute_url()

        params = expand_param_names(params)
        results = backend_request(params,demographics,networks,async=False,
                                  demographics_extension=demographics_extension)
        self.stage_one_output = results
        self.stage_two_output = results
        self.save()
