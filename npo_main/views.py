from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from sample_data.params import params
from sample_data.leona import params as params_leona
from sample_data.kenya import params as params_kenya
from backend import expand_param_names
from backend import request as backend_request
SAMPLE_PATH = "sample_data"
import os
from simplejson import loads, dumps
from models import Case
from collections import defaultdict

class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name
 
    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if type(items) == type({}):
                return render_to_response(self.template_name, items, context_instance=RequestContext(request))
            else:
                return items
 
        return rendered_func

@login_required
@rendered_with('npo/index.html')
def index(request):
    cases = Case.objects.filter(owner=request.user)
    return dict(cases=cases)

@login_required
def bulk(request):
    if request.method == "POST":
        if request.POST.get("delete","") != "":
            for k in request.POST.keys():
                if k.startswith("case_"):
                    caseid = k.split("_")[1]
                    case = Case.objects.get(id=caseid)
                    case.delete()
        # compare not handled yet
        # it'll be a redirect to another view
    return HttpResponseRedirect("/")

@login_required
@rendered_with('npo/create_case.html')
def create_case(request):
    if request.method == "POST":

        # start with params from sample data (see import above)
        # now, for each parameter that we get from the request,
        # we override those

        # the params we don't want to copy over
        SKIP_PARAMS = ["title","xyzxyzxyz","dataset"]

        selected_paramset = request.POST['selected-param-set'] + "-"

        for key in request.POST.keys():
            # ignore fields not from the selected paramset
            if not key.startswith(selected_paramset):
                continue 

            fullkey = key
            key = key[len(selected_paramset):] # strip the prefix

            if key in SKIP_PARAMS:
                continue

            parts = key.split(">")
            plevel = params
            for p in parts[:-1]:
                p = p.replace("_"," ")
                plevel = plevel[p]
            plevel[parts[-1].replace("_"," ")] = " ".join(request.POST.getlist(fullkey))

        params["dataset"] = request.POST.get("dataset","default")
        case = Case.objects.create(name=request.POST['title'],
                                   owner=request.user,
                                   parameters=dumps(params),
                                   )
        # here's where we would actually kick off the job
        # to the backend
        case.run(request.get_host())
        return HttpResponseRedirect("/")
    defaults = params
    return dict(cases=Case.objects.filter(owner=request.user),defaults=defaults,
                leona=params_leona,kenya=params_kenya)


def case_callback(request,id):
    case = get_object_or_404(Case,id=id)
    if request.method == "POST":
        # this should be Roy's backend sending us some results
        if case.status() == "started":
            # save results to stage 1
            case.stage_one_output = loads(request.POST.get('json','{}'))
        if case.status() == "stage 1":
            case.stage_two_output = loads(request.POST.get('json','{}'))
        case.save()

        if case.status() == "complete":
            # umm. someone's POSTing but it's already complete
            pass

        return HttpResponse("ok")
    return HttpResponse("this requires a POST")

@login_required
@rendered_with('npo/case.html')
def case(request,id):
    case = get_object_or_404(Case,id=id)
    return dict(case=case)

@login_required
def delete_case(request,id):
    case = get_object_or_404(Case,id=id)
    case.delete()
    return HttpResponseRedirect("/")


@login_required
@rendered_with('npo/run.html')
def run(request):
    demographics = open(os.path.join(SAMPLE_PATH,"demographics.csv")).read()
    networks = open(os.path.join(SAMPLE_PATH,"networks.zip")).read()
    results = loads(backend_request(expand_param_names(params),demographics,networks))
    return dict(results=results)

