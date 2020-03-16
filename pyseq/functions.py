import functools
from operator import itemgetter


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
