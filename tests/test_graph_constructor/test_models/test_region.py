'''
Project: jdna
File: test_region
Author: Justin
Date: 2/23/17

Description:

'''
import pytest
from dasi.graph_constructor.models import Context, Region
from dasi.graph_constructor.exceptions import RegionError


def test_region_construction():
    # Test construction
    c = Context(10, False, 1)
    Region(1, 5, context=Context(10, False, start_index=1))

    # Test invalid, out of bounds Region constructions
    with pytest.raises(RegionError):
        Region(1, 5, direction=Region.FORWARD, context=Context(10, False, start_index=5))
    with pytest.raises(RegionError):
        Region(5, 10, direction=Region.FORWARD, context=Context(5, False, start_index=5))
    with pytest.raises(RegionError):
        Region(5, 10, direction=Region.FORWARD, context=Context(5, False, start_index=1))

    # Test start>end for linear region
    # |--------|
    # 123456789
    #       |>>> ???
    with pytest.raises(RegionError):
        Region(7, 5, direction=Region.FORWARD, context=Context(10, False, start_index=1))

    # Test start>end for linear region
    # |--------|
    # 123456789
    # <<<<|      ???
    with pytest.raises(RegionError):
        Region(5, 7, direction=Region.REVERSE, context=Context(10, False, start_index=1))

    # start>end for forward, circular region
    # Test start>end for linear region
    # |--------|
    # 123456789
    # >>>>| |>>> OK
    Region(7, 5, direction=Region.FORWARD, context=Context(10, True, start_index=1))

    # start>end for reverse, linear region
    # Test start>end for linear region
    # |--------|
    # 123456789
    #     |<|    OK
    Region(7, 5, direction=Region.REVERSE, context=Context(10, False, start_index=1))

    # start<end for reverse, circular region
    # Test start>end for linear region
    # |--------|
    # 123456789
    # <<<<| |<<< OK
    Region(5, 7, direction=Region.REVERSE, context=Context(10, True, start_index=1))


def test_str_and_repr():
    linear_context = Context(100, False, 1)
    r = Region.create_from_ends(5, 10, linear_context, direction=Region.FORWARD)
    print(r)
    print(str(r))


def test_create_from_ends():
    linear_context = Context(100, False, 1)
    circular_context = Context(100, True, 1)

    # Test forward, linear
    r = Region.create_from_ends(5, 10, linear_context, direction=Region.FORWARD)
    assert r.left_end == 5 == r.start
    assert r.right_end == 10 == r.end

    r = Region.create_from_ends(5, 10, linear_context, direction=Region.REVERSE)
    assert r.left_end == 5 == r.end
    assert r.right_end == 10 == r.start

    # Test forward, linear with error
    with pytest.raises(RegionError):
        r = Region.create_from_ends(10, 5, linear_context, direction=Region.FORWARD)
    with pytest.raises(RegionError):
        r = Region.create_from_ends(10, 5, linear_context, direction=Region.REVERSE)

    # when left end > right end is ALWAYS means its circular
    r = Region.create_from_ends(10, 5, circular_context, direction=Region.FORWARD)
    assert r.left_end == 10
    assert r.right_end == 5
    assert r.start == 10
    assert r.end == 5

    r = Region.create_from_ends(10, 5, circular_context, direction=Region.REVERSE)
    assert r.left_end == 10
    assert r.right_end == 5
    assert r.start == 5
    assert r.end == 10


def test_region_properties():
    # Properties of linear region
    r = Region(1, 5, context=Context(10, False, start_index=1))
    assert r.start == 1
    assert r.end == 5
    assert r.context_length == 10
    assert not r.circular
    assert r.start_index == 1

    # Properties of circular region
    r = Region(5, 9, context=Context(10, True, start_index=4))
    assert r.start == 5
    assert r.end == 9
    assert r.context_length == 10
    assert r.circular
    assert r.start_index == 4

    # Properties of circular region
    r = Region(7, 5, direction=Region.REVERSE, context=Context(10, False, start_index=1))
    assert r.start == 7
    assert r.end == 5
    assert r.context_length == 10
    assert not r.circular
    assert r.start_index == 1


def test_len():
    r = Region(1, 5, context=Context(10, False, start_index=1))
    assert r.context_length == 10
    assert r.length == 5
    assert len(r) == 5


def test_faulty_direction():
    with pytest.raises(RegionError):
        s = 1
        e = 5
        l = 10
        r = Region(s, e, direction=5, context=Context(l, True, start_index=0))


def test_reverse_region():
    s = 1
    e = 5
    l = 10
    start_index = 0

    r = Region(e, s, direction=Region.REVERSE, context=Context(l, True, start_index=start_index))
    print(r.start, r.end)
    assert r.start == e
    assert r.end == s


def test_lp_and_rp():
    r = Region(1, 3, direction=Region.FORWARD, context=Context(9, True, start_index=1))
    assert r.lp == 1
    assert r.rp == 3
    assert r.start == r.lp
    assert r.end == r.rp

    r = Region(3, 1, direction=Region.REVERSE, context=Context(9, False, start_index=1))
    assert r.lp == 1
    assert r.rp == 3
    assert r.start == r.rp
    assert r.end == r.lp


def test_lp_and_rp_setter():
    r = Region(1, 3, direction=Region.FORWARD, context=Context(9, False, start_index=1))
    r.lp = 2
    assert r.lp == 2
    r.rp = 5
    assert r.rp == 5
    r.rp = 4

    r = Region(3, 1, direction=Region.REVERSE, context=Context(9, False, start_index=1))
    r.lp = 2
    assert r.lp == 2
    r.rp = 5
    assert r.rp == 5
    r.rp = 4

    r = Region(2, 2, context=Context(9, False, start_index=1))
    r.rp = 3
    assert r.rp == 3 == r.lp
    r.lp = 4
    assert r.rp == 4 == r.lp


def test_end_setter():
    r = Region(2, 5, context=Context(9, False, start_index=1))
    r.left_end = 1
    assert r.start == 1 == r.left_end == r.lp

    r.right_end = 6
    assert r.end == 6 == r.right_end == r.rp

    r = Region(5, 2, direction=Region.REVERSE, context=Context(9, False, start_index=1))
    r.left_end = 1
    assert r.end == 1 == r.left_end == r.lp

    r.right_end = 6
    assert r.start == 6 == r.right_end == r.rp


def test_spans_origin():
    r = Region(1, 3, direction=Region.FORWARD, context=Context(10, True, start_index=0))
    assert not r._spans_origin()
    r = Region(3, 1, direction=Region.FORWARD, context=Context(10, True, start_index=0))
    assert r._spans_origin()

    r = Region(1, 3, direction=Region.REVERSE, context=Context(10, True, start_index=0))
    assert r._spans_origin()
    r = Region(3, 1, direction=Region.REVERSE, context=Context(10, True, start_index=0))
    assert not r._spans_origin()


def test_length():
    # Forward region, circular
    r = Region(1, 3, direction=Region.FORWARD, context=Context(10, True, start_index=0))
    assert r.length == 3

    # Forward region, linear
    r = Region(1, 3, direction=Region.FORWARD, context=Context(10, True, start_index=0))
    assert r.length == 3

    # Reverse region, circular
    r = Region(3, 1, direction=Region.REVERSE, context=Context(10, True, start_index=0))
    assert r.length == 3

    # Reverse region, linear
    r = Region(3, 1, direction=Region.REVERSE, context=Context(10, False, start_index=0))
    assert r.length == 3

    # Span of 1, linear
    r = Region(5, 5, direction=Region.FORWARD, context=Context(10, False, start_index=1))
    assert r.length == 1

    # Span of 1, circular
    r = Region(5, 5, direction=Region.FORWARD, context=Context(10, True, start_index=1))
    assert r.length == 1

    # Over origin, forward
    r = Region(5, 4, direction=Region.FORWARD, context=Context(10, True, start_index=1))
    assert r.length == 10

    # Over origin, reverse
    r = Region(4, 5, direction=Region.REVERSE, context=Context(10, True, start_index=1))
    assert r.length == 10

    # Span 2
    r = Region(4, 5, direction=Region.FORWARD, context=Context(10, True, start_index=1))
    assert r.length == 2


def test_valid_indices():
    r = Region(9, 1, context=Context(9, True, start_index=1))
    assert r._valid_indices(inclusive=True) == [(1, 1), (9, 9)]
    assert r._valid_indices(inclusive=False) == []


def test_region():
    r = Region(2, 2, context=Context(3, True, start_index=1))
    assert r.bounds_end == 3

    s = 1
    e = 2
    l = 10
    start_index = 1
    r = Region(s, e, context=Context(l, True, start_index=start_index))
    assert r.bounds_end == 10
    assert r.bounds_start == start_index
    indices = list(range(start_index - 3, start_index + l - 1 + 3))
    values = list(range(start_index, l + start_index))
    print(values)
    assert len(values) == l
    for x in range(start_index - 3, start_index + l - 1):
        assert r.context.translate_pos(x) == values[x - start_index]
    for x in range(start_index + l - 1, start_index + l - 1 + 3):
        assert r.context.translate_pos(x) == values[x - start_index - len(values)]

    with pytest.raises(RegionError):
        Region(500, 100, context=Context(1000, False))

    start_index = 10
    r = Region(100, 500, context=Context(1000, True, start_index=start_index))
    assert r.bounds_start == start_index
    assert r.bounds_end == start_index + r.context_length - 1
    for x in range(-5, 300):
        r = Region(100, x, context=Context(200, True, start_index=30))
        assert r.end <= r.bounds_end
    for x in range(-5, 300):
        r = Region(x, 100, context=Context(200, True, start_index=30))
        assert r.start >= r.bounds_start


def test_region_within():
    r = Region(1000, 2000, context=Context(4000, True, start_index=1))
    assert r.within_region(1000, inclusive=True)
    assert not r.within_region(1000, inclusive=False)
    assert r.within_region(1500, inclusive=True)
    assert r.within_region(2000, inclusive=True)
    assert not r.within_region(2000, inclusive=False)
    assert not r.within_region(2001, inclusive=True)
    assert not r.within_region(999, inclusive=True)

    r = Region(900, 100, context=Context(1000, True, start_index=1))
    assert r.within_region(1, inclusive=True)
    assert r.within_region(10, inclusive=True)
    assert r.within_region(901, inclusive=True)
    assert not r.within_region(0, inclusive=True)
    assert r.within_region(900, inclusive=True)
    assert not r.within_region(900, inclusive=False)
    assert not r.within_region(100, inclusive=False)
    assert r.within_region(100, inclusive=True)

    r = Region(1, 9, context=Context(9, True, start_index=1))
    assert r.within_region(1)
    assert not r.within_region(1, inclusive=False)


def test_region_copy():
    r = Region(50, 20, context=Context(1000, False, 2), name='name', direction=Region.REVERSE)
    r2 = r.copy()
    assert r.same_context(r2)


def test_region_gap_basic():
    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(60, 70, context=Context(100, False, start_index=0))
    g = r.get_gap(r2)
    assert g.lp == 51
    assert g.rp == 59

    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(51, 70, context=Context(100, False, start_index=0))
    assert r.get_gap(r2) is None

    r = Region(90, 99, context=Context(100, False, start_index=1))
    r2 = Region(2, 70, context=Context(100, False, start_index=1))
    g = r.get_gap(r2)
    assert g.start == 100
    assert g.end == 1

    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(48, 70, context=Context(100, False, start_index=0))
    g = r.get_gap(r2)
    assert g is None


def test_circular_gaps():
    """
        context:   |-------------------------|
        r1:         ----|              |-----
        r2:                  |----|
        r1.get_gap(r2)   |==|
        r2.get_gap(r1)             |==|
    """

    r1 = Region(80, 20, context=Context(100, True, start_index=0))
    r2 = Region(50, 60, context=Context(100, True, start_index=0))

    g1 = r1.get_gap(r2)
    assert g1.start == 21
    assert g1.end == 49

    g2 = r2.get_gap(r1)
    assert g2.start == 61
    assert g2.end == 79


def test_self_circular_gap():
    """
        context:   |-------------------------|
        r1:         ----|              |-----
        r1.gap(r1)       |>>>>>>>>>>>>|
    """

    r1 = Region(80, 20, context=Context(100, True, start_index=0))
    g = r1.get_gap(r1)
    assert g.start == 21
    assert g.end == 79


def test_gap_span():
    r = Region(1, 100, context=Context(100, True, start_index=1))
    r2 = Region(10, 90, context=Context(100, True, start_index=1))
    assert r.get_gap_span(r2) is None

    r = Region(1, 10, context=Context(100, True, start_index=1))
    r2 = Region(10, 90, context=Context(100, True, start_index=1))
    assert r.get_gap_span(r2) == -1

    r = Region(1, 10, context=Context(100, True, start_index=1))
    r2 = Region(11, 90, context=Context(100, True, start_index=1))
    assert r.get_gap_span(r2) == 0

    r = Region(1, 10, context=Context(100, True, start_index=1))
    r2 = Region(8, 90, context=Context(100, True, start_index=1))
    assert r.get_gap_span(r2) == -3

    r = Region(1, 10, context=Context(100, True, start_index=1))
    r2 = Region(15, 90, context=Context(100, True, start_index=1))
    assert r.get_gap_span(r2) == 4


def test_gap():
    # Test when r2 is contained in r1
    r = Region(1, 100, context=Context(100, True, start_index=1))
    r2 = Region(10, 90, context=Context(100, True, start_index=1))
    g = r.get_gap(r2)
    assert g is None

    # Test when r2 is contained in r1; test on end
    r = Region(1, 100, context=Context(100, True, start_index=1))
    r2 = Region(10, 100, context=Context(100, True, start_index=1))
    g = r.get_gap(r2)
    assert g is None

    # Test when r2 is contained in r1; test on start
    r = Region(1, 100, context=Context(100, True, start_index=1))
    r2 = Region(1, 10, context=Context(100, True, start_index=1))
    g = r.get_gap(r2)
    assert g is None

    r = Region(25, 90, context=Context(100, True, start_index=1))
    r2 = Region(1, 10, context=Context(100, True, start_index=1))

    # Test outer gap
    g = r.get_gap(r2)
    assert r.get_gap_span(r2) == g.length
    assert r.get_gap_span(r2) == 10

    # Test inner gap
    g = r2.get_gap(r)
    assert r2.get_gap_span(r) == g.length
    assert g.length == 14

    # Test overlap
    r = Region(1, 10, context=Context(100, True, start_index=1))
    r2 = Region(5, 15, context=Context(100, True, start_index=1))
    g = r.get_gap(r2)
    assert g is None

    r = Region(1, 10, context=Context(100, True, start_index=1))
    r2 = Region(10, 15, context=Context(100, True, start_index=1))
    g = r.get_gap(r2)
    assert g is None


def test_reverse_direction():
    # is_forward and is_reverse
    r = Region(10, 50, context=Context(100, False, start_index=0))
    assert r.is_forward()
    assert not r.is_reverse()

    r = Region(50, 10, direction=Region.REVERSE, context=Context(100, False, start_index=0))
    assert r.is_reverse()
    assert not r.is_forward()
    assert r.length == 41

    # reverse_direction
    r.reverse_direction()
    assert r.is_forward()
    assert not r.is_reverse()
    assert r.length == 41

    # reverse back
    r.reverse_direction()
    assert r.is_reverse()
    assert not r.is_forward()
    assert r.length == 41

    r.set_forward()
    assert r.is_forward()
    assert r.length == 41

    r.set_reverse()
    assert r.is_reverse()
    assert r.length == 41

    r.set_reverse()
    assert r.is_reverse()
    assert r.length == 41


def test_ends_overlaps_with():
    r = Region(10, 50, context=Context(100, False, start_index=0))
    r2 = Region(20, 90, context=Context(100, False, start_index=0))
    assert r.end_overlaps_with(r2)
    assert not r2.end_overlaps_with(r)


def test_ends_overlap_with_raise_region_error():
    """This test should raise an error since the contexts are different"""
    with pytest.raises(RegionError):
        r = Region(10, 50, context=Context(100, False, start_index=0))
        r2 = Region(20, 90, context=Context(100, True, start_index=0))
        r.end_overlaps_with(r2)

    with pytest.raises(RegionError):
        r = Region(10, 50, context=Context(100, False, start_index=0))
        r2 = Region(20, 90, context=Context(100, False, start_index=1))
        r.end_overlaps_with(r2)


def test_ends_overlap_with_circular_context():
    """This tests handling of circular context with end overlaps"""
    r = Region(90, 10, context=Context(100, True, start_index=2))
    r2 = Region(5, 20, context=Context(100, True, start_index=2))
    assert r.end_overlaps_with(r2)
    assert not r2.end_overlaps_with(r)


def test_ends_overlap_with_reverse_regions():
    """This tests ends overlaps with reverse regions"""
    r = Region(50, 10, direction=Region.REVERSE, context=Context(100, False, start_index=0))
    r2 = Region(90, 20, direction=Region.REVERSE, context=Context(100, False, start_index=0))
    assert r.end_overlaps_with(r2)
    assert not r2.end_overlaps_with(r)


def test_overlap_linear_forward():
    """This tests that overlap region has basic attributes expected"""
    r = Region(10, 50, context=Context(100, False, start_index=0))
    r2 = Region(20, 90, context=Context(100, False, start_index=0))
    overlap = r.get_overlap(r2)
    print(overlap.start, overlap.end)
    assert overlap.same_context(r)
    assert overlap.same_context(r2)
    assert overlap.start == 20
    assert overlap.end == 50
    assert overlap.direction == r.direction
    assert r2.get_overlap(r) is None


def test_overlap_circular():
    """
    Tests overlap with circular regions

    r1 ------|        |-------
    r2 ---------|        |----
    """
    r1 = Region(90, 10, context=Context(100, True, start_index=2))
    r2 = Region(95, 20, context=Context(100, True, start_index=2))
    overlap = r1.get_overlap(r2)
    assert overlap.start == 95
    assert overlap.end == 10


# def test_self_overlap():
#     raise NotImplementedError("Self wrapping regions are not implemented.")

def test_raise_context_error():
    with pytest.raises(RegionError):
        r = Region(10, 50, context=Context(100, True, start_index=0))
        r2 = Region(20, 90, context=Context(100, False, start_index=0))
        r.consecutive_with(r2)

    with pytest.raises(RegionError):
        r = Region(10, 50, context=Context(100, False, start_index=0))
        r2 = Region(20, 90, context=Context(101, False, start_index=0))
        r.consecutive_with(r2)

    with pytest.raises(RegionError):
        r = Region(10, 50, context=Context(100, False, start_index=1))
        r2 = Region(20, 90, context=Context(100, False, start_index=0))
        r.consecutive_with(r2)


def test_subregion():
    r = Region(20, 50, context=Context(100, False, start_index=0))
    r.sub_region(20, 30)
    s = r.sub_region(30, 50)
    assert s.start == 30
    assert s.end == 50
    with pytest.raises(RegionError):
        r.sub_region(19, 30)
    with pytest.raises(RegionError):
        r.sub_region(30, 51)

    r = Region(90, 10, context=Context(100, True, start_index=0))
    s = r.sub_region(95, 5)
    s_compare = Region(95, 5, context=Context(100, True, start_index=0))
    assert s.start == 95
    assert s.end == 5
    assert s_compare.length == s.length


def test_get_gap_degree():
    pass


def test_consecutive_with():
    # is consecutive
    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(51, 70, context=Context(100, False, start_index=0))
    assert r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    # has gap
    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(52, 70, context=Context(100, False, start_index=0))
    assert not r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    # same indices
    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(50, 70, context=Context(100, False, start_index=0))
    assert not r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    # has overlap
    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(49, 70, context=Context(100, False, start_index=0))
    assert not r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    # linear regions over origin
    r = Region(20, 100, context=Context(100, False, start_index=1))
    r2 = Region(1, 10, context=Context(100, False, start_index=1))
    assert not r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    # linear regions over origin
    r = Region(1, 10, context=Context(100, False, start_index=1))
    r2 = Region(11, 30, context=Context(100, False, start_index=1))
    assert r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    # circular regions over origin
    r = Region(20, 100, context=Context(100, True, start_index=1))
    r2 = Region(1, 10, context=Context(100, True, start_index=1))
    assert r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    # self consecutive with
    r = Region(20, 19, context=Context(100, True))
    assert r.consecutive_with(r)

    with pytest.raises(RegionError):
        r = Region(20, 50, context=Context(100, False, start_index=0))
        r2 = Region(51, 70, context=Context(100, False, start_index=1))
        r.consecutive_with(r2)

    r = Region(90, 10, context=Context(100, True, start_index=1))
    r2 = Region(11, 20, context=Context(100, True, start_index=1))
    assert r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    r = Region(10, 90, direction=Region.REVERSE, context=Context(100, True, start_index=1))
    r2 = Region(11, 20, direction=Region.FORWARD, context=Context(100, True, start_index=1))
    assert r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    r = Region(10, 90, direction=Region.REVERSE, context=Context(100, True, start_index=1))
    r2 = Region(89, 20, direction=Region.REVERSE, context=Context(100, True, start_index=1))
    assert not r.consecutive_with(r2)
    assert r2.consecutive_with(r)


def test_region_fuse():
    # Fusing two linear regions
    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(51, 70, context=Context(100, False, start_index=0))
    assert r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    r.fuse(r2)
    assert r2.fuse(r) is None

    r = Region(95, 100, context=Context(100, True, start_index=1))
    r2 = Region(1, 70, context=Context(100, True, start_index=1))
    assert r.consecutive_with(r2)
    assert not r2.consecutive_with(r)

    r.fuse(r2)
    assert r.start == 95
    assert r.end == 70
    assert r2.start == 1
    assert r2.end == 70

    r = Region(1, 100, context=Context(100, False, start_index=1))
    r2 = Region(5, 99, context=Context(100, False, start_index=1))
    assert not r.consecutive_with(r2)

    r = Region(20, 50, context=Context(100, False, start_index=0))
    r2 = Region(51, 70, context=Context(100, False, start_index=0))
    f = r.fuse(r2, inplace=False)
    assert r is not f


def test_extend_start():
    # linear, forward
    r = Region(10, 20, context=Context(100, False, start_index=1))
    r.extend_start(5)
    assert r.start == 5

    # linear, reverse
    r = Region(20, 10, direction=Region.REVERSE, context=Context(100, False, start_index=1))
    r.extend_start(5)
    assert r.start == 25

    # linear, forward, negative
    r = Region(10, 20, context=Context(100, False, start_index=1))
    r.extend_start(-5)
    assert r.start == 15

    # linear, reverse, negative
    r = Region(20, 10, direction=Region.REVERSE, context=Context(100, False, start_index=1))
    r.extend_start(-5)
    assert r.start == 15

    # over origin, forward
    # 95 96 97 98 99 100 1 2 3 4
    # -5 -4 -3 -2 -1  0
    r = Region(-5, 5, direction=Region.FORWARD, context=Context(100, True, start_index=1))
    r.extend_start(-6)
    assert r.start == 1

    # Retract by length
    r = Region(5, 10, direction=Region.FORWARD, context=Context(100, True, start_index=1))
    r.extend_start(-r.length + 1)
    assert r.start == r.end

    # Throw error
    r = Region(5, 10, direction=Region.FORWARD, context=Context(100, True, start_index=1))
    with pytest.raises(RegionError):
        r.extend_start(-r.length)

    r = Region(2, 4, direction=Region.FORWARD, context=Context(12, True, start_index=1))
    r.extend_start(9)
    with pytest.raises(RegionError):
        r.extend_start(10)


def test_extend_end():
    # linear, forward
    r = Region(10, 20, context=Context(100, False, start_index=1))
    r.extend_end(5)
    assert r.end == 25

    # linear, reverse
    r = Region(20, 10, direction=Region.REVERSE, context=Context(100, False, start_index=1))
    r.extend_end(5)
    assert r.end == 5

    # linear, forward, negative
    r = Region(10, 20, context=Context(100, False, start_index=1))
    r.extend_end(-5)
    assert r.end == 15

    # linear, reverse, negative
    r = Region(20, 10, direction=Region.REVERSE, context=Context(100, False, start_index=1))
    r.extend_end(-5)
    assert r.end == 15

    # over origin, forward
    r = Region(-5, 5, direction=Region.FORWARD, context=Context(100, True, start_index=1))
    r.extend_end(-5)
    assert r.end == 100

    # Retract by length
    r = Region(5, 10, direction=Region.FORWARD, context=Context(100, True, start_index=1))
    r.extend_end(-r.length + 1)
    assert r.start == r.end

    # Raise error
    r = Region(5, 10, direction=Region.FORWARD, context=Context(100, True, start_index=1))
    with pytest.raises(RegionError):
        r.extend_end(-r.length)

    r = Region(2, 4, direction=Region.FORWARD, context=Context(12, True, start_index=1))
    r.extend_end(9)
    with pytest.raises(RegionError):
        r.extend_end(10)


def test_extend_end():
    r = Region(40, 30, direction=Region.REVERSE, context=Context(100, True, start_index=1))
    re = 15
    le = 7
    l = r.length
    r.extend_right_end(re)
    r.extend_left_end(le)
    assert r.right_end == 40 + re
    assert r.left_end == 30 - le
    assert r.length == l + re + le

    r = Region(40, 30, direction=Region.REVERSE, context=Context(100, True, start_index=1))
    re = -3
    le = -2
    l = r.length
    r.extend_right_end(re)
    r.extend_left_end(le)
    assert r.right_end == 40 + re
    assert r.left_end == 30 - le
    assert r.length == l + re + le


def test_eq_location():
    r = Region(10, 20, context=Context(100, False, start_index=1))
    r2 = Region(10, 20, context=Context(100, False, start_index=1))
    r3 = Region(10, 20, context=Context(110, False, start_index=1))
    assert r.equivalent_location(r2)
    assert r2.equivalent_location(r)
    with pytest.raises(RegionError):
        r.equivalent_location(r3)
    with pytest.raises(RegionError):
        r3.equivalent_location(r)

        # assert r.translate_pos(-1) == -1 + l
        # assert r.translate_pos(l + start_index - 1 + 2) == start_index + 2 - 1



        # for start_index in range(-2, 2):
        #     indices = np.array(range(start_index - 10, l + 10))
        #     new_indices = indices + start_index
        #     for i, pos in enumerate(indices):
        #         start_index = 0
        #         r = Region(5, 99, circular=True, context=Context(100, False, start_index=start_index))
        #         x = r.translate_pos(pos)
        #         assert x == new_indices[i]
