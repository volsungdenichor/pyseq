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


def pipe(*functions):
    return functools.reduce(lambda f, g: lambda x: g(f(x)), functions)


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions)


get_key = itemgetter(0)
get_value = itemgetter(1)


def invoke_on_key(func):
    return pipe(get_key, func)


def invoke_on_value(func):
    return pipe(get_value, func)


def unpack(func):
    return lambda arg: func(*arg)


class Indexed:
    def __init__(self, func, start=0):
        self._func = func
        self._index = start

    def __call__(self, *args, **kwargs):
        result = self._func(self._index, *args, **kwargs)
        self._index += 1
        return result


indexed = Indexed


def associate(func):
    def result(item):
        return item, func(item)

    return result


def update_dict_value(func):
    def result(item):
        key, value = item
        return key, func(value)

    return result


def nested_getter(*keys):
    def result(item):
        for key in keys:
            item = item[key]
        return item

    return result


def getter(path, delimiter='.'):
    return nested_getter(*path.split(delimiter))


def apply(func, *funcs):
    if funcs:
        def result(item):
            return tuple(f(item) for f in (func,) + funcs)

        return result
    else:
        return func
