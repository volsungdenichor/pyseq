from pyseq.core import ensure


class OptError(Exception):
    pass


class Opt:
    def __init__(self, value=None):
        self._value = value

    def __str__(self):
        return f'some({self._value})' if self else 'none'

    __repr__ = __str__

    @staticmethod
    def of(value):
        ensure(value is not None, lambda: OptError())
        return Opt(value)

    @staticmethod
    def of_nullable(value):
        if isinstance(value, Opt):
            return Opt(value._value)
        return Opt(value)

    @staticmethod
    def eval(func):
        try:
            return Opt.of_nullable(func())
        except:
            return Opt.none()

    some = of

    @staticmethod
    def none():
        return Opt(None)

    def value_or(self, default_value):
        return self._value if self else default_value

    def value_or_eval(self, func):
        return self._value if self else func()

    def value_or_raise(self, exception):
        if self:
            return self._value
        else:
            if isinstance(exception, str):
                raise OptError(exception)
            else:
                raise exception

    def value_or_none(self):
        return self.value_or(None)

    def value(self):
        return self.value_or_raise('empty optional')

    def has_value(self):
        return self._value is not None

    def __bool__(self):
        return self.has_value()

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
            res = res.flat_map(lambda v: Opt.of_nullable(getattr(v, name, None)))
        return res

    def getitem(self, *names):
        res = self
        for name in names:
            res = res.flat_map(lambda v: Opt.of_nullable(v.get(name, None)))
        return res

    def contains(self, value):
        return self and self._value == value

    def exists(self, pred):
        return self and pred(self._value)

    def filter(self, pred):
        if self.exists(pred):
            return self
        else:
            return Opt.none()

    def __or__(self, other):
        return self if self.has_value() else other

    def __and__(self, other):
        return self if not self.has_value() else other

    def __eq__(self, other):
        if isinstance(other, Opt):
            return self._value == other._value
        else:
            return self._value == other
