import functools
import itertools
import operator
from collections import deque

from pyseq.functions import identity, negate
from pyseq.opt import Opt


def as_seq(func):
    def wrapper(*args, **kwargs):
        return Seq(func(*args, **kwargs))

    return wrapper


def _adjust_selectors(key_selector, value_selector):
    if key_selector is None and value_selector is None:
        return operator.itemgetter(0), operator.itemgetter(1)
    else:
        return key_selector or identity, value_selector or identity


def _append(lst, item):
    lst.append(item)
    return lst


class Seq:
    def __init__(self, iterable):
        self._iterable = iterable._iterable if isinstance(iterable, Seq) else iterable

    def __iter__(self):
        return iter(self._iterable)

    def len(self):
        return sum(1 for item in self._iterable)

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
    def repeat(value, n=None):
        if n is not None:
            return itertools.repeat(value, n)
        else:
            return itertools.repeat(value)

    @staticmethod
    @as_seq
    def once(value):
        yield value

    @staticmethod
    @as_seq
    def empty():
        yield from ()

    @staticmethod
    @as_seq
    def as_iterable(obj, base_type=(str, bytes)):
        if obj is None:
            return Seq.empty()
        if isinstance(obj, Opt):
            return Seq.as_iterable(obj.get_or_none())
        if base_type is not None and isinstance(obj, base_type):
            return Seq.once(obj)
        try:
            return iter(obj)
        except TypeError:
            return Seq.once(obj)

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
    def replace_if(self, pred, new_value):
        return self.map(lambda item: new_value if pred(item) else item)

    @as_seq
    def replace(self, old_value, new_value):
        return self.replace_if(lambda item: item == old_value, new_value)

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
    def union(self, other_iterable):
        return self.to_set().union(other_iterable)

    @as_seq
    def intersection(self, other_iterable):
        return self.to_set().intersection(other_iterable)

    @as_seq
    def difference(self, other_iterable):
        return self.to_set().difference(other_iterable)

    @as_seq
    def exclude(self, other_iterable):
        if not isinstance(other_iterable, set):
            other_iterable = set(other_iterable)
        return self.drop_if(lambda item: item in other_iterable)

    @as_seq
    def zip_with(self, other_iterable):
        return Seq.zip(self._iterable, other_iterable)

    @as_seq
    def chain(self, other_iterable):
        return itertools.chain(self._iterable, other_iterable)

    extend = chain

    @as_seq
    def append(self, value):
        return self.extend((value,))

    @as_seq
    def flatten(self):
        return itertools.chain.from_iterable(self._iterable)

    @as_seq
    def flat_map(self, func):
        return self.map(func).flatten()

    @as_seq
    def filter_map(self, func):
        for item in self._iterable:
            res = func(item)
            assert isinstance(res, Opt)
            if res.is_some():
                yield res.get()

    def _split(self, handler):
        buf = []

        for item in self._iterable:
            res, buf = handler(item, buf)
            if res:
                yield res

        if buf:
            yield buf

    @as_seq
    def split_at(self, pred):
        return self._split(lambda item, buf: (buf, []) if pred(item) else ([], _append(buf, item)))

    @as_seq
    def split_after(self, pred):
        return self._split(lambda item, buf: (_append(buf, item), []) if pred(item) else ([], _append(buf, item)))

    @as_seq
    def split_before(self, pred):
        return self._split(lambda item, buf: (buf, [item]) if pred(item) else ([], _append(buf, item)))

    @as_seq
    def chunk(self, chunk_size):
        return self._split(lambda item, buf: (buf, [item]) if len(buf) == chunk_size else ([], _append(buf, item)))

    def tee(self, n=2):
        return tuple(Seq(it) for it in itertools.tee(self._iterable, n))

    def partition(self, pred):
        s1, s2 = self.tee()
        return s1.take_if(pred), s2.drop_if(pred)

    @as_seq
    def adjacent(self):
        s1, s2 = self.tee()
        return Seq.zip(s1, s2.drop(1))

    @as_seq
    def adjacent_difference(self, func=None):
        func = func or operator.sub
        return self.adjacent().map(lambda pair: func(pair[1], pair[0]))

    @as_seq
    def intersperse(self, delimiter):
        return Seq.zip(Seq.repeat(delimiter), self._iterable).flatten().drop(1)

    def all(self, pred=bool):
        return all(self.map(pred))

    def any(self, pred=bool):
        return any(self.map(pred))

    def none(self, pred=bool):
        return not self.any(pred)

    def contains(self, value):
        return self.any(lambda item: item == value)

    def for_each(self, func):
        for item in self._iterable:
            func(item)

    @as_seq
    def inspect(self, func):
        for item in self._iterable:
            func(item)
            yield item

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
        return {key_selector(item): value_selector(item) for item in self._iterable}

    def to_multidict(self, key_selector=None, value_selector=None):
        key_selector, value_selector = _adjust_selectors(key_selector, value_selector)
        res = {}
        for item in self._iterable:
            res.setdefault(key_selector(item), []).append(value_selector(item))
        return res

    def reduce(self, func, init):
        return functools.reduce(func, self._iterable, init)

    def sum(self, init=0.0):
        return self.reduce(operator.add, init)

    def min(self, key=identity):
        return Opt.eval(lambda: min(self._iterable, key=key))

    def max(self, key=identity):
        return Opt.eval(lambda: max(self._iterable, key=key))

    def first(self):
        return Opt.of(next(iter(self._iterable), None))

    def last(self):
        return Opt.eval(lambda: deque(self._iterable, maxlen=1)[0])

    def nth(self, index):
        return self.drop(index).first()

    def single(self):
        lst = self.take(2).to_list()
        return Opt.some(lst[0]) if len(lst) == 1 else Opt.none()

    def find(self, pred):
        return self.drop_until(pred).first()
