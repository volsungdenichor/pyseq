from math import sqrt

from pyseq.opt import Opt


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
    assert Opt.some(2).has_value()
    assert not Opt.none().has_value()
    assert Opt.some(2).value() == 2
    assert Opt.some(2).value_or(-1) == 2
    assert Opt.none().value_or(-1) == -1
    assert Opt.none().value_or_eval(lambda: -1) == -1
    assert Opt.some(2).map(lambda x: x * x) == Opt.some(4)
    assert Opt.none().map(lambda x: x * x) == Opt.none()
    assert Opt.some(4).filter(lambda x: x > 2) == Opt.some(4)
    assert Opt.some(1).filter(lambda x: x > 2) == Opt.none()
    assert Opt.none().filter(lambda x: x > 2) == Opt.none()
    assert Opt.some(4).flat_map(square_root) == Opt.some(2)
    assert Opt.none().flat_map(square_root) == Opt.none()
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

    item = Super(
        Sub('K', 'L'),
        Sub('M', 'N'))

    assert Opt.of_nullable(item).getattr('super_a').getattr('sub_a') == Opt.some('K')
    assert Opt.of_nullable(item).getattr('super_b', 'sub_b') == Opt.some('N')
    assert Opt.of_nullable(item).getattr('super_b', 'sub_c') == Opt.none()
    assert Opt.of_nullable(item).getattr('super_b', 'sub_c', 'd') == Opt.none()

    dct = {'name': {
        'first': 'Adam',
        'last': 'Mickiewicz'}
    }

    assert Opt.of_nullable(dct).getitem('name').getitem('first') == Opt.some('Adam')
    assert Opt.of_nullable(dct).getitem('name', 'first') == Opt.some('Adam')
    assert Opt.of_nullable(dct).getitem('name', 'middle') == Opt.none()
