from core.graph_constructor.models import schemas, Context, Region, Contig, ContigRegion
from marshmallow import pprint

def test_context_schema():
    c = Context(1000, True, start_index=2)
    schema = schemas.ContextSchema()
    data = schema.dump(c)
    assert data['circular']
    assert data['size'] == 1000
    assert data['start'] == 2


def test_region_schema():
    c = Context(1000, True, start_index=2)
    r = Region(5, 100, c, direction=Region.REVERSE, name="New region")
    schema = schemas.RegionSchema()
    data = schema.dump(r)

    assert data['start'] == 5
    assert data['end'] == 100
    assert data['context']['length'] == 1000
    assert data['direction'] == Region.REVERSE
    assert data['length'] == len(r)


def test_contig_schema():
    c1 = Context(10000, True)
    c2 = Context(5100, True)
    q1 = ContigRegion(100, 300, context=c1, forward=True)
    s1 = ContigRegion(500, 700, context=c2, forward=True)
    contig1 = Contig(q1, s1, "BLAST", data1=5)
    schema = schemas.ContigSchema()
    data = schema.dump(contig1)

    assert data['query']['start'] == 100
    assert data['query']['end'] == 300
    assert data['query']['context']['length'] == 10000

    assert data['subject']['start'] == 500
    assert data['subject']['end'] == 700
    assert data['subject']['context']['length'] == 5100

    assert data['quality']
    assert data['metadata'] == {'data1': 5}
    assert data['alignment_length'] == 201


def test_contig_container_schema(cc):
    cc.meta = {'data2': 10}
    schema = schemas.ContigContainerSchema()
    data = schema.dump({"contigs": cc.contigs})
    assert len(data['contigs']) > 0