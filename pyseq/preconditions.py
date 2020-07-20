import functools
import inspect

from pyseq.core import ensure


def _extract_predicates(annotation):
    if annotation is inspect.Parameter.empty:
        return ()
    elif isinstance(annotation, list):
        return tuple(annotation)
    else:
        return annotation,


class PreconditionError(RuntimeError):
    pass


class PostconditionError(RuntimeError):
    pass


class _Var:
    def __init__(self, value, name=None, exception_type=RuntimeError, stack_level=2):
        self.value = value
        self.name = name or '<unknown>'
        self.exception_type = exception_type
        self.stack_level = stack_level

    def _expected(self, pred):
        if isinstance(pred, type):
            return pred.__name__
        elif isinstance(pred, tuple):
            return ','.join(map(self._expected, pred))
        else:
            return str(pred)

    def _actual(self):
        return f'{self.value} <{type(self.value).__name__}>'

    def is_type(self, v):
        return isinstance(v, type) or (isinstance(v, tuple) and all(map(self.is_type, v)))

    def _test_predicate(self, pred):
        if self.is_type(pred):
            return isinstance(self.value, pred)
        else:
            return pred(self.value)

    def _format_error(self, pred):
        name = self.name() if callable(self.name) else self.name
        return f'{name}: expected = {self._expected(pred)}; actual = {self._actual()}'

    def ensure(self, *predicates):
        for pred in predicates:
            ensure(self._test_predicate(pred),
                   lambda: self._format_error(pred),
                   self.exception_type,
                   stack_level=self.stack_level)

        return self.value


class _Wrapper:
    def __init__(self, func, preconditions=None, postconditions=None):
        self._preconditions = preconditions or {}
        self._postconditions = postconditions or []

        if isinstance(func, _Wrapper):
            self._func = func._func
            self._signature = func._signature
            for name, predicates in func._preconditions.items():
                self._add_precondition(name, predicates)
            self._add_postcondition(func._postconditions)
        else:
            self._func = func
            self._signature = inspect.signature(self._func)
            for param in self._signature.parameters.values():
                self._add_precondition(param.name, _extract_predicates(param.annotation))
            self._add_postcondition(_extract_predicates(self._signature.return_annotation))

        functools.update_wrapper(self, self._func)

    def _add_precondition(self, name, predicates):
        if predicates:
            self._preconditions.setdefault(name, []).extend(predicates)

    def _add_postcondition(self, predicates):
        self._postconditions.extend(predicates)

    def format_func(self):
        return f'{self._func.__name__}'

    def bind_params(self, *args, **kwargs):
        bounds_args = self._signature.bind(*args, **kwargs)
        return dict(bounds_args.arguments)

    def __call__(self, *args, **kwargs):
        bound_params = self.bind_params(*args, **kwargs)

        for name, predicates in self._preconditions.items():
            if name in bound_params:  # if missing, default argument value was used and should not be checked
                var(bound_params[name],
                    lambda: f'{self.format_func()}: argument "{name}"',
                    exception_type=PreconditionError,
                    stack_level=3).ensure(*predicates)

        return_value = self._func(*args, **kwargs)

        var(return_value,
            lambda: f'{self.format_func()}: return_value',
            exception_type=PostconditionError,
            stack_level=3).ensure(*self._postconditions)

        return return_value


def precondition(arg_name, *predicates):
    def decorator(func):
        return _Wrapper(func, preconditions={arg_name: list(predicates)})

    return decorator


def postcondition(*predicates):
    def decorator(func):
        return _Wrapper(func, postconditions=list(predicates))

    return decorator


var = _Var
value_of = var
pre = precondition
post = postcondition
check_annotation = _Wrapper
