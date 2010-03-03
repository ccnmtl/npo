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
        "demand (peak)" : {
            "fraction of nodal demand occurring during peak hours (rural)" : "0.4",
            "fraction of nodal demand occurring during peak hours (urban)" : "0.4",
            "peak electrical usage hours per year" : "1460",
            },
        "demand (social infrastructure)" : {
            "commercial facility count curve points (population and facility count)" : """500 1.2
1000 7
5000 24.4
10000 127.6""",
            "commercial facility count curve type" : "logistic",
            "unit demand per commercial facility in kilowatt-hours per year" : "500",
            "education facility count curve points (population and facility count)" : """500 2
1000 5.9
5000 15.3
10000 25""",
            "education facility count curve type" : "logistic",
            "unit demand per education facility in kilowatt-hours per year" : "438",
            "demand curve type" : "logistic",
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
            },
        "demand lighting" : {
            "count curve points (population and count)" : """500 1
1000 2.8
5000 7.3
10000 25.5""",
            "count curve type" : "logistic",
            "unit demand in kilowatts per year" : "102",
            },
        "demand (productive)" : {
            "demand curve points (population and multiplier)" : """500 1
1000 3.06
5000 3.57
10000 5.10""",
            "demand curve type" : "logistic",
            "productive unit demand per household in kilowatt-hours per year" : "19.5",
            
            },
        "demographics" : {
            "population count" : "100",
            "mean household size (rural)" : "5.2",
            "mean household size (urban)" : "4",
            "mean interhousehold distance in meters" : "50",
            "urban_population_threshold" : "5000",
            "population growth rate per year" : "0.02",
            },
        "distribution" : {
            "low voltage line cost per meter" : "10",
            "low voltage line lifetime in years" : "10",
            "low voltage line operations and maintenance cost per meter" : "1",
            },
        "system (mini-grid)" : {
            "distribution loss per system kilowatt" : "0.15",
            "diesel generator cost per diesel system kilowatt" : "150",
            "diesel generator installation cost as fraction of diesel generator cost" : "0.25",
            "diesel generator lifetime in years" : "5",
            "diesel equipment cost per household" : "50",
            "diesel generator operations and maintenance cost per year as fraction of diesel generator cost" : "0.0",
            "diesel fuel cost per liter" : "1.08",
            "diesel generator hours of operation per year" : "8760",
            "diesel fuel liters consumed per kilowatt-hour" : "0.5",
            "diesel equipment operations and maintenance cost per year as fraction of diesel equipment cost" : "0.05",
            "available system capacities (diesel generator)" : "6 12 19 32 70 100 150 200 400 500 750 1000",
            },
        "system grid" : {
            "distribution loss as fraction of system demand" : "0.15",
            "electricity cost per kilowatt-hour" : "0.1",
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
        "system (off-grid)" : {
            "photovoltaic balance cost as fraction of photovoltaic panel cost" : "0.5",
            "photovoltaic balance lifetime in years" : "10",
            "photovoltaic battery cost per kilowatt-hour" : "400",
            "photovoltaic battery kilowatt-hours per photovoltaic system kilowatt" : "5",
            "photovoltaic battery lifetime in years" : "3",
            "photovoltaic operations and maintenance cost per year as fraction of photovoltaic system cost" : "0.05",
            "photovoltaic panel cost per photovoltaic system kilowatt" : "6000",
            "photovoltaic panel lifetime in years" : "30",
            "diesel generator hours of operation per year" : "7260.0",
            "available system capacities (photovoltaic panel)" : "0.05 0.075 0.15 0.4 1 1.5",
            "available system capacities (diesel generator)" : "2 4 6 12 19 32 70 100 150 200 400 500 750 1000",
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
# elasticity of electricity demand
# 
# medium voltage stuff
