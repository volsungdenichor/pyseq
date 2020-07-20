import re
from decimal import Decimal
from functools import wraps
from math import isclose

from pyseq.functions import getter


def _fmt(values):
    return ';'.join(map(str, values))


def as_predicate(message):
    import inspect

    def wrapper(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if isinstance(func, inspect.Signature):
                signature = func
            else:
                signature = inspect.signature(func)

            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            arg_values = dict(bound_args.arguments)

            return Predicate(pred=func(*args, **kwargs),
                             name=message.format(**arg_values))

        return func_wrapper

    return wrapper


class Predicate:
    def __init__(self, pred, name=None):
        if isinstance(pred, Predicate):
            self._pred = pred._pred
            self.__name__ = name or pred.__name__
        else:
            if callable(pred):
                self._pred = pred
                self.__name__ = name or str(self._pred)
            elif isinstance(pred, type):
                self._pred = lambda arg: isinstance(arg, pred)
                self.__name__ = f'of type {pred.__name__}'
            elif isinstance(pred, tuple) and all(isinstance(p, type) for p in pred):
                self._pred = lambda arg: isinstance(arg, pred)
                self.__name__ = f'of type ' + ','.join(p.__name__ for p in pred)
            else:
                self._pred = lambda arg: arg == pred
                self.__name__ = f'equal to {pred}'

    def __call__(self, arg):
        return self._pred(arg)

    @as_predicate('({self}) and ({other})')
    def __and__(self, other):
        return lambda arg: self(arg) and other(arg)

    @as_predicate('({self}) or ({other})')
    def __or__(self, other):
        return lambda arg: self(arg) or other(arg)

    @as_predicate('({self}) xor ({other})')
    def __xor__(self, other):
        return lambda arg: self(arg) ^ other(arg)

    @as_predicate('not ({self})')
    def __invert__(self):
        return lambda arg: not self(arg)

    @staticmethod
    def all(*preds):
        return Predicate(lambda arg: all(p(arg) for p in preds), f'all [{_fmt(preds)}]')

    @staticmethod
    def any(*preds):
        return Predicate(lambda arg: any(p(arg) for p in preds), f'any [{_fmt(preds)}]')

    @staticmethod
    def none(*preds):
        return Predicate(lambda arg: not any(p(arg) for p in preds), f'any [{_fmt(preds)}]')

    def alias(self, name):
        return Predicate(self._pred, name)

    def __str__(self):
        return self.__name__

    __repr__ = __str__


always = Predicate(lambda _arg: True, 'always')
never = always.alias('never')


def of_type(*types):
    return Predicate(types)


@as_predicate('equal to {value}')
def eq(value):
    return lambda arg: arg == value


@as_predicate('not equal to {value}')
def ne(value):
    return lambda arg: arg != value


@as_predicate('less than {value}')
def lt(value):
    return lambda arg: arg < value


@as_predicate('less than or equal to {value}')
def le(value):
    return lambda arg: arg <= value


@as_predicate('greater than {value}')
def gt(value):
    return lambda arg: arg > value


@as_predicate('greater than or equal to {value}')
def ge(value):
    return lambda arg: arg >= value


equal = eq
not_equal = ne
less = lt
less_equal = le
greater = gt
greater_equal = ge

positive = greater(0).alias('positive')
negative = less(0).alias('negative')
non_negative = greater_equal(0).alias('non-negative')
non_positive = less_equal(0).alias('non-positive')
non_zero = not_equal(0).alias('non-zero')


@as_predicate('approx equal to {value}')
def approx_equal(value, rel_tol=None, abs_tol=None):
    kwargs = {}
    if abs_tol is not None:
        kwargs['abs_tol'] = abs_tol
    if rel_tol is not None:
        kwargs['rel_tol'] = rel_tol
    return lambda arg: isclose(arg, value, **kwargs)


@as_predicate('between {lo} and {up}')
def between(lo, up):
    return lambda arg: lo <= arg <= up


@as_predicate('divisible by {d}')
def divisible_by(d):
    return lambda arg: arg % d == 0


even = Predicate(divisible_by(2), 'even')
odd = (~even).alias('odd')


def any_of(*args):
    return Predicate(lambda arg: arg in args, f'any of {_fmt(args)}')


none = Predicate(lambda arg: arg is None, 'none')
not_none = (~none).alias('not none')


def match(get, pred):
    get = getter(get)
    pred = Predicate(pred)
    return Predicate(pred=lambda arg: pred(get(arg)), name=f'{get.__name__}:{pred}')


def matches(dct):
    return Predicate.all(*(match(get, pred) for get, pred in dct.items()))


def has_len(pred):
    return match(len, pred)


empty = Predicate(has_len(equal(0)), 'empty')
not_empty = (~empty).alias('not empty')

true = Predicate(bool, 'true')
false = (~true).alias('false')

numeric = of_type(int, float, Decimal).alias('numeric')


@as_predicate('has prefix {prefix}')
def has_prefix(prefix):
    return lambda arg: arg[:len(prefix)] == prefix


@as_predicate('has suffix {suffix}')
def has_suffix(suffix):
    return lambda arg: arg[-len(suffix):] == suffix


@as_predicate('has sub {sub}')
def has_sub(sub):
    return lambda arg: any(arg[i:i + len(sub)] == sub for i in range(len(arg)))


def matches_re(pattern):
    r = re.compile(pattern)
    return Predicate(lambda arg: r.match(arg), f'matches regex {pattern}')


@as_predicate('contains {value}')
def contains(value):
    return lambda arg: value in arg


@as_predicate('inside {value}')
def inside(value):
    return lambda arg: arg in value


def contains_all_of(*values):
    return Predicate.all(*(contains(v) for v in values)).alias(f'contains all of {_fmt(values)}')


def contains_any_of(*values):
    return Predicate.any(*(contains(v) for v in values)).alias(f'contains any of {_fmt(values)}')


def contains_none_of(*values):
    return Predicate.none(*(contains(v) for v in values)).alias(f'contains none of {_fmt(values)}')


class Iterable(Predicate):
    def __init__(self):
        super().__init__(lambda arg: hasattr(arg, '__iter__'), 'iterable')

    def __getitem__(self, item):
        return Predicate(self, f'iterable[{item}]')


class Collection(Predicate):
    def __init__(self):
        super().__init__(lambda arg: hasattr(arg, '__iter__') and hasattr(arg, '__len__'), 'collection')

    def __getitem__(self, item):
        return Predicate(self, f'collection[{item}]')


iterable = Iterable()
