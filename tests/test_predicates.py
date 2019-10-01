from pyseq.predicates import *


def _test_pred(pred, pos, neg):
    for item in pos:
        assert pred(item)
    for item in neg:
        assert not pred(item)


def test_predicates():
    _test_pred(equal(7), [7], [1, 2, 3, 8])
    _test_pred(not_equal(7), [1, 2, 3, 8], [7])
    _test_pred(less(7), [1, 2, 3], [7, 8, 9, 10])
    _test_pred(less_equal(7), [1, 2, 3, 7], [8, 9, 10])
    _test_pred(greater(7), [8, 9, 10], [1, 2, 3, 7])
    _test_pred(greater_equal(7), [7, 8, 9, 10], [1, 2, 3])
