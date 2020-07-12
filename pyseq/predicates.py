import re
from decimal import Decimal
from math import isclose


def format(values):
    return ','.join(map(str, values))


class Predicate:
    def __init__(self, pred, name=None):
        if isinstance(pred, Predicate):
            self._pred = pred._pred
            self._name = name or pred._name
        else:
            if callable(pred):
                self._pred = pred
                self._name = name or str(self._pred)
            else:
                self._pred = lambda arg: arg == pred
                self._name = f'equal to {pred}'

    def __call__(self, arg):
        return self._pred(arg)

    def __and__(self, other):
        return Predicate(lambda arg: self(arg) and other(arg), f'({self}) and ({other})')

    def __or__(self, other):
        return Predicate(lambda arg: self(arg) or other(arg), f'({self}) or ({other})')

    def __xor__(self, other):
        return Predicate(lambda arg: self(arg) ^ other(arg), f'({self}) xor ({other})')

    def __invert__(self):
        return Predicate(lambda arg: not self(arg), f'not ({self})')

    @staticmethod
    def all(*preds):
        return Predicate(lambda arg: all(map(lambda p: p(arg), preds)), f'all [{format(preds)}]')

    @staticmethod
    def any(*preds):
        return Predicate(lambda arg: any(map(lambda p: p(arg), preds)), f'any [{format(preds)}]')

    @staticmethod
    def none(*preds):
        return Predicate(lambda arg: not any(map(lambda p: p(arg), preds)), f'any [{format(preds)}]')

    def alias(self, name):
        return Predicate(self._pred, name)

    def __str__(self):
        return self._name

    __repr__ = __str__


def as_predicate(func):
    return Predicate(func, func.__name__)


always = Predicate(lambda _arg: True, 'always')
never = always.alias('never')


def eq(value):
    return Predicate(lambda arg: arg == value, f'equal to {value}')


def ne(value):
    return Predicate(lambda arg: arg != value, f'not equal to {value}')


def lt(value):
    return Predicate(lambda arg: arg < value, f'less than {value}')


def le(value):
    return Predicate(lambda arg: arg <= value, f'less than or equal to {value}')


def gt(value):
    return Predicate(lambda arg: arg > value, f'greater than {value}')


def ge(value):
    return Predicate(lambda arg: arg >= value, f'greater than or equal to {value}')


equal = eq
not_equal = ne
less = lt
less_equal = le
greater = gt
greater_equal = ge

positive = greater(0.0).alias('positive')
negative = less(0.0).alias('negative')
non_negative = greater_equal(0.0).alias('non-negative')
non_positive = less_equal(0.0).alias('non-positive')
non_zero = not_equal(0.0).alias('non-zero')


def approx_equal(value, rel_tol=None, abs_tol=None):
    kwargs = {}
    if abs_tol is not None:
        kwargs['abs_tol'] = abs_tol
    if rel_tol is not None:
        kwargs['rel_tol'] = rel_tol
    return Predicate(lambda arg: isclose(arg, value, **kwargs), f'approx equal to {value}')


def between(lo, up):
    return Predicate(lambda arg: lo <= arg <= up, f'between {lo} and {up}')


def divisible_by(d):
    return Predicate(lambda arg: arg % d == 0, f'divisible by {d}')


even = Predicate(divisible_by(2), 'even')
odd = (~even).alias('odd')


def any_of(*args):
    return Predicate(lambda arg: arg in args, f'any of {format(args)}')


none = Predicate(lambda arg: arg is None, 'none')
not_none = (~none).alias('not none')


def has_len(pred):
    pred = Predicate(pred)
    return Predicate(lambda arg: pred(len(arg)), f'has len {pred}')


empty = Predicate(has_len(equal(0)), 'empty')
not_empty = (~empty).alias('not empty')

true = Predicate(bool, 'true')
false = (~true).alias('false')


def of_type(*types):
    names = format(t.__name__ for t in types)
    return Predicate(lambda arg: isinstance(arg, types), f'of type {names}')


numeric = of_type(int, float, Decimal).alias('numeric')


def has_prefix(prefix):
    return Predicate(lambda arg: arg[:len(prefix)] == prefix, f'has prefix {prefix}')


def has_suffix(suffix):
    return Predicate(lambda arg: arg[-len(suffix):] == suffix, f'has suffix {suffix}')


def has_sub(sub):
    return Predicate(lambda arg: any(arg[i:i + len(sub)] == sub for i in range(len(arg))), f'has sub {sub}')


def matches_re(pattern):
    r = re.compile(pattern)
    return Predicate(lambda arg: r.match(arg), f'matches regex {pattern}')


def contains(value):
    return Predicate(lambda arg: value in arg, f'contains {value}')


def inside(value):
    return Predicate(lambda arg: arg in value, f'inside {value}')


def contains_all_of(*values):
    return Predicate.all(*(contains(v) for v in values)).alias(f'contains all of {format(values)}')


def contains_any_of(*values):
    return Predicate.any(*(contains(v) for v in values)).alias(f'contains any of {format(values)}')


def contains_none_of(*values):
    return Predicate.none(*(contains(v) for v in values)).alias(f'contains none of {format(values)}')
