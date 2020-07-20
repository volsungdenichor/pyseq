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

    if func is None:
        return identity

    try:
        if sum(1 for p in inspect.signature(func).parameters.values() if is_valid(p)) > 1:
            return unpack(func)
        else:
            return func

    except (TypeError, ValueError):
        return func


# noinspection PyPep8Naming
class indexed:
    def __init__(self, func, start=0):
        self._func = func
        self._index = start

    def __call__(self, *args, **kwargs):
        result = self._func(self._index, *args, **kwargs)
        self._index += 1
        return result


def associate(func):
    def result(item):
        return item, func(item)

    return result


def update_dict_value(func):
    def result(item):
        key, value = item
        return key, func(value)

    return result


# noinspection PyPep8Naming
class nested_getter:
    def __init__(self, *keys):
        self._keys = keys
        self.__name__ = '.'.join(map(str, self._keys))

    def __call__(self, item):
        for key in self._keys:
            item = item[key]
        return item

    def __repr__(self):
        return self.__name__


# noinspection PyPep8Naming
class apply:
    def __init__(self, func, *funcs):
        if funcs:
            self.all_funcs = (func,) + funcs

            def result(item):
                return tuple(f(item) for f in self.all_funcs)

            self._func = result
        else:
            self.all_funcs = (func,)
            self._func = func

        self.__name__ = ';'.join(f.__name__ for f in self.all_funcs)

    def __call__(self, item):
        return self._func(item)

    def __repr__(self):
        return self.__name__


def split_path(path, delimiter='.'):
    path = path.replace('[', f'{delimiter}[')

    def adjust(value):
        if value.startswith('[') and value.endswith(']'):
            return int(value[1:-1])
        else:
            return value

    chunks = map(adjust, path.split(delimiter))
    return chunks


def getter(*paths, delimiter='.'):
    def create(path):
        if isinstance(path, str):
            return nested_getter(*split_path(path, delimiter))
        elif isinstance(path, int):
            return nested_getter(path)
        elif isinstance(path, tuple):
            return nested_getter(*path)
        elif callable(path):
            return path

    return apply(*(create(path) for path in paths))
