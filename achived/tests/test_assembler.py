from dasi import Assembly, Assembler, ContigRegion, Context, BlastContig
import networkx as nx

def test_assembler_init(cc):
    a = Assembler(cc, int(cc.contigs[0].query.context.length / 2))

    contig_dict = {}
    for c in a.contigs:
        contig_dict[c.contig_id] = c

    for k, v in a.graph.items():
        print(contig_dict[k])
        for c in v:
            print(f"   {contig_dict[c]}")

def test_graph_init(pseudocircular_cc):
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