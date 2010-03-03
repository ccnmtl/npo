DEMAND_TYPES = "household productive commercial education health lighting".split()
FACILITY_TYPES = "household health education commercial lighting".split()
SYSTEM_TYPES = "grid off-grid mini-grid".split()

class urban_rural_population_totals(object):
    def __init__(self, time_horizon=0):
        self.urban = [0] * time_horizon
        self.rural = [0] * time_horizon
        self.time_horizon = time_horizon

    def __call__(self, nodes):
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

class demand_totals(object):
    def __init__(self):
        self.demands = dict()
        for type in DEMAND_TYPES:
            self.demands[type] = 0

    def __call__(self, nodes):
        for node in nodes._dict:
            node = nodes[node]

            for type in DEMAND_TYPES:
                demand = node.demand(type)
                self.demands[type] += demand

        return self.demands

def count_totals(nodes):
    counts = dict()
    for type in FACILITY_TYPES:
        counts[type] = 0

    for node in nodes._dict:
        node = nodes[node]

        for type in FACILITY_TYPES:
            count = node.count(type)
            counts[type] += count

    return counts

def nodes_per_system(nodes):
    counts = dict()
    for type in SYSTEM_TYPES:
        counts[type] = 0

    for node in nodes._dict:
        node = nodes[node]
        counts[node.system()] += 1

    return counts

        
from simplejson import loads
import os
def load():
    try:
        from django.conf import settings
        data_path = settings.SAMPLE_PATH
    except:
        data_path = "./sample_data"
    x = open(os.path.join(data_path, 'output.json')).read()
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

    def system(self):
        val = self['metric']['system']
        assert val in SYSTEM_TYPES
        return val

    def count(self, type):
        assert type in FACILITY_TYPES
        if type == 'household':
            value = self['demographics']['projected household count']
        elif type == 'lighting':
            value = self['demand (social infrastructure)']['projected public lighting facility count']
        else:
            value = self['demand (social infrastructure)']['projected %s facility count' % type]
        return float(value)

    def demand(self, type):
        assert type in DEMAND_TYPES

        key = "projected %s demand in kilowatt-hours per year"
        if type == "household":
            x = self['demand (household)']
            key = "projected %s demand in kilowatts-hours per year"
        elif type == "productive":
            x = self['demand (productive)']
        else:
            if type == "lighting":
                type = "public lighting"
            x = self['demand (social infrastructure)']
            type = type + " facility"
        key = key % type
        return float(x[key])

if __name__ == '__main__':
    import code
    from pprint import pprint as pp
    code.interact(local=locals())

