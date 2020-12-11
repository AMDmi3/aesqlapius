import functools
import inspect
from typing import Any

import aesqlapius


def _wrap_func_as_async(func):
    async def wrapper(*args, **kwargs):
        print('wrapped func', func)
        return func(*args, **kwargs)
    return wrapper


def _wrap_gen_as_async(func):
    async def wrapper(*args, **kwargs):
        print('wrapped gen', func)
        for val in func(*args, **kwargs):
            yield val
    return wrapper


def convert_api_to_async(ns: Any) -> None:
    for name in dir(ns):
        member = getattr(ns, name)

        if isinstance(member, aesqlapius.Namespace):
            convert_api_to_async(member)

        # XXX: according to python docs, inspect.iscoroutinefunction
        # should work on partial but it doesn't, so we resolve original
        # function out of it
        origfunc = member
        while isinstance(origfunc, functools.partial):
            origfunc = origfunc.func

        if getattr(member, 'aesqlapius_method', False):
            if inspect.iscoroutinefunction(origfunc) or inspect.isasyncgenfunction(origfunc):
                pass  # already async
            elif inspect.isgeneratorfunction(origfunc):
                setattr(ns, name, _wrap_gen_as_async(member))
            else:
                setattr(ns, name, _wrap_func_as_async(member))
