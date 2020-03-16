from pyseq.predicates import *


def _test_pred(pred, pos, neg):
    for item in pos:
        assert pred(item)
    for item in neg:
        assert not pred(item)


def test_predicates():
    _test_pred(equal(7) | equal(2),
               pos=[7, 2],
               neg=[1, 3, 8])
    _test_pred(greater(3) & less(6),
               pos=[4, 5],
               neg=[1, 3, 8])
    _test_pred(~equal(3),
               pos=[2, 4, 5],
               neg=[3])
    _test_pred(equal(7),
               pos=[7],
               neg=[1, 2, 3, 8])
    _test_pred(not_equal(7),
               pos=[1, 2, 3, 8],
               neg=[7])
    _test_pred(less(7),
               pos=[1, 2, 3],
               neg=[7, 8, 9, 10])
    _test_pred(less_equal(7),
               pos=[1, 2, 3, 7],
               neg=[8, 9, 10])
    _test_pred(greater(7),
               pos=[8, 9, 10],
               neg=[1, 2, 3, 7])
    _test_pred(greater_equal(7),
               pos=[7, 8, 9, 10],
               neg=[1, 2, 3])
    _test_pred(has_len(2),
               pos=[[1, 2], [3, 4]],
               neg=[[], [1, 2, 3]])
    _test_pred(has_len(less(3)),
               pos=[[1, 2], [3, 4], []],
               neg=[[1, 2, 3], [1, 2, 3, 4]])
    _test_pred(of_type(int),
               pos=[1, 2],
               neg=[1.2, 'x'])
    _test_pred(of_type(int, float),
               pos=[1, 2.2],
               neg=['x'])
    _test_pred(matches_re('^A[a-z]+a$'),
               pos=['Anna', 'Alpha'],
               neg=['Aa', 'anna', ''])
    _test_pred(any_of(1, 4, 9),
               pos=[1, 4, 9],
               neg=[2, 5, 10])
    _test_pred(contains_all(1, 4),
               pos=[[1, 2, 3, 4], [1, 4]],
               neg=[[1], [4]])
    _test_pred(contains_all('a', 'b'),
               pos=[{'a': 1, 'b': 2}],
               neg=[])
    _test_pred(has_prefix('error'),
               pos=['error'],
               neg=['success'])
    _test_pred(has_suffix('error'),
               pos=['terror'],
               neg=['success'])
    _test_pred(has_sub('error'),
               pos=['terrorist'],
               neg=['success'])
    _test_pred(empty,
               pos=[(), [], ""],
               neg=[(1, 2), [3, 4], "x"])
    _test_pred(true,
               pos=[1, "A", [3]],
               neg=[0, "", None])
