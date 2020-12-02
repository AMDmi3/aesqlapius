# Copyright (c) 2020 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import functools
import importlib
from typing import (
    Any,
    Literal,
    Optional,
    TypeVar,
    Union,
    overload
)

from aesqlapius.namespace import Namespace, inject_method
from aesqlapius.querydir import iter_queries


__version__ = '0.0.4'


T = TypeVar('T')
NAMESPACE_MODE = Literal['dirs', 'files', 'flat']


@overload
def generate_api(
    path: str,
    driver: str,
    db: Any = None,
    *,
    extension: str = '.sql',
    namespace_mode: NAMESPACE_MODE = 'dirs',
    namespace_root: str = '__init__',
) -> Namespace:
    ...  # pragma: no cover


@overload
def generate_api(
    path: str,
    driver: str,
    db: Any = None,
    *,
    target: T,
    extension: str = '.sql',
    namespace_mode: NAMESPACE_MODE = 'dirs',
    namespace_root: str = '__init__',
) -> T:
    ...  # pragma: no cover


def generate_api(
    path: str,
    driver: str,
    db: Any = None,
    *,
    target: Optional[T] = None,
    extension: str = '.sql',
    namespace_mode: NAMESPACE_MODE = 'dirs',
    namespace_root: str = '__init__',
) -> Union[T, Namespace]:
    ns: Union[T, Namespace]
    if target is None:
        ns = Namespace()
    else:
        ns = target

    driver_module = importlib.import_module(f'aesqlapius.drivers.{driver}')

    for entry, queries in iter_queries(path, extension):
        if namespace_mode == 'flat':
            namespace_path = []
        elif namespace_mode == 'files' and entry.namespace_path[-1] != namespace_root:
            namespace_path = entry.namespace_path
        else:
            namespace_path = entry.namespace_path[:-1]

        for query in queries:
            method_func = driver_module.generate_method(query)  # type: ignore

            if db is not None:
                method_func = functools.partial(method_func, db)

            inject_method(
                ns,
                namespace_path + [query.func_def.name],
                method_func
            )

    return ns
