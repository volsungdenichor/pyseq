class Predicate:
    def __init__(self, pred):
        self._pred = pred

    def __call__(self, item):
        return self._pred(item)

    def __and__(self, other):
        return Predicate(lambda item: self(item) and other(item))

    def __or__(self, other):
        return Predicate(lambda item: self(item) or other(item))

    def __invert__(self):
        return Predicate(lambda item: not self(item))


def as_predicate(func):
    def wrapper(*args, **kwargs):
        return Predicate(func(*args, **kwargs))

    return wrapper


@as_predicate
def always():
    return lambda _: True


@as_predicate
def never():
    return lambda _: False


@as_predicate
def eq(value):
    return lambda item: item == value


@as_predicate
def ne(value):
    return lambda item: item != value


@as_predicate
def lt(value):
    return lambda item: item < value


@as_predicate
def le(value):
    return lambda item: item <= value


@as_predicate
def gt(value):
    return lambda item: item > value


@as_predicate
def ge(value):
    return lambda item: item >= value


@as_predicate
def between(lo, up):
    return lambda item: lo <= item < up


@as_predicate
def divisible_by(d):
    return lambda item: item % d == 0


@as_predicate
def even():
    return lambda item: item % 2 == 0


@as_predicate
def odd():
    return lambda item: item % 2 == 1


@as_predicate
def any_of(*args):
    return lambda item: item in args


@as_predicate
def none():
    return lambda item: item is None


@as_predicate
def not_none():
    return lambda item: item is not None


@as_predicate
def is_true():
    return lambda item: bool(item)


@as_predicate
def is_false():
    return lambda item: not bool(item)


@as_predicate
def of_type(t):
    return lambda item: isinstance(item, t)
