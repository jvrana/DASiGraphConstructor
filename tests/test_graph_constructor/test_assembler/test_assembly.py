from dasi.graph_constructor.models import BlastContig, ContigRegion, Context
from dasi.graph_constructor.assembly import Assembly

def test_gap_cost_both_extendable():
    subject = ContigRegion(1, 100, Context(9795, True))
    query_context = Context(20000, True)
    query = ContigRegion(1, 100, query_context)

    left = BlastContig(query, subject, "test")

    from matplotlib import pyplot as plt
    for left_extendable, right_extendable, color in [(True, True, "blue"), (False, True, "green"), (False, False, "red")]:

        X = []
        Y = []
        left.lp_extendable = left_extendable
        left.rp_extendable = left_extendable

        for right_start in range(1, 1000):
            right = BlastContig(ContigRegion(right_start, right_start + 99, query_context), subject, "test")
            right.lp_extendable = right_extendable
            right.rp_extendable = right_extendable

            gap_cost = Assembly._gap_cost(left, right)
            left_end = left.query.end
            right_start = right.query.start
            distance = right_start - left_end
            print(f"{left_end} {right_start} Distance: {distance}, Gap_cost: {gap_cost}")

            X.append(distance)
            Y.append(gap_cost)

        plt.scatter(X, Y, s=1.0, c=[color]*len(Y), label=f"{left_extendable + right_extendable}")

    if False:
        plt.ylim(0, 500)
        plt.xlabel("Distance (bp)")
        plt.ylabel("Gap Cost ($)")
        plt.legend(loc=2)
        plt.show()
