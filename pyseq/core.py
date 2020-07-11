def ensure(cond, error=None, error_type=RuntimeError):
    if cond:
        return

    if error is None:
        error = 'Condition not met'

    if callable(error):
        error = error()

    if isinstance(error, Exception):
        raise error
    elif isinstance(error, str):
        raise error_type(error)


def merge_dicts(*dicts):
    result = dict()
    for dct in dicts:
        if dct is not None:
            result.update(dct)
    return result


def dict_if(cond, dct):
    if not cond:
        return {}
    if callable(dct):
        dct = dct()
    return dct
