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
    _test_pred(has_len(2), [[1, 2], [3, 4]], [[], [1, 2, 3]])
    _test_pred(has_len(less(3)), [[1, 2], [3, 4], []], [[1, 2, 3], [1, 2, 3, 4]])
    _test_pred(of_type(int), [1, 2], [1.2, 'x'])
    _test_pred(of_type(int, float), [1, 2.2], ['x'])
    _test_pred(matches_re('^A[a-z]+a$'), ['Anna', 'Alpha'], ['Aa', 'anna', ''])
    _test_pred(any_of(1, 4, 9), [1, 4, 9], [2, 5, 10])
    _test_pred(contains_all(1, 4), [[1, 2, 3, 4], [1, 4]], [[1], [4]])
    _test_pred(contains_all('a', 'b'), [{'a': 1, 'b': 2}], [])
    _test_pred(has_prefix('error'), ['error'], ['success'])
    _test_pred(has_suffix('error'), ['terror'], ['success'])
    _test_pred(has_sub('error'), ['terrorist'], ['success'])
