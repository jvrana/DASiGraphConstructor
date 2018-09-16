

def test_junction_cost():

    def _junction_efficiency(overlap):
        """Assembly cost"""
        # gibson assembly
        INF = 1000000.0
        params = [
            {"lower": -INF, "upper": 10, "cost": 0.0},
            {"lower": 11, "upper": 19, "cost": 0.1},
            {"lower": 20, "upper": 30, "cost": 0.75},
            {"lower": 31, "upper": 100, "cost": 0.9},
            {"lower": 101, "upper": INF, "cost": 0.0},
        ]

        for p in params:
            lower = p['lower']
            upper = p['upper']
            if lower <= overlap <= upper:
                return p['cost']

    primer_size = (10, 60)
    primer_extension = (0, 40)
    primer_cost = 0.60  # / bp
    ultramer_size = (60, 200)
    ultramer_extension = (40, 180)
    ultramer_cost = 0.80  # / bp

    costs = []
    efficiency = []

    primer_costs = []
    ultramer_costs = []
    for i in range(*primer_extension):
        primer_costs.append((i, primer_cost * (20.0 + i), "primer"))
    for i in range(*ultramer_extension):
        ultramer_costs.append((i, ultramer_cost * (20.0 + i), "ultramer"))

    import itertools

    g = list(itertools.combinations(primer_costs + ultramer_costs, 2))

    results = {}

    for d in [10, 20, 30]:
        print(d)
        results[d] = []
        for l, r in g:
            extension = l[0] + r[0]
            cost = l[1] + r[1]
            efficiency = _junction_efficiency(d - extension)
            score = float("Inf")
            if efficiency > 0:
                score = cost / efficiency
            x = [l, r]
            results[d].append({
                "score": score,
                "cost": cost,
                "efficiency": efficiency,
                "condition": f"{l[2]} {r[2]}",
                "extension": f"{l[1]} {r[1]}"
            })
            results[d].sort(key=lambda x: x['score'], reverse=True)

    pass

test_junction_cost()