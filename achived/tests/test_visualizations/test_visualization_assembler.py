from dasi import Assembler, schemas
import os
import json


def test_assembler_vis(pseudocircular_cc, test_dir):
    # pseudocircular_cc.expand_circular_ends(pseudocircular_cc.contigs[0].query.context.length / 2.0)
    a = Assembler(pseudocircular_cc)

    contig_dict = {}
    for c in a.contigs:
        contig_dict[c.contig_id] = c

    for k, v in a.graph.items():
        print(contig_dict[k])
        for c in v:
            print(f"   {contig_dict[c]}")

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
    for k, v in a.graph.items():
        if k not in nodes:
            nodes.append(k)
            data['nodes'].append({'name': k})
        for c in v:
            if c not in nodes:
                nodes.append(c)
                data['nodes'].append({'name': c})
            data['links'].append({
                'source': k,
                'target': c,
                'distance': a.edges[k][c]
            })
    with open(os.path.join(os.path.dirname(test_dir), "viewer", "graph.json"), 'w') as f:
        json.dump(data, f)


def test_cc_to_json(cc):
    schema = schemas.ContigContainerSchema()

    here = os.path.dirname(os.path.abspath(__file__))
    core = os.path.dirname(here)
    print(len(cc.contigs))
    cc.contigs = sorted(cc.contigs, key=lambda x: x.alignment_length, reverse=True)
    with open(os.path.join(core, '../viewer', 'contigs_linear.json'), 'w') as f:
        json.dump(schema.dump(cc).data, f)
    for c in cc.contigs:
        print(f'{c.alignment_length} {c.subject.start} {c.subject.end}')


def test_cc_to_json_pseudocircular(pseudocircular_cc):
    cc = pseudocircular_cc
    cc.remove_redundant_contigs()
    cc.circular_partition(int(cc.contigs[0].query.context.length / 2.0))
    cc.remove_redundant_contigs()
    schema = schemas.ContigContainerSchema()

    here = os.path.dirname(os.path.abspath(__file__))
    core = os.path.dirname(here)
    print(len(cc.contigs))
    contigs = cc.contigs
    contigss = sorted(contigs, key=lambda x: x.query.start, reverse=False)
    with open(os.path.join(core, '../viewer', 'contigs.json'), 'w') as f:
        json.dump(schema.dump(cc).data, f)
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
