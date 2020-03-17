def ensure(cond, error):
    if cond:
        return

    if callable(error):
        error = error()

    if isinstance(error, Exception):
        raise error
    elif isinstance(error, str):
        raise RuntimeError(error)
