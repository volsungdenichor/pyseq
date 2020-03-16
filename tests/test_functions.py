from pyseq.functions import invoke_on_key, invoke_on_value, compose


def test_functions():
    dct = {
        2: 'X',
        3: 'Y'
    }

    key_func = invoke_on_key(compose(lambda x: 10 * x, str, lambda x: f'_{x}_'))
    val_func = invoke_on_value(lambda x: x.lower())

    assert [key_func(item) for item in dct.items()] == ['_20_', '_30_']
    assert [val_func(item) for item in dct.items()] == ['x', 'y']
