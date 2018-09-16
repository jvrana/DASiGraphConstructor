import pytest

from dasi import Context
from dasi.exceptions import RegionError


def test_context_constructor():
    opts = [
        [10, False, 1],
        [15, True, 3]
    ]
    for args in opts:
        c = Context(*args)
        assert c.length == args[0]
        assert c.start == args[2]
        assert len(c) == args[0]
        assert c.circular == args[1]


def test_context_span():
    c = Context(9, False, 1)
    assert c.span(1, 3) == 3
    assert c.span(3, 1) is None
    c = Context(9, True, 1)
    assert c.span(3, 1) == 8


def test_context_translate_pos():
    c = Context(10, False, 1)
    for p in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        c.translate_pos(p)
    for p in [0, 11, -1, 15, 20]:
        with pytest.raises(RegionError):
            c.translate_pos(p)

    c = Context(10, True, 1)
    for p in [0, 11, -1, 15, 20]:
        c.translate_pos(p)
    assert c.translate_pos(11) == 1


def test_within_bounds():
    c = Context(100, False, 1)
    assert c.within_bounds(50)
    assert not c.within_bounds(101)
    assert c.within_bounds(100)
    assert c.within_bounds(1)
    assert not c.within_bounds(100, inclusive=False)
    assert not c.within_bounds(1, inclusive=False)


def test_str_and_repr():
    c = Context(100, False, 1)
    print(c)
