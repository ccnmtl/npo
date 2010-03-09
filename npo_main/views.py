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

class recursivedefaultdict(defaultdict): 
    def __init__(self): 
        self.default_factory = type(self) 

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

        # we need this to handle curve parameters
        curves = recursivedefaultdict()
        curveparams = dict() # map fullkey -> key list

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
            clevel = curves
            for p in parts[:-1]:
                p = p.replace("_"," ")
                plevel = plevel[p]
                clevel = clevel[p]

            # special case for "curve" parameters
            if "__x__" in parts[-1] or "__y__" in parts[-1]:
                (k,xy,n) = parts[-1].split("__")
                k = k.replace("_"," ")
                curve = clevel[k]
                curve[int(n)][xy] = request.POST[fullkey]
                fk = fullkey.split("__")[0] # we only want the beginning
                curveparams[fk] = parts[:-1] + [k]
            else:
                # it's not a curve so we can just save it
                plevel[parts[-1].replace("_"," ")] = " ".join(request.POST.getlist(fullkey))

        # now we have to go back and flatten out the curve params into single text fields
        for k in curveparams.keys():
            path = curveparams[k]
            path2 = [p.replace('_', ' ') for p in path]

            curve = curves
            for key in path2:
                curve = curve[key]
            
            s = "\n".join(["%s %s" % (curve[n]["x"],curve[n]["y"]) for n in sorted(curve.keys())])
            params[k] = s

        keys_to_delete = [key for key in params.keys() 
                          if key.startswith(selected_paramset)
                          and (key.endswith("_(population_and_multiplier)" or key.endswith("_(population_and_facility_count)"))
                               or key.endswith("_(population_and_multiplier)") or key.endswith("_(population_and_facility_count)"))]
        for key in keys_to_delete:
            del params[key]
        
        params["dataset"] = request.POST.get("dataset","default")
        save = request.POST.get("submitbutton","") == "Run case"
        case = Case.objects.create(name=request.POST['title'],
                                   owner=request.user,
                                   parameters=dumps(params),
                                   save_parameters=save,
                                   )

        # here's where we would actually kick off the job
        # to the backend
        case.run(request.get_host())
        return HttpResponseRedirect("/")
    defaults = params
    return dict(cases=Case.objects.filter(owner=request.user,save_parameters=True),defaults=defaults,
                leona=params_leona,kenya=params_kenya)


def case_callback(request,id):
    case = get_object_or_404(Case,id=id)
    if request.method == "POST":
        # this should be Roy's backend sending us some results
        status = case.status()
        if status == "started":
            # save results to stage 1
            case.stage_one_output = request.POST.get('payload','{}')
        elif status == "stage 1":
            case.stage_two_output = request.POST.get('payload','{}')
        case.save()

        if case.status() == "complete":
            # umm. someone's POSTing but it's already complete
            pass

        return HttpResponse("ok")
    return HttpResponse("this requires a POST")

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


### outputs

from backend.calc import Nodes, get_nodes
def node_output(case):
    #return get_nodes()
    nodes = case.output_dict()['variables']['node']
    return Nodes(nodes)

def time_horizon(case):
    #return 11
    return int(case.parameters_dict()['metric']['finance']['time horizon in years']) + 1

@login_required
@rendered_with('npo/case.html')
def case(request,id):
    case = get_object_or_404(Case,id=id)

    try:
        results = pop(case)

        results['demand'] = demand(case)
        results['counts'] = count(case)
        results['system_counts'] = system_count(case)
        results['system_breakdown_counts'] = system_summary(case)
        x = cost_components(case)
        results['cost_components'] = x['components']
        results['totals'] = x['totals']
        results['cost_histogram_counts'] = cost_histograms(case, request)

        results['case'] = case
        return results
    except:
        #raise
        return panic(request, id)

@rendered_with('npo/case_raw.html')
def panic(request, id):
    case = get_object_or_404(Case,id=id)
    return {'case': case}

from backend.calc import urban_rural_population_totals as ur
def pop(case):
    horizon = time_horizon(case)
    nodes = node_output(case)

    x = ur(horizon)
    results = x(nodes)
    
    results['years'] = range(horizon)
    return results

from backend.calc import demand_totals

def demand(case):
    nodes = node_output(case)

    x = demand_totals()
    results = x(nodes)
    return results

from backend.calc import count_totals
def count(case):
    nodes = node_output(case)

    results = count_totals(nodes)
    return results

from backend.calc import nodes_per_system_nongrid
def system_count(case):
    nodes = node_output(case)

    results = nodes_per_system_nongrid(nodes)
    return results

from backend.calc import nodes_per_system_and_type
def system_summary(case):
    nodes = node_output(case)

    results = nodes_per_system_and_type(nodes)
    return results

from backend.calc import cost_components as calc_component_costs
def cost_components(case):
    nodes = node_output(case)

    results = calc_component_costs(nodes)
    return results

from backend.calc import cost_histogram
def cost_histograms(case, request):
    nodes = node_output(case)

    def bins(param):
        _bins = request.GET.getlist(param)
        if not _bins:
            _bins = ['1e10', '1e12', '1e14']
            
        return _bins
    
    results = {
        'grid': cost_histogram(nodes, 'grid', *bins('g')),
        'off-grid': cost_histogram(nodes, 'off-grid', *bins('o')),
        'mini-grid': cost_histogram(nodes, 'mini-grid', *bins('m')),
        }
    
    return results

from backend.calc import average_cost_per_household
@login_required
@rendered_with("npo/output/household_average_cost.html")
def household_average_cost(request, id):
    case = get_object_or_404(Case, id=id)

    try:
        nodes = node_output(case)
    except KeyError:
        return HttpResponse("stage 1 output is empty or missing node-level data. maybe the backend is still processing the job?")

    results = average_cost_per_household(nodes)
    return dict(results=results)

@rendered_with("npo/output/summary.html")
def summary(request, id):

    urls = "pop demand count system-count system-summary component-costs cost-histograms?m=1000000&m=2000000&m=3000000&o=1e%2B10&o=1e%2B14&o=1e%2B18&o=1e%2B16&g=1000000&g=2000000&g=3000000&g=4000000".split()
    return {"urls": urls}
