from dasi.graph_constructor import Assembler
from dasi.graph_constructor.models import schemas
import os
import json


def test_assembler_vis(cc, test_dir):
    # pseudocircular_cc.expand_circular_ends(pseudocircular_cc.contigs[0].query.context.length / 2.0)
    a = Assembler(cc)

    contig_dict = {}
    for c in a.contigs:
        contig_dict[c.contig_id] = c

    # here = os.path.dirname(os.path.abspath(__file__))
    # core = os.path.dirname(here)
    # schema = schemas.ContigContainerSchema()
    # pseudocircular_cc.contigs = sorted(pseudocircular_cc.contigs, key=lambda x: x.query.start, reverse=False)
    # with open(os.path.join(core, '../viewer', 'contigs.json'), 'w') as f:
    #     json.dump(schema.dump(pseudocircular_cc).data, f)

    # print graph

    nodes = []
    data = {}
    data['nodes'] = []
    data['links'] = []
    for node in a.graph.nodes():
        data['nodes'].append({"name": node})
    for edge in a.graph.edges():
        data['links'].append({
            'source': edge[0],
            'target': edge[1],
            'distance': edge
        })
    with open(os.path.join(os.path.dirname(test_dir), '..', "viewer", "graph.json"), 'w') as f:
        json.dump(data, f)


def test_cc_to_json(cc, test_dir):
    schema = schemas.ContigContainerSchema()

    here = os.path.dirname(os.path.abspath(__file__))
    print(len(cc.contigs))
    contigs = sorted(cc.contigs, key=lambda x: x.alignment_length, reverse=True)
    with  open(os.path.join(os.path.dirname(test_dir), '..', "viewer", "contigs.json"), 'w') as f:
        json.dump(schema.dump({"contigs": cc.contigs}), f)
    for c in contigs:
        print(f'{c.alignment_length} {c.subject.start} {c.subject.end}')

def test_cc_to_csv(pseudocircular_cc):
    cc = pseudocircular_cc
    cc = pseudocircular_cc
    cc.remove_redundant_contigs()
    cc.circular_partition(int(cc.contigs[0].query.context.length / 2.0))
    cc.remove_redundant_contigs()
    import csv

    with open('eggs.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for c in cc.contigs:
            writer.writerow([c.query.start, c.query.end])
