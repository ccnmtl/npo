from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.simplejson import loads, dumps
from backend import expand_param_names
from backend import request as backend_request
from django.conf import settings
import os
from django.core.mail import send_mail
from restclient import GET
import time
from backend.calc import Nodes
from backend.calc import urban_rural_population_totals as ur
from backend.calc import demand_totals
from backend.calc import total_projected_household_count
from backend.calc import count_totals
from backend.calc import nodes_per_system_nongrid
from backend.calc import nodes_per_system_and_type
from backend.calc import cost_components as calc_component_costs
from backend.calc import cost_histogram
from backend.calc import average_cost_per_household
from backend.calc import lv_per_household


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
    output_summary = models.TextField(blank=True, default="")
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

    def output_summary_dict(self):
        try:
            return loads(self.output_summary)
        except ValueError:
            return {}
    def get_output_summary(self, key):
        values = self.output_summary_dict()
        return values.get(key)
    def set_output_summary(self, key, value):
        values = self.output_summary_dict()
        values[key] = value
        self.output_summary = dumps(values)
        self.save()

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

    def time_horizon(self):
        return int(self.parameters_dict()['metric']['finance']['time horizon in years']) + 1

    def node_output(self):
        nodes = self.output_dict()['variables']['node']
        return Nodes(nodes)
    
    def total_mv_line_length(self):
        return float(self.output_dict()
                     ['statistics']['network']
                     ['new segment weight'])
    def mv_line_cost_per_meter(self):
        return float(self.parameters_dict()
                     ['metric']
                     ['system (grid)']
                     [
                'medium voltage line cost per meter'
                ])

    def years(self):
        return range(self.time_horizon())

    def total_households_on_grid(self):
        return total_projected_household_count(
            self.node_output(), system='grid')
                                               
    def mv_hh(self):
        _val = self.get_output_summary("mv_hh")
        if _val is not None: return _val

        nodes = self.node_output()
        count = total_projected_household_count(
            nodes, system='grid')
        mv_length = self.total_mv_line_length()

        _val = 0
        if count:
            _val = mv_length / count

        self.set_output_summary("mv_hh", _val)
        return _val

    def pop(self):
        _val = self.get_output_summary("pop")
        if _val is not None: return _val

        horizon = self.time_horizon()
        nodes = self.node_output()
        x = ur(horizon)
        results = x(nodes)

        self.set_output_summary("pop", results)
        return results

    def demand(self):
        _val = self.get_output_summary("demand")
        if _val is not None: return _val

        nodes = self.node_output()
        x = demand_totals()
        results = x(nodes)

        self.set_output_summary("demand", results)
        return results

    def count(self):
        _val = self.get_output_summary("count")
        if _val is not None: return _val

        nodes = self.node_output()
        results = count_totals(nodes)

        self.set_output_summary("count", results)
        return results

    def system_count(self):
        _val = self.get_output_summary("system_count")
        if _val is not None: return _val

        nodes = self.node_output()
        results = nodes_per_system_nongrid(nodes)

        self.set_output_summary("system_count", results)
        return results

    def system_summary(self):
        _val = self.get_output_summary("system_summary")
        if _val is not None: return _val

        nodes = self.node_output()
        results = nodes_per_system_and_type(nodes)

        self.set_output_summary("system_summary", results)
        return results

    def cost_components(self):
        _val = self.get_output_summary("cost_components")
        if _val is not None: return _val

        nodes = self.node_output()
        results = calc_component_costs(nodes)
        mv_cost = (self.total_mv_line_length() *
                   self.mv_line_cost_per_meter())
        results['components']['grid'][
            'medium-voltage line cost'] = mv_cost

        x = self.output_dict()
        results['totals']['grid'] = float(x['variables'][
            'metric']['system (grid)']['system total cost'])

        self.set_output_summary("cost_components", results)
        return results

    def mv_infrastructure_costs(self):
        cost_components = self.cost_components()['components']['grid']
        mv = cost_components["medium-voltage line cost"]
        mv += cost_components["transformer cost"]
        return mv

    def lv_infrastructure_costs(self):
        cost_components = self.cost_components()['components']['grid']
        lv = cost_components["low voltage line cost"]
        lv += cost_components["equipment cost"]
        return lv

    def cost_histograms(self, g_bins, o_bins, m_bins):
        nodes = self.node_output()

        results = {
            'grid': cost_histogram(nodes, 'grid', *g_bins),
            'off-grid': cost_histogram(nodes, 'off-grid', *o_bins),
            'mini-grid': cost_histogram(nodes, 'mini-grid', *m_bins),
            }

        return results

    def household_average_cost(self):
        _val = self.get_output_summary("household_average_cost")
        if _val is not None: return _val

        nodes = self.node_output()
        results = average_cost_per_household(nodes)

        self.set_output_summary("household_average_cost", results)
        return results

    def household_average_cost_grid(self):
        d = self.household_average_cost()
        return d['grid']['urban'] + d['grid']['rural']

    def household_average_cost_off_grid(self):
        d = self.household_average_cost()
        return d['off-grid']['urban'] + d['off-grid']['rural']

    def household_average_cost_mini_grid(self):
        d = self.household_average_cost()
        return d['mini-grid']['urban'] + d['mini-grid']['rural']

    def lv_hh(self):
        _val = self.get_output_summary("lv_hh")
        if _val is not None: return _val

        nodes = self.node_output()
        results = lv_per_household(nodes)

        self.set_output_summary("lv_hh", results)
        return results

    def lv_hh_total(self):
        r = self.lv_hh()
        return r['rural'] + r['urban']

    def populate_summary_cache(self):
        """ Clear the output_summary cache (json blob) and re-run
        all the methods that populate and use that cache, ie all the
        methods which iterate over the node data in the output (which
        is really slow because it's so big).
        """
        self.output_summary = ""
        self.save()
        self.mv_hh()
        self.pop()
        self.demand()
        self.count()
        self.system_count()
        self.system_summary()
        self.cost_components()
        self.household_average_cost()
        self.lv_hh()

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
        if dataset not in datasets: dataset = 'default'
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
            return

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
