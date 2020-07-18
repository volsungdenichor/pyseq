import inspect


def _format_frame_info(frame, stack_level=0):
    for _ in range(stack_level):
        frame = frame.f_back
    file_name, line_number, function_name, *_ = inspect.getframeinfo(frame)
    return f'File "{file_name}", line {line_number}, in {function_name}'


def ensure(cond, error=None, error_type=RuntimeError, stack_level=1):
    if cond:
        return

    if error is None:
        error = 'Condition not met'

    if callable(error):
        error = error()

    loc = _format_frame_info(inspect.currentframe(), stack_level=stack_level)

    if isinstance(error, Exception):
        exception = error
    else:
        exception = error_type(error)

    exception.args += (loc,)
    raise exception


def merge_dicts(*dicts):
    result = dict()
    for dct in dicts:
        if dct is not None:
            result.update(dct)
    return result
