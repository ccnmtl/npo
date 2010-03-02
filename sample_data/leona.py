from collections import defaultdict

params = defaultdict(defaultdict,
    metricModelName="mvMax",
    metric = {
        "finance" : {
            "economic growth rate per year" : "0.06",
            "elasticity of electricity demand" : "0.015",
            "yearly interest rate" : "0.10",
            "time horizon in years" : "10",
            },
        "demand" : {
            "fraction of total demand during peak hours (rural)" : "0.4",
            "fraction of total demand during peak hours (urban)" : "0.4",
            "peak electrical usage hours per year" : "1460",
            },
        "demand commercial" : {
            "count curve points (population and count)" : """500 1.2
1000 7
5000 24.4
10000 127.6""",
            "count curve type" : "logistic",
            "unit demand in kilowatts per year" : "500",
            },
        "demand education" : {
            "count curve points (population and count)" : """500 2
1000 5.9
5000 15.3
10000 25""",
            "count curve type" : "logistic",
            "unit demand in kilowatts per year" : "438",
            },
        "demand health" : {
            "count curve points (population and count)" : """500 1.6
1000 3.5
5000 5.2
10000 20""",
            "count curve type" : "logistic",
            "unit demand in kilowatts per year" : "10000",
            },
        "demand (household)" : {
            "demand curve points (population and multiplier)" : """500 1
1000 1.56
5000 6.16
10000 11.5""",
            "demand curve type" : "logistic",
            "household unit demand per household in kilowatt-hours per year" : "100",
            },
        "demand institution" : {
            "demand curve points (population and multiplier)" : """500 1
1000 1.5
5000 2.25
10000 3.375""",
            "demand curve type" : "logistic",
            "unit demand in kilowatts per year" : "1000",
            },
        "demand lighting" : {
            "count curve points (population and count)" : """500 1
1000 2.8
5000 7.3
10000 25.5""",
            "count curve type" : "logistic",
            "unit demand in kilowatts per year" : "102",
            },
        "demand production" : {
            "demand curve points (population and multiplier)" : """500 1
1000 3.06
5000 3.57
10000 5.10""",
            "demand curve type" : "logistic",
            "unit demand in kilowatts per year" : "19.5",
            
            },
        "people" : {
            "mean household size (rural)" : "9.6",
            "mean household size (urban)" : "7.5",
            "mean interhousehold distance in meters" : "25",
            "rural urban threshold" : "5000",
            "yearly growth rate" : "0.02",
            },
        "system" : {
            "low voltage line cost in dollars per meter" : "10",
            "low voltage line lifetime in years" : "10",
            "low voltage line operations and maintenance cost in dollars per meter" : "1",
            },
        "system diesel" : {
            "engine cost per kilowatt" : "150",
            "engine installation cost as fraction of engine cost" : "0.25",
            "engine lifetime in years" : "5",
            "equipment cost per household" : "50",
            "equipment operations and maintenance cost as fraction of equipment cost" : "0.0",
            "fuel cost per liter" : "1.08",
            "fuel hours per year" : "8760",
            "fuel liters consumed per kilowatt-hour" : "0.5",
            "operations and maintenance cost as fraction of engine cost" : "0.05",
            "system sizes" : "6 12 19 32 70 100 150 200 400 500 750 1000",
            },
        "system grid" : {
            "distribution loss as fraction of system demand" : "0.15",
            "electricity cost per kilowatt-hour" : "0.17",
            "equipment cost per household" : "200",
            "equipment operations and maintenance cost as fraction of equipment cost" : "0.03",
            "installation cost per household" : "60",
            "material and labor cost in dollars per meter of grid extension" : "20",
            "material and labor lifetime in years" : "30",
            "material and labor operations and maintenance cost as fraction of material labor cost" : "0.02",
            "service cost per household" : "70",
            "service operations and maintenance cost as fraction of service cost" : "0.0",
            "system sizes" : "5 15 20 30 40 50 60 70 80 90 100 200 300 400 500 600 700 800 900 1000",
            "transformer cost per kilowatt" : "1000",
            "transformer lifetime in years" : "10",
            "transformer operations and maintenance cost as fraction of transformer cost" : "0.03",
            },
        "system photovoltaic" : {
            "balance cost as fraction of panel cost" : "0.5",
            "balance lifetime in years" : "10",
            "battery cost per kilowatt-hour" : "400",
            "battery kilowatt-hours per system kilowatt" : "5",
            "battery lifetime in years" : "3",
            "operations and maintenance cost as fraction of system cost" : "0.05",
            "panel cost per system kilowatt" : "6000",
            "panel lifetime in years" : "30",
            "system sizes" : "0.05 0.075 0.15 0.4 1 1.5",
            },
        "system photovoltaic diesel" : {
            "system sizes" : "2 4 6 12 19 32 70 100 150 200 400 500 750 1000",
            },
        },
    networkModelName = "modified-kruskal",
    network = {
        "algorithm" : {
            "minimum node count per subnetwork" : "2",
            "search radius in meters" : "2500",
            },
        }
    )


# not accounted for (i don't know what to call them):
#elasticity of electricity demand
#
#medium voltage stuff
