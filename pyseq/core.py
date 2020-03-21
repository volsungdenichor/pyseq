def ensure(cond, error):
    if cond:
        return

    if callable(error):
        error = error()

    if isinstance(error, Exception):
        raise error
    elif isinstance(error, str):
        raise RuntimeError(error)


def merge_dicts(*dicts):
    result = dict()
    for d in dicts:
        result.update(d)
    return result
