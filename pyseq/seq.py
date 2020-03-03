import functools
import itertools
import operator

from pyseq.opt import Opt


def as_seq(func):
    def wrapper(*args, **kwargs):
        return Seq(func(*args, **kwargs))

    return wrapper


def identity(x):
    return x


def negate(func):
    def result(*args, **kwargs):
        return not func(*args, **kwargs)

    return result


def _adjust_selectors(key_selector, value_selector):
    if key_selector is None and value_selector is None:
        return operator.itemgetter(0), operator.itemgetter(1)
    elif value_selector is None:
        return key_selector, identity
    else:
        return key_selector, value_selector


class Seq:
    def __init__(self, iterable):
        self._iterable = iterable._iterable if isinstance(iterable, Seq) else iterable

    def __iter__(self):
        return iter(self._iterable)

    @staticmethod
    @as_seq
    def range(*args):
        return range(*args)

    @staticmethod
    @as_seq
    def count(start=0, step=1):
        return itertools.count(start, step)

    @staticmethod
    @as_seq
    def zip(*iterables):
        return zip(*iterables)

    @staticmethod
    @as_seq
    def repeat(value, count):
        return itertools.repeat(value, count)

    @staticmethod
    @as_seq
    def once(value):
        if value is not None:
            yield value

    @as_seq
    def map(self, func):
        return map(func, self._iterable)

    @as_seq
    def filter(self, pred):
        return filter(pred, self._iterable)

    @as_seq
    def take_if(self, pred):
        return self.filter(pred)

    @as_seq
    def drop_if(self, pred):
        return self.filter(negate(pred))

    @as_seq
    def take_while(self, pred):
        return itertools.takewhile(pred, self._iterable)

    @as_seq
    def drop_while(self, pred):
        return itertools.dropwhile(pred, self._iterable)

    @as_seq
    def take_until(self, pred):
        return self.take_while(negate(pred))

    @as_seq
    def drop_until(self, pred):
        return self.drop_while(negate(pred))

    @as_seq
    def take(self, n):
        return itertools.islice(self._iterable, None, n)

    @as_seq
    def drop(self, n):
        return itertools.islice(self._iterable, n, None)

    @as_seq
    def slice(self, *args):
        return itertools.islice(self._iterable, *args)

    @as_seq
    def enumerate(self, start=0):
        return enumerate(self._iterable, start=start)

    @as_seq
    def collect(self):
        return list(self._iterable)

    @as_seq
    def reverse(self):
        return reversed(self._iterable)

    @as_seq
    def sort(self, key=None):
        return sorted(self._iterable, key=key)

    @as_seq
    def sort_desc(self, key=None):
        return sorted(self._iterable, key=key, reverse=True)

    @as_seq
    def unique(self):
        visited = set()
        for item in self._iterable:
            if item not in visited:
                visited.add(item)
                yield item


    @as_seq
    def zip_with(self, other_iterable):
        return Seq.zip(self._iterable, other_iterable)

    @as_seq
    def chain(self, other_iterable):
        return itertools.chain(self._iterable, other_iterable)

    @as_seq
    def flatten(self):
        return itertools.chain.from_iterable(self._iterable)

    @as_seq
    def flat_map(self, func):
        return self.map(func).flatten()

    def all(self, pred=None):
        return all(self.map(pred if pred is not None else bool))

    def any(self, pred=None):
        return any(self.map(pred if pred is not None else bool))

    def none(self, pred=None):
        return not self.any(pred)

    def for_each(self, func):
        for item in self._iterable:
            func(item)

    def join(self, separator=''):
        return separator.join(self.map(str))

    def to(self, container):
        return container(self._iterable)

    def to_list(self):
        return self.to(list)

    def to_set(self):
        return self.to(set)

    def to_tuple(self):
        return self.to(tuple)

    def to_str(self):
        return self.join()

    def to_dict(self, key_selector=None, value_selector=None):
        key_selector, value_selector = _adjust_selectors(key_selector, value_selector)
        res = {}
        for item in self._iterable:
            res[key_selector(item)] = value_selector(item)
        return res

    def to_multidict(self, key_selector=None, value_selector=None):
        key_selector, value_selector = _adjust_selectors(key_selector, value_selector)
        res = {}
        for item in self._iterable:
            res.setdefault(key_selector(item), []).append(value_selector(item))
        return res

    def reduce(self, func, init):
        return functools.reduce(func, self._iterable, init)

    def sum(self, init=None):
        return self.reduce(operator.add, init if init is not None else 0)

    def first(self):
        return Opt.of_nullable(next(iter(self._iterable), None))

    def nth(self, index):
        return self.drop(index).first()
