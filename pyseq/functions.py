import functools
from operator import itemgetter

from pyseq.core import ensure
from pyseq.opt import Opt


def identity(x):
    return x


def negate(func):
    def result(*args, **kwargs):
        return not func(*args, **kwargs)

    return result


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: g(f(x)), functions, identity)


get_key = itemgetter(0)
get_value = itemgetter(1)


def invoke_on_key(func):
    return compose(get_key, func)


def invoke_on_value(func):
    return compose(get_value, func)


def with_input(func):
    return lambda arg: (arg, func(arg))


def replace_if(pred, new_value):
    return lambda arg: new_value if pred(arg) else arg


def replace(old_value, new_value):
    return lambda arg: new_value if arg == old_value else arg


def raise_error(error):
    def result(*args, **kwargs):
        ensure(False, error)

    return result


def get(dct, key):
    return Opt.some(dct).getitem(key)


def getter(key):
    return lambda dct: get(dct, key)


def get_nested(dct, *keys):
    return Opt.some(dct).getitem(*keys)


def nested_getter(*keys):
    return lambda dct: get_nested(dct, *keys)


def invoke_on_tuple(func):
    return lambda arg: func(*arg)


unpack = invoke_on_tuple
