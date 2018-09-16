import itertools
from copy import copy

from core.graph_constructor.cost_functions.gibson_assembly_cost_function import GibsonAssemblyCost
from core.graph_constructor.log import logger
from core.graph_constructor.models import ContigContainer, ContigRegion
import networkx as nx
from core.graph_constructor.utils import pair
from tqdm import tqdm

# logger.propogate = False

class Assembly(object):
    """Represents a particular Assembly"""

    global_id = 0
    INF = -1000000

    def __init__(self, assembly_path, contig_container):
        """

        :param assembly_path: list of contig ids
        :type assembly_path: list
        :param contig_container: ContigContainer
        :type contig_container: ContigContainer
        """
        self._id = self.global_id
        Assembly.global_id += 1
        self.contig_container = contig_container
        self.assembly_path = assembly_path
        self.expected_length = contig_container.contigs[0].query.context.length

    @property
    def contigs(self):
        return [self.contig_container[contig_id] for contig_id in self.assembly_path]

    @property
    def first(self):
        return self.contigs[0]

    @property
    def last(self):
        return self.contigs[-1]

    @property
    def span(self):
        return self.last.query.rp - self.first.query.lp

    @property
    def unassembled_span(self):
        return self.contig_container.contigs[0].query.length - self.span

    @staticmethod
    def _overlap_range(left, right):
        """Gap span range between a left and right contig"""
        # primers are 60bp, 20bp are annealed, leaving 40bp
        max_primer_extension = 40.0
        gap_span = ContigRegion.get_gap_span(left.query, right.query)
        if gap_span is not None:
            extension = max_primer_extension * left.end_extendable
            extension += max_primer_extension * right.start_extendable

            min_overlap = -1.0 * gap_span
            max_overlap = -1.0 * gap_span + extension

            return (min_overlap, max_overlap, gap_span)
        return None

    def assembly_pair_ids(self):
        if len(self.assembly_path) == 1:
            return []
        return list(zip(self.assembly_path[:-1], self.assembly_path[1:]))

    def assembly_pairs(self):
        if len(self.contigs) == 1:
            return []
        return list(zip(self.contigs[:-1], self.contigs[1:]))

    def can_extend(self):
        MAX_HOMOLOGY = 100
        return self.span < self.contig_container.contigs[0].query.length + MAX_HOMOLOGY

        # def gap_cost(self):
        #     """Gap cost for linear assembly"""
        #     cost = 0
        #     for l, r in self.assembly_pairs():
        #         cost += self._gap_cost(l, r)
        #
        # @classmethod
        # def _junction_efficiency(cls, overlap):
        #     """Assembly cost"""
        #     # gibson assembly
        #     params = [
        #         {"lower": -cls.INF, "upper": 10, "cost": 0.0},
        #         {"lower": 11, "upper": 19, "cost": 0.1},
        #         {"lower": 20, "upper": 30, "cost": 0.75},
        #         {"lower": 31, "upper": 100, "cost": 0.9},
        #         {"lower": 101, "upper": cls.INF, "cost": 0.0},
        #     ]
        #
        #     for p in params:
        #         lower = p['lower']
        #         upper = p['upper']
        #         if lower <= overlap <= upper:
        #             return p['cost']
        #
        # @classmethod
        # def _junction_cost(cls, left, right):
        #     """Monetary cost of a junction"""
        #     cost = 0
        #
        #     # calculate primer cost
        #     primer_cost = 14.0
        #     if left.query.end_extendable:
        #         cost += primer_cost
        #     if right.query.start_extendable:
        #         cost += primer_cost
        #
        #     overlap_range = cls._overlap_range(left, right)
        #     if overlap_range is None:
        #         return 1000001.0
        #
        #     min_overlap, max_overlap, overlap = cls._gap_span_range(left, right)
        #     if min_overlap >= 101:
        #         return 1000002.0
        #     if max_overlap <= 10:
        #         pass
        #
        #     # situation 1: junction can form between left and right
        #     # situation 2: junction cannot form between left and right
        #
        # # TODO: Clean up gap_cost
        # # TODO: make parameter sheet for costs
        # @classmethod
        # def _gap_cost(cls, left, right):
        #     overlap_result = cls.possible_overlap(left, right)
        #     if overlap_result is None:
        #         pass
        #         return 10001.0
        #     min_possible_overlap, max_possible_overlap = overlap_result
        #
        #     maximum_overlap = 80.0
        #
        #     # super simple function to determine cost on a scale of 0.0 (GOOD) to 1.0 (BAD)
        #     cost1 = (maximum_overlap - min_possible_overlap) / maximum_overlap
        #     if min_possible_overlap > maximum_overlap:
        #         return 10002.0
        #
        #     cost2 = (maximum_overlap - max_possible_overlap) / maximum_overlap
        #     if cost1 < 0:
        #         cost1 = 0
        #     if cost2 < 0:
        #         cost2 = 0
        #     if cost1 > 1:
        #         cost1 = 1.0
        #     if cost2 > 1:
        #         cost2 = 1.0
        #
        #     overlap = max_possible_overlap
        #     cost = cost2
        #     if cost1 < cost2:
        #         overlap = min_possible_overlap
        #         cost = cost1
        #
        #     if cost == 1.0:
        #         # $0.2 / bp
        #         gap_span = ContigRegion.get_gap_span(left.query, right.query)
        #         if 100 <= gap_span <= 500:
        #             cost = 89.0
        #         elif 501 <= gap_span <= 750:
        #             cost = 129.0
        #         elif gap_span > 750:
        #             cost = 150.0
        #         else:
        #             cost = (gap_span + 40) * 0.8
        #
        #     if left.end_extendable:
        #         # need to purchase primer
        #         # for right now assume a primer costs $14
        #         cost += 14.0
        #     if right.start_extendable:
        #         # need to purchase primer
        #         cost += 14.0
        #
        #     return cost


class Assembler(ContigContainer):
    """Creates assemblies"""

    def __init__(self, contig_container):
        self.contig_container = contig_container
        self.graph = None
        self.create_assembly_graph()

    @property
    def contigs(self):
        return self.contig_container.contigs

    @property
    def query_length(self):
        query = self.contig_container.contigs[0].query
        if query.circular:
            return query.length/2
        return query.length

    # def create_assembly_graph(self):
    #     # TODO: May want to use combinations instead
    #     gac = GibsonAssemblyCost.load()
    #     gap_cost_dict = gac.gap_cost_dict(-500, 3000, e=2, syn=True)
    #
    #
    #     pairs = list(itertools.permutations(self.contigs, 2))
    #     logger.debug(f"Number of contigs {len(self.contigs)}")
    #     logger.debug(f"Number of pairs {len(pairs)}")
    #     logger.debug("Creating assembly graph")
    #
    #
    #     graph = {}
    #     edges = {}
    #     closing_edges = {}
    #     for left, right in pairs:
    #         if left == right:
    #             continue
    #
    #         gap = ContigRegion.get_gap_span(left.query, right.query)
    #         if gap is not None and -100 < gap < 500:
    #             if left.contig_id not in graph:
    #                 graph[left.contig_id] = []
    #             if left.contig_id not in edges:
    #                 edges[left.contig_id] = {}
    #             # if right.contig_id not in edges[left.contig_id]:
    #             #     edges[left.contig_id][right.contig_id] = None
    #             try:
    #                 cost = float("Inf")
    #                 if gap in gap_cost_dict:
    #                     cost = gap_cost_dict[gap]
    #                 if cost < 100000:
    #                     graph[left.contig_id].append(right.contig_id)
    #                     edges[left.contig_id][right.contig_id] = cost
    #             except KeyError:
    #                 pass
    #
    #         closing_gap = self.expected_length - (right.query.rp - left.query.lp)
    #         if right.contig_id not in closing_edges:
    #             closing_edges[right.contig_id] = {}
    #         closing_edges[right.contig_id][left.contig_id] = abs(closing_gap)
    #         # if closing_gap is not None and -100 < closing_gap < 100:
    #         #     if left.contig_id not in closing_edges:
    #         #         closing_edges[right.contig_id] = {}
    #         #     # if right.contig_id not in edges[left.contig_id]:
    #         #     #     edges[left.contig_id][right.contig_id] = None
    #         #     try:
    #         #         cost = float("Inf")
    #         #         if closing_gap in gap_cost_dict:
    #         #             cost = gap_cost_dict[closing_gap]
    #         #         if cost < 100000:
    #         #             closing_edges[right.contig_id][left.contig_id] = cost
    #         #     except KeyError:
    #         #         pass
    #
    #     self.edges = edges
    #     self.closing_edges = closing_edges
    #     self.graph = graph

    def create_assembly_graph(self):
        return self.create_assembly_graph_using_starts_and_ends()

        # return self.create_assembly_graph_using_contigs()

    def create_assembly_graph_using_contigs(self):
        # TODO: May want to use combinations instead
        gac = GibsonAssemblyCost.load()
        gap_cost_dict = gac.gap_cost_dict(-500, 3000, e=2, syn=True)


        pairs = list(itertools.permutations(self.contigs, 2))
        logger.debug(f"Number of contigs {len(self.contigs)}")
        logger.debug(f"Number of pairs {len(pairs)}")
        logger.debug("Creating assembly graph")


        G = nx.DiGraph()
        print("creating")
        for i in tqdm(range(1000)):
            pass
        for left, right in tqdm(pairs, desc='creating edge costs...'):
            if left == right:
                continue

            if right.contig_id == 433:
                pass



            gap = right.query.start - left.query.end
            if gap is not None and -100 < gap < 500:
                # if right.contig_id not in edges[left.contig_id]:
                #     edges[left.contig_id][right.contig_id] = None
                try:
                    cost = float("Inf")
                    if gap in gap_cost_dict:
                        cost = gap_cost_dict[gap]
                    if cost < 10000:
                        # LEFT
                        n1 = pair(left.query.start, left.contig_id)
                        n1 = left.query.start
                        G.add_node(left.contig_id, data="end", y=left.contig_id, x=left.query.start)
                        G.add_node(right.contig_id, data="end", y=right.contig_id, x=right.query.end)
                        G.add_edge(left.contig_id, right.contig_id, weight=float(cost))

                except KeyError:
                    pass

            if left.query.rp > right.query.lp:
                closing_gap = self.query_length - (left.query.rp - right.query.lp)
                try:
                    cost = float("Inf")
                    if closing_gap in gap_cost_dict:
                        cost = gap_cost_dict[closing_gap]
                    if cost < 10000:
                        G.add_node(left.contig_id, data="start", y=left.contig_id, x=left.query.start)
                        G.add_node(right.contig_id, data="start", y=right.contig_id, x=right.query.end)
                        G.add_edge(left.contig_id, right.contig_id, weight=float(closing_gap))
                except KeyError:
                    pass


            # if closing_gap is not None and -100 < closing_gap < 100:
            #     if left.contig_id not in closing_edges:
            #         closing_edges[right.contig_id] = {}
            #     # if right.contig_id not in edges[left.contig_id]:
            #     #     edges[left.contig_id][right.contig_id] = None
            #     try:
            #         cost = float("Inf")
            #         if closing_gap in gap_cost_dict:
            #             cost = gap_cost_dict[closing_gap]
            #         if cost < 100000:
            #             closing_edges[right.contig_id][left.contig_id] = cost
            #     except KeyError:
            #         pass

        self.graph = G

    # Construct using starts and ends
    def create_assembly_graph_using_starts_and_ends(self):
        # TODO: May want to use combinations instead

        def add_nodes_from_contig(contig):
            """
            Adds a contig to the graph by creating two nodes (start and end), and one edge
            spanning the nodes.

            :param contig: The contig to add to the graph
            :type contig: Contig
            :return:
            :rtype:
            """
            # n1 = pair(contig.query.start, contig.contig_id)
            # n2 = pair(contig.query.end, contig.contig_id)
            n1 = pair(contig.query.start, 0)
            n2 = pair(contig.query.end, 1)
            # n1 = contig.query.start
            # n2 = contig.query.end
            G.add_node(n1, data="start", y=contig.contig_id, x=contig.query.start)
            G.add_node(n2, data="end", y=contig.contig_id, x=contig.query.end)
            G.add_edge(n1, n2, weight=float(25.0), type="fragment")
            return n1, n2

        # load the edge costs dictionary
        logger.debug("loading GibsonAssemblyCost...")
        gac = GibsonAssemblyCost.load()
        gap_cost_dict = gac.gap_cost_dict(-500, 3000, e=2, syn=True)

        # pair all of the contigs by finding all permutations of 2
        G = nx.DiGraph()
        pairs = list(itertools.permutations(self.contigs, 2))
        logger.debug(f"Number of contigs {len(self.contigs)}")
        logger.debug(f"Number of pairs {len(pairs)}")
        logger.debug("Creating assembly graph")

        # for each left and right pair,
        for left, right in tqdm(pairs, desc="calculating gap costs"):
            if left == right:
                continue

            gap = right.query.start - left.query.end
            closing = False
            if left.query.rp > right.query.lp:
                gap = self.query_length - (left.query.rp - right.query.lp)
                closing = True
            # TODO: remove hard coded gap limiters
            if gap is not None and -100 < gap < 2000:
                # if right.contig_id not in edges[left.contig_id]:
                #     edges[left.contig_id][right.contig_id] = None
                try:
                    jxn_cost = float("Inf")
                    if gap in gap_cost_dict:
                        jxn_cost = gap_cost_dict[gap]
                    # TODO: remove hard coded max jxn_cost
                    if jxn_cost < 10000:
                        n1, n2 = add_nodes_from_contig(left)
                        n3, n4 = add_nodes_from_contig(right)
                        edge_type = "gap"
                        if closing:
                            edge_type = "closing_gap"
                            # print(f"Closing gap: {left.query.end} {right.query.start}")
                        G.add_edge(n2, n3, weight=float(jxn_cost), type=edge_type)
                except KeyError:
                    pass


            # if right.query.rp > left.query.lp:
            #     closing_gap = self.expected_length - (right.query.rp - left.query.lp)
            #     G.add_edge(right.query.end, left.query.start, weight=closing_gap)


            # if closing_gap is not None and -100 < closing_gap < 100:
            #     if left.contig_id not in closing_edges:
            #         closing_edges[right.contig_id] = {}
            #     # if right.contig_id not in edges[left.contig_id]:
            #     #     edges[left.contig_id][right.contig_id] = None
            #     try:
            #         cost = float("Inf")
            #         if closing_gap in gap_cost_dict:
            #             cost = gap_cost_dict[closing_gap]
            #         if cost < 100000:
            #             closing_edges[right.contig_id][left.contig_id] = cost
            #     except KeyError:
            #         pass

        self.graph = G

    """
    Assembly graph of all possible connections
    Save list of edges and costs
    (include closing edges)
    Find shortest cycle
    """
    # TODO: finish dfs_iter
    def dfs_iter(self, place_holder_size=5, data_plot=False):
        logger.debug("DFS")
        assemblies = []
        best_costs_array = []
        steps = []
        step = 0

        sorted_contigs = sorted(self.contigs, key=lambda x: len(x.query), reverse=True)
        stack = []

        available_contigs = [x.contig_id for x in sorted_contigs]
        # for x in self.closing_edges:
        #     for y in self.closing_edges[x]:
        #         if y not in available_contigs:
        #             available_contigs.append(y)

        for c in available_contigs:
            a = Assembly([c], self.contig_container)
            stack.append(a)

        best_costs = [float("Inf")] * place_holder_size  # e.g. five best costs

        while stack:
            step += 1
            steps.append(step)
            best_costs.sort()
            assembly = stack.pop()

            pairs = assembly.assembly_pair_ids()
            if len(pairs) > 0 and pairs[0] == (105, 157):
                pass
            gap_costs = []
            for xid, yid in pairs:
                cost = float("Inf")
                if xid in self.edges:
                    x = self.edges[xid]
                    if yid in x:
                        cost = x[yid]
                gap_costs.append(cost)

            left = assembly.contigs[0]
            right = assembly.contigs[-1]
            closing_cost = self.query_length - (right.query.rp - left.query.lp)

            gap_cost = sum(gap_costs)
            if gap_cost > best_costs[-1]:
                continue

            cost = gap_cost + closing_cost
            assembly.cost = cost
            if gap_cost > 10000:
                continue

                # if cost > best_costs[-1]:
                #     continue
                # cost can only get worst, so trim this search

            new_assembly_paths = []
            n = assembly.last.contig_id
            if n == 105:
                pass
            if n in self.graph:
                child_ids = self.graph[n]
                if child_ids:
                    for child_id in child_ids:
                        assembly_copy = copy(assembly)
                        assembly_copy.assembly_path = assembly.assembly_path[:] + [child_id]
                        new_assembly_paths.append(assembly_copy)

            for assembly_path in new_assembly_paths:
                if assembly_path.can_extend():
                    stack.append(assembly_path)

            if cost < best_costs[-1]:
                best_costs[-1] = cost
                print(self.query_length)
                print(gap_cost)
                print(closing_cost)
                print(best_costs)
                print(assembly.contigs)
                if data_plot:
                    best_costs_array.append(best_costs[:])
            assembly.best_cost = assembly.cost
            assemblies.append(assembly)
            # end of path
        assemblies = sorted(assemblies, key=lambda x: x.cost)

        if data_plot:
            return assemblies, list(zip(steps, best_costs_array))
        return assemblies
