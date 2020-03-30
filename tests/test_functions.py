from pyseq.functions import invoke_on_key, invoke_on_value, compose, unpack


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

    assert _test_func(unpack(
        lambda k, v: f'{v}_{k * 11}'),
        dct.items()) == ['X_22', 'Y_33']
