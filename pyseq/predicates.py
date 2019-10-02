import operator
import re


class Predicate:
    def __init__(self, pred):
        self._pred = pred._pred if isinstance(pred, Predicate) else pred

    def __call__(self, *args, **kwargs):
        return self._pred(*args, **kwargs)

    def __and__(self, other):
        return self._binary(operator.and_, other)

    def __or__(self, other):
        return self._binary(operator.or_, other)

    def __xor__(self, other):
        return self._binary(operator.xor, other)

    def __invert__(self):
        return self._unary(operator.not_)

    def __str__(self):
        return str(self._pred)

    def _binary(self, op, other):
        def pred(*args, **kwargs):
            return op(self(*args, **kwargs), other(*args, **kwargs))

        return Predicate(pred)

    def _unary(self, op):
        def pred(*args, **kwargs):
            return op(self(*args, **kwargs))

        return Predicate(pred)

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
def has_len(pred):
    if isinstance(pred, int):
        pred = equal(pred)
    return lambda arg: pred(len(arg))


@as_predicate
def empty():
    return has_len(equal(0))


@as_predicate
def not_empty():
    return has_len(greater(0))


@as_predicate
def true():
    return lambda arg: bool(arg)


@as_predicate
def false():
    return lambda arg: not bool(arg)


@as_predicate
def of_type(*types):
    return lambda arg: isinstance(arg, tuple(types))


@as_predicate
def has_prefix(prefix):
    return lambda arg: arg[:len(prefix)] == prefix


@as_predicate
def has_suffix(suffix):
    return lambda arg: arg[-len(suffix):] == suffix


@as_predicate
def has_sub(sub):
    return lambda arg: any(arg[i:i + len(sub)] == sub for i in range(len(arg)))


@as_predicate
def matches_re(pattern):
    r = re.compile(pattern)
    return lambda arg: r.match(arg)


@as_predicate
def contains_all(*values):
    return lambda arg: all(v in arg for v in values)


@as_predicate
def contains_any(*values):
    return lambda arg: any(v in arg for v in values)


@as_predicate
def contains_none(*values):
    return lambda arg: not any(v in arg for v in values)
