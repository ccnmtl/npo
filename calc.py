class urban_rural_population_totals(object):
    def __init__(self, time_horizon=0):
        self.urban = [0] * time_horizon
        self.rural = [0] * time_horizon
        self.time_horizon = time_horizon

    def __call__(self):
        nodes = get_nodes()
        time_horizon = prev_time_horizon = None
        for node in nodes._dict:
            node = nodes[node]

            time_horizon = node.time_horizon()
            assert time_horizon == self.time_horizon, \
                "I'm assuming all the nodes should project population counts " \
                "over identical time horizons of %s, but that doesn't seem to be the case. " \
                "I just came across a node with a time horizon of %s!" % (self.time_horizon, time_horizon)

            for interval in range(time_horizon):
                if node.is_urban(at_t=interval):
                    self.urban[interval] += node.population(at_t=interval)
                else:
                    self.rural[interval] += node.population(at_t=interval)
        return {'urban': self.urban, 'rural': self.rural}

from simplejson import loads
def load():
    x = open('1.json').read()
    y = loads(x)
    return y

def get_nodes():
    x = load()
    nodes = x['outputs']['variables']['node']
    return Nodes(nodes)

class Nodes(object):
    def __init__(self, dict):
        self._dict = dict

    def __getitem__(self, key):
        if isinstance(key, int):
            return Node(self._dict[str(key)])
        return Node(self._dict[key])

def is_urban(population, threshold):
    return population >= threshold

class Node(object):
    def __init__(self, dict):
        self._dict = dict

    def __getitem__(self, key):
        return self._dict[key]

    def keys(self):
        return self._dict.keys()

    def time_horizon(self):
        return len(self.population_over_time())

    def population_over_time(self):
        x = self['demographics']['projected population counts']
        x = [int(p) for p in x.split()]
        return x

    def population(self, at_t=0):
        return self.population_over_time()[at_t]

    def is_urban(self, at_t=0):
        p = self.population(at_t)
        threshold = int(self['demographics']['urban population threshold'])
        return is_urban(p, threshold)
    
import code
from pprint import pprint as pp

from webob import Request, Response
import paste.httpserver

class webapp(object):
    def __call__(self, environ, start_response):
        req = Request(environ)
        path = req.path_info.strip('/')
        return getattr(self, path)(req)(environ, start_response)

    def pop(self, req):
        results = urban_rural_population_totals(time_horizon=11)()
        urban = results['urban']
        rural = results['rural']
        urban = ','.join(str(x) for x in urban)
        #rural = ','.join(str(x) for x in rural)
        #src += urban# + '|' + rural
        other_src = "http://chart.apis.google.com/chart?cht=lc&chs=200x125&chd=t:40,60,60,45,47,75,70,72"
        html = """
<html><head>
<script type="text/javascript" src="http://blackrock.ccnmtl.columbia.edu/site_media/js/bluff/bluff-src.js" />
</head><body>

"""
        return Response(html)

import sys
if len(sys.argv) == 1:
    code.interact(local=locals())
elif sys.argv[1] == 'serve':
    paste.httpserver.serve(webapp())
