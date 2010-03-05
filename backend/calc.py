DEMAND_TYPES = "household productive commercial education health lighting".split()
FACILITY_TYPES = "household health education commercial lighting".split()
SYSTEM_TYPES = "grid off-grid mini-grid".split()
COST_COMPONENTS = {
    'grid': [
        "transformer cost",
        "installation cost",
        "service cost",
        "equipment cost",
        ## XXX TODO NO MEDIUM VOLTAGE LINE COST YET "medium voltage line cost per meter",
        ## XXX TODO NO LOW VOLTAGE LINE COST YET
        "internal system recurring cost per year",
        ## XXX TODO what about external system recurring cost per year per meter?
        ],

    'off-grid': [
        "photovoltaic panel cost",
        "photovoltaic battery cost",
        "photovoltaic balance cost",
        "diesel generator cost",
        "diesel equipment cost",
        "diesel generator installation cost"

        "system recurring cost per year",
        ],

    'mini-grid': [
        "diesel generator cost",
        "diesel equipment cost",
        "diesel generator installation cost",
        ## XXX TODO NO LOW VOLTAGE LINE COST YET
        "system recurring cost per year",
        ],
    }

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

def cost_histogram(nodes, system, *bins):
    bins = sorted(set(float(bin) for bin in bins))
    counts = dict()

    def find_bin(cost, bin_set):
        for bin in bin_set:
            if cost < bin:
                return bin
        return bin_set[-1]

    for bin in bins:
        counts[bin] = 0

    for node in nodes._dict:
        node = nodes[node]

        cost = node.total_costs(system)
        bin = find_bin(cost, bins)
        counts[bin] += 1

    return counts

def nodes_per_system_nongrid(nodes):
    counts = dict()
    types = "mini-grid off-grid".split()

    for type in types:
        counts[type] = 0

    for node in nodes._dict:
        node = nodes[node]

        mini_cost = node.total_cost("mini-grid")
        off_cost = node.total_cost("off-grid")

        if mini_cost > off_cost:
            counts["off-grid"] += 1
        else:
            counts['mini-grid'] += 1

    return counts

def cost_components(nodes):
    component_cost = dict()
    total_cost = dict()
    for system_type in SYSTEM_TYPES:
        components = COST_COMPONENTS[system_type]
        component_cost[system_type] = dict()
        for component in components:
            component_cost[system_type][component] = 0
        total_cost[system_type] = 0

    for node in nodes._dict:
        node = nodes[node]

        system_type = node.system()
        costs = component_cost[system_type]
        for component in costs:
            my_cost = node.initial_cost(component)
            costs[component] += my_cost
        my_total_cost = node.total_cost()## XXX TODO final=True) --> when we have MV COST
        total_cost[system_type] += my_total_cost

    return {'components': component_cost,
            'totals': total_cost}

def nodes_per_system_and_type(nodes):
    counts = dict()
    for type in SYSTEM_TYPES:
        counts[type] = {'urban':0, 'rural':0}

    for node in nodes._dict:
        node = nodes[node]
        system = node.system()
        if node.is_urban():
            counts[system]['urban'] += 1
        else:
            counts[system]['rural'] += 1

    return counts

def average_cost_per_household(nodes):
    costs = dict()
    households = dict()
    for type in SYSTEM_TYPES:
        costs[type] = dict(urban=0, rural=0)
        households[type] = dict(urban=0, rural=0)

    for node in nodes._dict:
        node = nodes[node]

        system = node.system()
        cost = node.total_cost()
        if node.is_urban:
            urbanity = 'urban'
        else:
            urbanity = 'rural'
        costs[system][urbanity] += cost
        households[system][urbanity] += node.projected_households()
        
    for type in SYSTEM_TYPES:
        for x in "urban rural".split():
            if households[type][x] == 0:
                costs[type][x] = 0
            else:
                costs[type][x] = costs[type][x] / households[type][x]

    return costs

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

    def projected_households(self):
        return float(self['demographics']['projected household count'])

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

    def mv_length_in_meters(self):
        ## XXX TODO
        raise NotImplementedError("NEED THIS FROM ROY")

    def total_cost(self, system=None, final=False):
        """
        Returns the total cost for building this node over the 
        time horizon.

        If system is None, uses the node's preferred system (if 
        that has been calculated).

        The `final` parameter signifies whether the network has
        been built (ie the Big Algorithm) - if it has not been
        built we don't have access to some of the data. I think
        this is only relevant for on-grid nodes.
        """
        system = system or self.system()
        if system == 'grid':
            cost = self['system (grid)']['internal system nodal cost']
            if final:
                external_cost = float(
                    self['system (grid)']['external nodal cost per meter'])
                meters = self.mv_length_in_meters()
                external_cost *= meters
                cost = float(cost) + external_cost
        else:
            cost = self['system (%s)' % system]['system nodal cost']
        cost = float(cost)
        return cost

    def initial_cost(self, component):
        system = self.system()
        assert component in COST_COMPONENTS[system]

        # typo in outputs
        if component == 'transformer cost':
            component = 'transfomer cost'

        component_cost = self['system (%s)' % system][component]
        component_cost = float(component_cost)
        
        if component == "medium voltage line cost per meter":
            num_meters = self['metric'][
                'maximum length of medium voltage line in meters']
            num_meters = float(num_meters)
            component_cost = component_cost * num_meters

        return component_cost

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

