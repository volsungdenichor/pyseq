from pyseq.core import ensure
from pyseq.functions import negate


class OptError(Exception):
    pass


class Opt:
    def __init__(self, value=None):
        self._value = value._value if isinstance(value, Opt) else value

    def __str__(self):
        return f'some({self._value})' if self else 'none'

    __repr__ = __str__

    @staticmethod
    def of(value):
        return Opt(value)

    @staticmethod
    def some(value):
        ensure(value is not None, lambda: OptError('value expected, got None'))
        return Opt(value)

    @staticmethod
    def eval(func, exceptions=None):
        if exceptions is None:
            exceptions = Exception

        try:
            return Opt.of(func())
        except exceptions:
            return Opt.none()

    @staticmethod
    def none():
        return Opt(None)

    def or_else(self, func):
        if self:
            return self
        else:
            res = func()
            ensure(isinstance(res, Opt), lambda: 'or_else: result Opt expected')
            return res

    def get_or(self, default_value):
        return self._value if self else default_value

    def get_or_else(self, func):
        return self._value if self else func()

    def get_or_raise(self, exception):
        ensure(self, exception, error_type=OptError)
        return self._value

    def get_or_none(self):
        return self.get_or(None)

    def get(self):
        return self.get_or_raise('empty optional')

    def is_some(self):
        return self._value is not None

    def is_none(self):
        return not self.is_some()

    def __bool__(self):
        return self.is_some()

    def map(self, func):
        if self:
            res = func(self._value)
            ensure(not isinstance(res, Opt), lambda: 'map: result Opt not expected')
            return Opt(res)
        else:
            return Opt.none()

    def flat_map(self, func):
        if self:
            res = func(self._value)
            ensure(isinstance(res, Opt), lambda: 'flat_map result Opt expected')
            return res
        else:
            return Opt.none()

    def getattr(self, *names):
        res = self
        for name in names:
            res = res.flat_map(lambda v: Opt.eval(lambda: getattr(v, name)))
        return res

    def getitem(self, *names):
        res = self
        for name in names:
            res = res.flat_map(lambda v: Opt.eval(lambda: v[name]))
        return res

    def matches(self, pred):
        return self and pred(self._value)

    def contains(self, value):
        return self.matches(lambda v: v == value)

    def filter(self, pred):
        if self.matches(pred):
            return self
        else:
            return Opt.none()

    def take_if(self, pred):
        return self.filter(pred)

    def drop_if(self, pred):
        return self.filter(negate(pred))

    def or_(self, other):
        ensure(isinstance(other, Opt), lambda: 'Opt expected')
        return self if self else other

    def and_(self, other):
        ensure(isinstance(other, Opt), lambda: 'Opt expected')
        return self if not self else other

    def __or__(self, other):
        return self.or_(other)

    def __and__(self, other):
        return self.and_(other)

    def __eq__(self, other):
        if isinstance(other, Opt):
            return self._value == other._value
        else:
            return self._value == other
