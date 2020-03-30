import functools
from operator import itemgetter


def do_nothing(*args, **kwargs):
    pass


def identity(arg):
    return arg


def negate(func):
    def result(*args, **kwargs):
        return not func(*args, **kwargs)

    return result


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: g(f(x)), functions)


get_key = itemgetter(0)
get_value = itemgetter(1)


def invoke_on_key(func):
    return compose(get_key, func)


def invoke_on_value(func):
    return compose(get_value, func)


def unpack(func):
    return lambda arg: func(*arg)
