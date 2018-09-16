from core.graph_constructor.models import Context, Region, ContigRegion, Contig
from core.graph_constructor.exceptions import ContigError, RegionError
import pytest
from copy import copy


@pytest.fixture
def linear_context():
    """This fixture returns a linear context"""
    return Context(100, False, 1)


@pytest.fixture
def circular_context():
    """This fixture returns a circular context"""
    return Context(100, True, 1)


@pytest.fixture
def query_subject_example(scope="module"):
    """This fixture returns an example of a subject and query"""
    subject = ContigRegion(911, 757, Context(9795, True), name="subjectexample", forward=False,
                           filename="templates/pRIAS (CC15).gb")
    query = ContigRegion(1, 155, Context(22240, True), name="queryexample", forward=True,
                         filename="templates/pRasdfasdfaIAS (CC15).gb")
    return [query, subject]


def test_contig_region_with_linear_context(linear_context):
    """This tests instantiation of a contig region using a linear context."""
    c = ContigRegion(1, 100, linear_context, name="example", forward=True, sequence="AGTCAG",
                     filename="somesequence.gb")
    assert c.start == 1
    assert c.end == 100
    assert not c.circular
    assert c.name == "example"
    assert c.direction == Region.FORWARD
    assert c.sequence == "AGTCAG"
    assert c.filename == "somesequence.gb"

def test_contig_region_with_circular_context(circular_context):
    """This test instantiation of a contig region using a circular context."""
    c = ContigRegion(1, 100, circular_context, name="example", forward=False, sequence="AGTCAGAGTCAG",
                     filename="somesequence2.gb")
    assert c.start == 1
    assert c.end == 100
    assert c.circular
    assert c.name == "example"
    assert c.direction == Region.REVERSE
    assert c.sequence == "AGTCAGAGTCAG"
    assert c.filename == "somesequence2.gb"


def test_contig_constructor(query_subject_example):
    """This tests constructing a contig from a subject and query"""
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    assert c.query == query
    assert c.subject == subject

def test_contig_constructor_with_context_error(query_subject_example):
    """This should raise a ContigError since the region lengths between
    r1 and r2 are different"""
    query, subject = query_subject_example
    with pytest.raises(ContigError):
        r1 = Region(1, 2, context=Context(100, True, start_index=1))
        r2 = Region(1, 20, context=Context(100, True, start_index=1))
        Contig(r1, r2, "Throws error")
    # assert c.query_start == query.start
    # assert c.query_end == query.end
    # assert c.subject_start == subject.start
    # assert c.subject_end == subject.end

def test_contig_reverse_direction(query_subject_example):
    """This contig should reverse the direction of contig"""
    query, subject = query_subject_example
    query.sequence = "ACGTAGTGCTGTSCGGCTGTGATGCGT"
    subject.sequence = "ACGTAGTGCTGTSCGGCTGTGATGCGT"
    c = Contig(query, subject, "Example")
    qcopy = query.copy()
    scopy = subject.copy()

    c.reverse_direction()
    assert c.query.start == qcopy.end
    assert c.query.end == qcopy.start
    assert c.subject.start == scopy.end
    assert c.subject.end == scopy.start
    assert c.query.sequence == qcopy.sequence[::-1]
    assert c.subject.sequence == scopy.sequence[::-1]

def test_invalid_region(query_subject_example):
    query, subject = query_subject_example
    query.start = 2
    with pytest.raises(ContigError):
        c = Contig(query, subject, "Example")


def test_alignment_length(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    assert c.alignment_length == query.length


def test_contig_copy(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    c_copy = c.copy()
    assert c_copy is not c
    c2_copy = copy(c)
    assert c2_copy is not c
    assert c2_copy.contig_id != c.contig_id
    assert c_copy.contig_id != c.contig_id
    assert c_copy.contig_id != c2_copy.contig_id


def test_modify_query_start(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    r = c.query
    meth = c.modify_query_start
    p1 = r.start+int(r.length * 0.9)
    p2 = r.start+int(r.length * -0.9)
    p3 = r.start+int(r.length * 10.1)
    p4 = r.start+int(r.length * -10.1)

    for p in [p1, p2]:
        meth(p)
        assert r.start == r.context.translate_pos(p)

    for p in [p3, p4]:
        with pytest.raises(RegionError):
            meth(p)


def test_modify_query_end(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    r = c.query
    meth = c.modify_query_end
    p1 = r.end+int(r.length * 0.9)
    p2 = r.end+int(r.length * -0.9)
    p3 = r.end+int(r.length * 200.1)
    p4 = r.end+int(r.length * -20.1)

    for p in [p1, p2]:
        meth(p)
        assert r.end == r.context.translate_pos(p)

    for p in [p3, p4]:
        with pytest.raises(RegionError):
            meth(p)


def test_modify_subject_start(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    r = c.subject
    meth = c.modify_subject_start
    p1 = r.start+int(r.length * 0.9)
    p2 = r.start+int(r.length * -0.9)
    p3 = r.start+int(r.length * 100.1)
    p4 = r.start+int(r.length * -100.1)

    for p in [p1, p2]:
        meth(p)
        assert r.start == r.context.translate_pos(p)

    for p in [p3, p4]:
        with pytest.raises(RegionError):
            meth(p)


def test_modify_subject_end(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    r = c.subject
    meth = c.modify_subject_end
    p1 = r.end+int(r.length * 0.9)
    p2 = r.end+int(r.length * -0.9)
    p3 = r.end+int(r.length * 200.1)
    p4 = r.end+int(r.length * -200.1)

    for p in [p1, p2]:
        meth(p)
        assert r.end == r.context.translate_pos(p)

    for p in [p3, p4]:
        with pytest.raises(RegionError):
            meth(p)


def test_modify_query(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    qs, qe = query.start-10, query.end-10
    ss, se = subject.start+10, subject.end+10
    c.modify_query(qs, qe)
    assert c.query.start == c.query.context.translate_pos(qs)
    assert c.query.end == c.query.context.translate_pos(qe)
    assert c.query.length == c.subject.length
    assert c.subject.start == c.subject.context.translate_pos(ss)
    assert c.subject.end == c.subject.context.translate_pos(se)

def test_modify_subject(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    qs, qe = query.start-10, query.end-10
    ss, se = subject.start+10, subject.end+10
    c.modify_subject(ss, se)
    assert c.query.start == c.query.context.translate_pos(qs)
    assert c.query.end == c.query.context.translate_pos(qe)
    assert c.query.length == c.subject.length
    assert c.subject.start == c.subject.context.translate_pos(ss)
    assert c.subject.end == c.subject.context.translate_pos(se)

def test_modify_query_ends(query_subject_example):
    query, subject = query_subject_example
    c = Contig(query, subject, "Example")
    le, re = query.left_end + 15, query.right_end - 10
    c.modify_query_ends(le, re)
    assert c.query.left_end == le
    assert c.query.right_end == re
    assert c.query.length == c.subject.length

def test_fuse():
    # Test fuse
    c1 = Context(10000, True)
    c2 = Context(5100, True)
    q1 = ContigRegion(100, 300, context=c1, forward=True)
    q2 = ContigRegion(301, 600, context=c1, forward=True)
    q3 = ContigRegion(301, 600, context=c2, forward=True)
    s1 = ContigRegion(500, 700, context=c2, forward=True)
    s2 = ContigRegion(701, 1000, context=c2, forward=True)
    s3 = ContigRegion(701, 1000, context=c2, forward=True)
    contig1 = Contig(q1, s1, "BLAST")
    contig2 = Contig(q2, s2, "BLAST")

    contig1.fuse(contig2)
    assert contig1.query.end == 600

    # Raises error if one has sequence and other does not
    contig1 = Contig(q1, s1, "BLAST")
    contig2 = Contig(q2, s2, "BLAST")
    a = "A"*contig1.query.length
    b = "B"*contig1.subject.length
    c = "C"*contig2.query.length
    d = "D"*contig2.subject.length
    contig1.query.sequence = a
    contig1.subject.sequence = b
    contig2.query.sequence = c
    contig2.subject.sequence = d

    contig1.fuse(contig2)
    assert contig1.query.sequence == a + c
    assert contig1.subject.sequence == b + d

    # Raises error if one has sequence and other does not
    contig1 = Contig(q1, s1, "BLAST")
    contig2 = Contig(q2, s2, "BLAST")
    contig1.query.sequence = "AGTCTGAGCTGTCGTGATAGTGCTGA"
    contig1.subject.sequence = "AGTYAGYCHYAYHCYHYSCHYHAYCY"

    with pytest.raises(ContigError):
        contig1.fuse(contig2)

    # Raise error if different contexts
    contig1 = Contig(q1, s1, "BLAST")
    contig2 = Contig(q2, s2, "BLAST")
    contig3 = Contig(q3, s3, "BLAST")
    with pytest.raises(ContigError):
        contig3.fuse(contig2)


def test_subquery():
    c1 = Context(10000, True)
    c2 = Context(5000, True)
    q1 = ContigRegion(100, 300, context=c1, forward=True)
    s1 = ContigRegion(500, 700, context=c2, forward=True)

    contig = Contig(q1, s1, "BLAST")
    sub_query1 = contig.sub_query(200, 250)
    sub_query2 = contig.sub_query(220, 300)

    assert len(sub_query1) == 51
    assert len(sub_query2) == 81


def test_divide_contigs():
    c1 = Context(10000, True)
    c2 = Context(8000, True)
    q1 = ContigRegion(1000, 3000, context=c1, forward=True)
    s1 = ContigRegion(5000, 7000, context=c2, forward=True)

    contig = Contig(q1, s1, "BLAST")

    # not including self
    divided_contigs = contig.divide_contig(
        [1100, 1200],
        [2000, 2200, 2300],
        include_self=False)
    assert len(divided_contigs) == 12

    # including self
    divided_contigs = contig.divide_contig(
        [1100, 1200],
        [2000, 2200, 2300],
        include_self=True)
    assert len(divided_contigs) == 13


    # def test_start_end(query_subject_example):
    #     query, subject = query_subject_example
    #     c = Contig(query, subject, "Example")

    # with pytest.raises(ContigError):
    #     c.query.start = 100
    # with pytest.raises(ContigError):
    #     c.subject.start = 100
    # with pytest.raises(ContigError):
    #     c.query.end = 100
    # with pytest.raises(ContigError):
    #     c.subject.end = 100

    # def test_query_setters(query_subject_example):
    #     query, subject = query_subject_example
    #     c = Contig(query, subject, "Example")
    #     assert c.query.length == c.subject.length
    #
    #     # Test query setters
    #     c.query_start = 10
    #     c.query_end = 15
    #     assert c.query.length == c.subject.length
    #     assert c.query_start == c.query.start == 10
    #     assert c.query_end == c.query.end == 15
    #
    #     # Test query setters with errors
    #     with pytest.raises(ContigError):
    #         c.query_start = 1000
    #     with pytest.raises(ContigError):
    #         c.query_end = 1

    # def test_subject_setters(query_subject_example):
    #     query, subject = query_subject_example
    #     c = Contig(query, subject, "Example")
    #
    #     # Test subject setters
    #     query, subject = query_subject_example
    #     c = Contig(query, subject, "Example")
    #     c.subject_start = 1000
    #     c.subject_end = 100
    #     assert c.subject.length == c.query.length
    #     assert c.subject_start == c.subject.start == 1000
    #     assert c.subject_end == c.subject.end == 100
    #
    #     # Test subject setters with errors
    #     with pytest.raises(ContigError):
    #         c.subject_start = 90
    #     with pytest.raises(ContigError):
    #         c.subject_end = 1001

    # def test_contig_overlaps(query_subject_example):
    #     query, subject = query_subject_example
    #     c = Contig(query, subject, "Example")
    #     contig1 = c.copy()
    #     contig2 = c.copy()
    #
    #     contig1.query.start = 1000
    #     contig1.query.end = 2000
    #     contig2.query.start = 2001
    #     contig2.query.end = 3000
    #
    #     assert not contig1.overlaps(contig2)
    #     assert not contig2.overlaps(contig1)
    #
    #     contig2.query.start = contig1.query.end
    #     assert not contig1.overlaps(contig2, inclusive=False)
    #     assert not contig2.overlaps(contig1, inclusive=False)
    #     assert contig1.overlaps(contig2, inclusive=True)
    #     assert contig2.overlaps(contig1, inclusive=True)
    #
    #     contig2.query.start = 1999
    #     assert contig1.overlaps(contig2, inclusive=True)
    #     assert contig2.overlaps(contig1, inclusive=True)
    #     assert contig1.overlaps(contig2, inclusive=False)
    #     assert contig2.overlaps(contig1, inclusive=False)
    #
    # def test_contig_equivalent_location(query_subject_example):
    #     query, subject = query_subject_example
    #     c = Contig(query, subject, "Example")
    #     contig1 = c.copy()
    #     contig2 = c.copy()
    #     contig1.query.start = 1000
    #     contig1.query.end = 2000
    #     contig2.query.start = 2001
    #     contig2.query.end = 3000
    #     assert not contig1.equivalent_location(contig2)
    #
    #     contig1.query.start = 1000
    #     contig1.query.end = 2000
    #     contig2.query.start = 1000
    #     contig2.query.end = 1999
    #     assert not contig1.equivalent_location(contig2)
    #
    #     contig1.query.start = 1000
    #     contig1.query.end = 2000
    #     contig2.query.start = 1000
    #     contig2.query.end = 2000
    #     assert contig1.equivalent_location(contig2)
    #
    # def test_contig_perfect_subject(query_subject_example):
    #     query, subject = query_subject_example
    #     c = Contig(query, subject, "Example")
    #     contig1 = c.copy()
    #
    #     contig1.query.start = 1000
    #     contig1.query.end = 2000
    #     contig1.subject.start = 3000
    #     contig1.subject.end = 4000
    #     contig1.alignment_length
