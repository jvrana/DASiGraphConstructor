from core.graph_constructor.models import ContigRegion, Context, BlastContig
from core.graph_constructor import Assembler, Assembly

import networkx as nx


def test_assembler_init(cc):
    a = Assembler(cc)
    assert len(a.graph) > 0

def test_graph_init(cc):
    cc.remove_redundant_contigs()
    cc.circular_partition(int(cc.contigs[0].query.context.length / 2))
    cc.remove_redundant_contigs()
    a = Assembler(cc)
    nx.write_graphml(a.graph, "test.graphml")
    nx.read_graphml("test.graphml")


def test_graph_init_pseudocircular(pseudocircular_cc):
    cc = pseudocircular_cc
    cc.remove_redundant_contigs()
    cc.circular_partition(int(cc.contigs[0].query.context.length / 2))
    cc.remove_redundant_contigs()
    a = Assembler(cc, int(cc.contigs[0].query.context.length / 2))
    nx.write_graphml(a.graph, "test.graphml")
    nx.read_graphml("test.graphml")


def test_dfs_iter(pseudocircular_cc, capsys):
    with capsys.disabled():
        a = Assembler(pseudocircular_cc)
        a.dfs_iter()