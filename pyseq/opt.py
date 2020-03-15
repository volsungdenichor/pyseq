class OptError(Exception):
    pass


class Opt:
    def __init__(self, value=None):
        self._value = value

    def __str__(self):
        return str(self._value) if self else '{none}'

    __repr__ = __str__

    @staticmethod
    def of(value):
        if value is None:
            raise OptError()

        return Opt(value)

    @staticmethod
    def of_nullable(value):
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

    def value(self):
        return self.value_or_raise('empty optional')

    def has_value(self):
        return self._value is not None

    def __bool__(self):
        return self.has_value()

    def map(self, func):
        if self:
            return Opt(func(self._value))
        else:
            return Opt.none()

    def filter(self, pred):
        if self and pred(self._value):
            return self
        else:
            return Opt.none()

    def flat_map(self, func):
        if self:
            res = func(self._value)
            assert isinstance(res, Opt)
            return Opt(res._value)
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
