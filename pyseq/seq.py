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


def _create_func(*funcs):
    if not funcs:
        return identity
    if all(isinstance(item, str) for item in funcs):
        return operator.attrgetter(*funcs)
    elif all(isinstance(item, int) for item in funcs):
        return operator.itemgetter(*funcs)
    elif callable(funcs[0]):
        return funcs[0]


class Seq:
    def __init__(self, iterable):
        self._iterable = iterable._iterable if isinstance(iterable, Seq) else iterable

    def __iter__(self):
        return iter(self._iterable)

    def __len__(self):
        return len(self._iterable)

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
    def map(self, *funcs):
        return map(_create_func(*funcs), self._iterable)

    @as_seq
    def replace_if(self, pred, new_value):
        return self.map(lambda item: new_value if pred(item) else item)

    @as_seq
    def replace(self, old_value, new_value):
        return self.replace_if(lambda item: item == old_value, new_value)

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
    def tee(self, count):
        return Seq(itertools.tee(self._iterable, count)).map(Seq)

    @as_seq
    def partition(self, pred):
        t, d = self.tee(2)
        return t.take_if(pred), d.drop_if(pred)

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
    def sort(self, *funcs):
        return sorted(self._iterable, key=_create_func(*funcs))

    @as_seq
    def sort_desc(self, *funcs):
        return sorted(self._iterable, key=_create_func(*funcs), reverse=True)

    @as_seq
    def group_by(self, *funcs):
        for k, v in itertools.groupby(self._iterable, key=_create_func(*funcs)):
            yield k, Seq(v)

    @as_seq
    def group_by_sorted(self, *funcs):
        f = _create_func(*funcs)
        return self.sort(f).group_by(f)

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
    def flat_map(self, *funcs):
        return self.map(*funcs).flatten()

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

    def reduce(self, func, init=None):
        return functools.reduce(func, self._iterable, init if init is not None else 0)

    def sum(self, init=None):
        return self.reduce(operator.add, init)

    def min(self, *funcs):
        return min(self._iterable, key=_create_func(*funcs))

    def max(self, *funcs):
        return max(self._iterable, key=_create_func(*funcs))

    def first_or(self, def_value):
        return next(iter(self._iterable), def_value)

    def first_or_none(self):
        return self.first_or(None)

    def first_or_eval(self, func):
        def_value = object()
        res = self.first_or(def_value)
        return res if res is not def_value else func()

    def first_or_throw(self, message):
        def handler():
            if isinstance(message, Exception):
                raise message
            else:
                raise IndexError(str(message))

        return self.first_or_eval(handler)

    def first(self):
        return self.first_or_throw('empty sequence')
