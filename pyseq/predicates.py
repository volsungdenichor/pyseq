class Predicate:
    def __init__(self, pred):
        self._pred = pred._pred if isinstance(pred, Predicate) else pred

    def __call__(self, *args, **kwargs):
        return self._pred(*args, **kwargs)

    def __and__(self, other):
        def pred(*args, **kwargs):
            return self(*args, **kwargs) and other(*args, **kwargs)

        return Predicate(pred)

    def __or__(self, other):
        def pred(*args, **kwargs):
            return self(*args, **kwargs) or other(*args, **kwargs)

        return Predicate(pred)

    def __invert__(self):
        def pred(*args, **kwargs):
            return not self(*args, **kwargs)

        return Predicate(pred)

    def __str__(self):
        return str(self._pred)

    __repr__ = __str__


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
    return lambda arg: arg == value


@as_predicate
def ne(value):
    return lambda arg: arg != value


@as_predicate
def lt(value):
    return lambda arg: arg < value


@as_predicate
def le(value):
    return lambda arg: arg <= value


@as_predicate
def gt(value):
    return lambda arg: arg > value


@as_predicate
def ge(value):
    return lambda arg: arg >= value


equal = eq
not_equal = ne
less = lt
less_equal = le
greater = gt
greater_equal = ge


@as_predicate
def between(lo, up):
    return lambda arg: lo <= arg < up


@as_predicate
def divisible_by(d):
    return lambda arg: arg % d == 0


@as_predicate
def even():
    return lambda arg: arg % 2 == 0


@as_predicate
def odd():
    return lambda arg: arg % 2 == 1


@as_predicate
def any_of(*args):
    return lambda arg: arg in args


@as_predicate
def none():
    return lambda arg: arg is None


@as_predicate
def not_none():
    return lambda arg: arg is not None


@as_predicate
def empty():
    return lambda arg: len(arg) == 0


@as_predicate
def not_empty():
    return lambda arg: len(arg) > 0


@as_predicate
def true():
    return lambda arg: bool(arg)


@as_predicate
def false():
    return lambda arg: not bool(arg)


@as_predicate
def of_type(t):
    return lambda arg: isinstance(arg, t)
