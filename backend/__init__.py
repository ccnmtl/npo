from restclient import POST
from pprint import pprint
import os
from simplejson import loads
from params import params

SAMPLE_PATH = "sample_data"
BACKEND_URL = "http://october.mech.columbia.edu/jobs"

def request(params,demographics,networks,async=True):
    params["sync"] = "1" # tell it we want our results NOW!
    files = {
        "network > network > existing network path" : {
            'file' : networks, 'filename' : "networks.zip",
            },
        "demographicDatabase" : {
            "file" : demographics, "filename" : "demographics.csv",
            },
        }
    if async:
        POST(BACKEND_URL,params,files=files,async=True)
    else:
        return POST(BACKEND_URL,params,files=files,async=False)

def _exp_names(d,parents):
    """ see expand_param_names() below """
    results = []
    for (k,v) in d.iteritems():
        if type(v) == type("s") or type(v) == type(u"s"):
            full_key = " > ".join(parents + [k])
            results.append((full_key,v))
        else:
            results.extend(_exp_names(v,parents + [k]))
    return results

def expand_param_names(d):
    """ we store params in a nested dictionary, but the backend
    needs it one deep with the structure expanded in the keys """
    results = dict()
    results.update(_exp_names(d,[]))
    return results
    
if __name__ == "__main__":
    demographics = open(os.path.join(SAMPLE_PATH,"demographics.csv")).read()
    networks = open(os.path.join(SAMPLE_PATH,"networks.zip")).read()
    params = expand_param_names(params)
    r = request(params,demographics,networks,async=False)
    results = loads(r)
    pprint(results)
