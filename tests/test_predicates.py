from pyseq.predicates import eq


def test_eq():
    pred = eq(7)
    assert pred(7)
