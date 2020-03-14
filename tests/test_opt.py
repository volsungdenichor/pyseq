from math import sqrt

from pyseq.opt import Opt


def square_root(x):
    if x > 0:
        return Opt.of(sqrt(x))
    else:
        return Opt.none()


def test_opt():
    assert Opt.of(2) == 2
    assert Opt.of(2).has_value()
    assert not Opt.none().has_value()
    assert Opt.of(2).value() == 2
    assert Opt.of(2).value_or(-1) == 2
    assert Opt.none().value_or(-1) == -1
    assert Opt.none().value_or_eval(lambda: -1) == -1
    assert Opt.of(2).map(lambda x: x * x) == Opt.of(4)
    assert Opt.none().map(lambda x: x * x) == Opt.none()
    assert Opt.of(4).filter(lambda x: x > 2) == Opt.of(4)
    assert Opt.of(1).filter(lambda x: x > 2) == Opt.none()
    assert Opt.none().filter(lambda x: x > 2) == Opt.none()
    assert Opt.of(4).flat_map(square_root) == Opt.of(2)
    assert Opt.of(-4).flat_map(square_root) == Opt.none()
    assert Opt.of(2) | Opt.of(4) == Opt.of(2)
    assert Opt.none() | Opt.of(4) == Opt.of(4)
    assert Opt.of(2) & Opt.of(4) == Opt.of(4)
    assert Opt.of(4) & Opt.of(2) == Opt.of(2)
