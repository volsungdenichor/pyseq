import functools
from operator import itemgetter

from pyseq.core import ensure


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
