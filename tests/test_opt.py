from math import sqrt

import pytest

from pyseq.opt import Opt, OptError


def square_root(x):
    if x > 0:
        return Opt.some(sqrt(x))
    else:
        return Opt.none()


class Sub:
    def __init__(self, a, b):
        self.sub_a = a
        self.sub_b = b


class Super:
    def __init__(self, a, b):
        self.super_a = a
        self.super_b = b


def test_opt():
    assert Opt.some(2) == 2
    assert Opt.some(4).is_some()
    assert Opt.none().is_none()
    assert Opt.some(2).get() == 2
    assert Opt.some(2).get_or(-1) == 2
    assert Opt.none().get_or(-1) == -1
    assert Opt.none().get_or_else(lambda: -1) == -1
    with pytest.raises(OptError):
        assert Opt.none().get_or_raise('A') == -1
    assert Opt.some(2).map(lambda x: x * x) == Opt.some(4)
    assert Opt.none().map(lambda x: x * x) == Opt.none()
    with pytest.raises(RuntimeError, match='Opt not expected'):
        Opt.some(2).map(lambda x: Opt(x))
    assert Opt.some(4).filter(lambda x: x > 2) == Opt.some(4)
    assert Opt.some(1).filter(lambda x: x > 2) == Opt.none()
    assert Opt.none().filter(lambda x: x > 2) == Opt.none()
    assert Opt.some(4).flat_map(square_root) == Opt.some(2)
    assert Opt.none().flat_map(square_root) == Opt.none()
    with pytest.raises(RuntimeError, match='Opt expected'):
        Opt.some(3).flat_map(lambda x: x + 1)
    assert Opt.some(-4).flat_map(square_root) == Opt.none()
    assert Opt.some(2) | Opt.some(4) == Opt.some(2)
    assert Opt.none() | Opt.some(4) == Opt.some(4)
    assert Opt.some(2) & Opt.some(4) == Opt.some(4)
    assert Opt.some(4) & Opt.some(2) == Opt.some(2)
    assert Opt.some(4).exists(lambda x: x > 2)
    assert not Opt.some(4).exists(lambda x: x > 5)
    assert not Opt.none().exists(lambda x: x > 2)
    assert Opt.some(8).contains(8)
    assert not Opt.some(8).contains(7)
    assert not Opt.none().contains(8)
    assert Opt.some(9).or_else(lambda: Opt(4)) == Opt.some(9)
    assert Opt.none().or_else(lambda: Opt(4)) == Opt.some(4)

    item = Super(
        Sub('K', 'L'),
        Sub('M', 'N'))

    assert Opt.some(item).getattr('super_a').getattr('sub_a') == Opt.some('K')
    assert Opt.some(item).getattr('super_b', 'sub_b') == Opt.some('N')
    assert Opt.some(item).getattr('super_b', 'sub_c') == Opt.none()
    assert Opt.some(item).getattr('super_b', 'sub_c', 'd') == Opt.none()

    dct = {'name': {
        'number': [[0, 1, 44]],
        'first': 'Adam',
        'last': 'Mickiewicz'}
    }

    assert Opt.some(dct).getitem('name').getitem('first') == Opt.some('Adam')
    assert Opt.some(dct).getitem('name', 'first') == Opt.some('Adam')
    assert Opt.some(dct).getitem('name', 'middle') == Opt.none()
    assert Opt.some(dct).getitem('name', 'number', 0, 2) == Opt.some(44)
