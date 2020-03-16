from pyseq.functions import invoke_on_key, invoke_on_value, compose, with_input, replace, replace_if
from pyseq.predicates import odd


def _test_func(func, lst):
    return [func(x) for x in lst]


def test_functions():
    dct = {
        2: 'X',
        3: 'Y'
    }

    assert _test_func(
        invoke_on_key(compose(lambda x: 10 * x, str, lambda x: f'_{x}_')),
        dct.items()) == ['_20_', '_30_']

    assert _test_func(
        invoke_on_value(str.lower),
        dct.items()) == ['x', 'y']

    assert _test_func(
        replace(2, -1),
        [1, 2, 3]) == [1, -1, 3]

    assert _test_func(
        replace_if(odd, -1),
        [0, 1, 2, 3, 4, 5]) == [0, -1, 2, -1, 4, -1]

    assert _test_func(
        with_input(lambda x: x ** 2),
        [1, 2, 3, 4]) == [(1, 1), (2, 4), (3, 9), (4, 16)]
