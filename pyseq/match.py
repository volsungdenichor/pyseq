from pyseq.predicates import Predicate, always


class MatchError(Exception):
    pass


def _is_type(o):
    return isinstance(o, type)


def _try_invoke(func, item):
    try:
        return func(item)
    except TypeError:
        return func()


def _convert_pred(pred):
    return Predicate(pred)


def _convert_func(func):
    if callable(func):
        return func
    else:
        return lambda item: func


class _Handler:
    def __init__(self, pred, func):
        self._pred = _convert_pred(pred)
        self._func = _convert_func(func)

    def matches(self, item):
        return _try_invoke(self._pred, item)

    def get_result(self, item):
        return _try_invoke(self._func, item)


class _When:
    def __init__(self, pred):
        self._pred = pred

    def then(self, func):
        return _Handler(self._pred, func)

    def __rshift__(self, other):
        return self.then(other)


def _validate_handlers(*handlers):
    assert all(isinstance(x, _Handler) for x in handlers)


def when(pred):
    return _When(pred)


__ = always


def match(item, *handlers):
    _validate_handlers(*handlers)
    for handler in handlers:
        if handler.matches(item):
            return handler.get_result(item)

    raise MatchError("No match")


def create_matcher(*handlers):
    def result(item):
        return match(item, *handlers)

    return result
