def ensure(cond, error, error_type=RuntimeError):
    if cond:
        return

    if callable(error):
        error = error()

    if isinstance(error, Exception):
        raise error
    elif isinstance(error, str):
        raise error_type(error)


def merge_dicts(*dicts):
    result = dict()
    for d in dicts:
        result.update(d)
    return result
