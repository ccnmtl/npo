from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.simplejson import loads
from backend import expand_param_names
from backend import request as backend_request
from django.conf import settings
import os
from django.core.mail import send_mail
from restclient import GET
import time

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
    save_parameters = models.BooleanField(default=False)
    output_file = models.FileField(upload_to="outputs/%Y/%m/%d",blank=True,null=True)
    email_user = models.BooleanField(default=False)

    def send_notification_email(self):
        if not self.email_user:
            return # they didn't ask for email so we don't spam them
        # note that the URL is hard-coded for production
        # I figure email functionality on dev instances isn't a
        # big deal if it's missing
        send_mail("NPO Run '%s' complete" % self.name or str(self.pk),
                  """Your NPO run has completed. You may view the output at

%s""" % "http://npo.ccnmtl.columbia.edu" + self.get_absolute_url(),
                  "npo@ccnmtl.columbia.edu",
                  [self.owner.email])

    def parameters_dict(self):
        return loads(self.parameters)

    def output_dict(self):
        try:
            # temporarily handle both possible payloads that the backend might give us
            d = loads(self.stage_one_output)
            if d.has_key('outputs'):
                return d['outputs']
            else:
                return d
        except:
            return dict()

    def geojson(self):
        return self.output_dict().get('geojson','')

    def node_stats(self):
        return self.output_dict().get('statistics',dict()).get('node',dict())

    def mean_lon(self):
        return self.node_stats().get('mean longitude',None)
    def mean_lat(self):
        return self.node_stats().get('mean latitude',None)
    def min_lon(self):
        return self.node_stats().get('minimum longitude',None)
    def min_lat(self):
        return self.node_stats().get('minimum latitude',None)
    def max_lon(self):
        return self.node_stats().get('maximum longitude',None)
    def max_lat(self):
        return self.node_stats().get('maximum latitude',None)

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
        dataset = params.get('dataset') or 'default'
        (demographicsfile,networksfile) = datasets[dataset]
        del params['dataset']
        demographics = open(os.path.join(settings.SAMPLE_PATH,demographicsfile)).read()
        networks = open(os.path.join(settings.SAMPLE_PATH,networksfile)).read()

        demographics_extension = demographicsfile.split(".")[-1].lower()

        params['callbackURL'] = "http://" + host + "/api" + self.get_absolute_url()

        params = expand_param_names(params)
        backend_request(params,demographics,networks,async=True,
                        demographics_extension=demographics_extension)
        self.stage_one_output = ""
        self.stage_two_output = ""
        self.save()

    def fetch_output_file(self):
        if self.status() == "started":
            return # precondition: must have output
        d = loads(self.stage_one_output)
        try:
            url = d['formats']['zip']
        except KeyError:
            # looks like we don't have a zip file to download
            # have to punt for now
            return url

        content = GET(url)
        path = time.strftime("outputs/%Y/%m/%d")
        fullpath = os.path.join(settings.MEDIA_ROOT,path)
        fname = "%d.zip" % self.id
        try:
            os.makedirs(fullpath)
        except OSError:
            pass # dir already exists
        f = open(os.path.join(fullpath,fname),"w")
        f.write(content)
        f.close()
        self.output_file = os.path.join(path,fname)
        self.save()

from django.contrib import admin
admin.site.register(Case)
