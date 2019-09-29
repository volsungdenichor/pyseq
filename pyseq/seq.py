import collections
import functools
import itertools
import operator


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
        key_selector = operator.itemgetter(0)
        value_selector = operator.itemgetter(1)
    else:
        key_selector = key_selector if key_selector is not None else identity
        value_selector = value_selector if value_selector is not None else identity

    return key_selector, value_selector


class Seq:
    def __init__(self, iterable):
        self._iterable = iterable._iterable if isinstance(iterable, Seq) else iterable

    def __bool__(self):
        raise NotImplementedError()

    def __iter__(self):
        return iter(self._iterable)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return Seq(self.slice(item.start, item.stop, item.step))
        elif isinstance(item, int):
            return next(itertools.islice(self._iterable, item, None))

    def __repr__(self):
        return 'Seq({})'.format(self.collect().join(' '))

    def __str__(self):
        return 'Seq({})'.format(self.collect().join(' '))

    @staticmethod
    @as_seq
    def range(*args):
        return range(*args)

    @staticmethod
    @as_seq
    def zip(*iterables):
        return zip(*iterables)

    @staticmethod
    @as_seq
    def repeat(value, count):
        return itertools.repeat(value, count)

    @as_seq
    def map(self, func):
        return map(func, self._iterable)

    @as_seq
    def map_attr(self, *attrs):
        return self.map(operator.attrgetter(*attrs))

    @as_seq
    def map_item(self, *items):
        return self.map(operator.itemgetter(*items))

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
    def partition(self, pred):
        return self.take_if(pred), self.drop_if(pred)

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
    def take(self, count):
        return itertools.islice(self._iterable, None, count)

    @as_seq
    def drop(self, count):
        return itertools.islice(self._iterable, count, None)

    @as_seq
    def slice(self, *args):
        return itertools.islice(self._iterable, *args)

    @as_seq
    def tail(self, count):
        return iter(collections.deque(self._iterable, maxlen=count))

    @as_seq
    def enumerate(self, start=0):
        return enumerate(self._iterable, start=start)

    @as_seq
    def collect(self):
        self._iterable = list(self._iterable)
        return self

    @as_seq
    def reverse(self):
        return reversed(self._iterable)

    @as_seq
    def sort(self, key=None, reverse=False):
        return sorted(self._iterable, key=key, reverse=reverse)

    @as_seq
    def group_by(self, key=None):
        for k, v in itertools.groupby(self._iterable, key=key):
            yield k, Seq(v)

    @as_seq
    def sort_and_group_by(self, key=None):
        return self.sort(key).group_by(key)

    @as_seq
    def zip_with(self, other_iterable):
        return Seq.zip(self._iterable, other_iterable)

    @as_seq
    def prepend(self, other_iterable):
        return itertools.chain(other_iterable, self._iterable)

    @as_seq
    def append(self, other_iterable):
        return itertools.chain(self._iterable, other_iterable)

    @as_seq
    def chain(self, other_iterable):
        return self.append(other_iterable)

    @as_seq
    def chunk(self, chunk_size):
        it = iter(self._iterable)
        chunk = tuple(itertools.islice(it, chunk_size))
        while chunk:
            yield Seq(chunk)
            chunk = tuple(itertools.islice(it, chunk_size))

    @as_seq
    def flatten(self):
        return itertools.chain.from_iterable(self._iterable)

    @as_seq
    def flat_map(self, func):
        return self.map(func).flatten()

    def all(self, pred=None):
        pred = pred if pred is not None else bool
        return all(self.map(pred))

    def any(self, pred=None):
        pred = pred if pred is not None else bool
        return any(self.map(pred))

    def none(self, pred=None):
        pred = pred if pred is not None else bool
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

    def reduce(self, func, init=None):
        init = init if init is not None else 0
        return functools.reduce(func, self._iterable, init)

    def sum(self, init=None):
        return self.reduce(operator.add, init)

    def min(self, key=None):
        key = key if key is not None else identity
        return min(self._iterable, key=key)

    def max(self, key=None):
        key = key if key is not None else identity
        return max(self._iterable, key=key)

    def min_max(self, key=None):
        return self.min(key), self.max(key)

    def first_or(self, def_value):
        return next(iter(self._iterable), def_value)

    def first_or_none(self):
        return self.first_or(None)

    def first_or_eval(self, func):
        res = self.first_or_none()
        return res if res is not None else func()

    def first_or_throw(self, message):
        res = self.first_or_none()
        if res is None:
            if isinstance(message, Exception):
                raise message
            else:
                raise IndexError(str(message))
        return res

    def first(self):
        return self.first_or_throw('empty range')
