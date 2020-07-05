import functools
from operator import itemgetter


def do_nothing(*args, **kwargs):
    pass


def identity(arg):
    return arg


def negate(func):
    def result(arg):
        return not func(arg)

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


def to_unary(func):
    import inspect
    from inspect import Parameter

    def is_valid(p):
        return p.kind in [Parameter.POSITIONAL_OR_KEYWORD] and p.default is p.empty

    try:
        if sum(1 for p in inspect.signature(func).parameters.values() if is_valid(p)) > 1:
            return unpack(func)
        else:
            return func

    except (TypeError, ValueError):
        return func


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


def apply(func, *funcs):
    if funcs:
        def result(item):
            return tuple(f(item) for f in (func,) + funcs)

        return result
    else:
        return func


def getter(*paths, **kwargs):
    delimiter = kwargs.pop('delimiter', '.')

    def create(path):
        if isinstance(path, str):
            return nested_getter(*path.split(delimiter))
        elif isinstance(path, int):
            return nested_getter(path)
        elif isinstance(path, tuple):
            return nested_getter(*path)

    return apply(*(create(path) for path in paths))
