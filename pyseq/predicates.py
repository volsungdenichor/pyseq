import re


class Predicate:
    def __init__(self, pred):
        self._pred = pred._pred if isinstance(pred, Predicate) \
            else pred if callable(pred) \
            else lambda arg: arg == pred

    def __call__(self, item):
        return self._pred(item)

    def __and__(self, other):
        def result(item):
            return self(item) and other(item)

        return Predicate(result)

    def __or__(self, other):
        def result(item):
            return self(item) or other(item)

        return Predicate(result)

    def __xor__(self, other):
        def result(item):
            return self(item) ^ other(item)

        return Predicate(result)

    def __invert__(self):
        def result(item):
            return not self(item)

        return Predicate(result)

    def __str__(self):
        return str(self._pred)

    __repr__ = __str__


def as_predicate(func):
    def wrapper(*args, **kwargs):
        return Predicate(func(*args, **kwargs))

    return wrapper


always = Predicate(lambda _: True)
never = ~always


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


even = Predicate(lambda arg: arg % 2 == 0)
odd = ~even


@as_predicate
def any_of(*args):
    return lambda arg: arg in args


none = Predicate(lambda arg: arg is None)
not_none = ~none


@as_predicate
def has_len(pred):
    pred = Predicate(pred)
    return lambda arg: pred(len(arg))


empty = has_len(equal(0))
not_empty = ~empty

true = Predicate(bool)
false = ~true


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
def contains(value):
    return lambda arg: value in arg


@as_predicate
def contains_all(*values):
    return lambda arg: all(contains(v)(arg) for v in values)


@as_predicate
def contains_any(*values):
    return lambda arg: any(contains(v)(arg) for v in values)


@as_predicate
def contains_none(*values):
    return lambda arg: not any(contains(v)(arg) for v in values)


@as_predicate
def value_of(key, pred):
    pred = Predicate(pred)
    return lambda arg: key in arg and pred(arg[key])
