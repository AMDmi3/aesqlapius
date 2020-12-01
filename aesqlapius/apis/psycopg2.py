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
from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
    overload
)

from aesqlapius.args import prepare_args_as_dict
from aesqlapius.function_def import ReturnValueOuterFormat
from aesqlapius.namespace import Namespace, inject_method
from aesqlapius.output import generate_row_processor
from aesqlapius.query import Query
from aesqlapius.querydir import iter_query_dir


def _generate_method(query: Query) -> Callable[..., Any]:
    func_def = query.func_def
    returns = func_def.returns

    if returns is None:
        def method_returning_none(db, *args, **kwargs) -> None:
            with db.cursor() as cur:
                cur.execute(query.text, prepare_args_as_dict(func_def, args, kwargs))

        return method_returning_none

    elif returns.outer_format == ReturnValueOuterFormat.ITERATOR:
        def method_returning_iterator(db, *args, **kwargs) -> Iterator[Any]:
            assert(returns is not None)  # mypy bug
            with db.cursor() as cur:
                cur.execute(query.text, prepare_args_as_dict(func_def, args, kwargs))
                names = [desc.name for desc in cur.description]
                process_row = generate_row_processor(returns.inner_format, names)
                yield from map(process_row, cur)

        return method_returning_iterator

    elif returns.outer_format == ReturnValueOuterFormat.LIST:
        def method_returning_list(db, *args, **kwargs) -> List[Any]:
            assert(returns is not None)  # mypy bug
            with db.cursor() as cur:
                cur.execute(query.text, prepare_args_as_dict(func_def, args, kwargs))
                names = [desc.name for desc in cur.description]
                process_row = generate_row_processor(returns.inner_format, names)
                return [process_row(row) for row in cur]

        return method_returning_list

    elif returns.outer_format == ReturnValueOuterFormat.SINGLE:
        def method_returning_single(db, *args, **kwargs) -> Any:
            assert(returns is not None)  # mypy bug
            with db.cursor() as cur:
                cur.execute(query.text, prepare_args_as_dict(func_def, args, kwargs))
                names = [desc.name for desc in cur.description]
                process_row = generate_row_processor(returns.inner_format, names)
                return process_row(cur.fetchone())

        return method_returning_single

    else:
        raise NotImplementedError(f"unsupported outer return type format '{returns.outer_format}'")  # pragma: no cover


def _maybe_bind(query: Query, db: Any) -> Callable[..., Any]:
    if db is None:
        return _generate_method(query)
    else:
        return functools.partial(_generate_method(query), db)


T = TypeVar('T')


@overload
def generate_api(
    path: str,
    db: Any = None,
    *,
    file_as_namespace: bool = False,
    extension: str = '.sql',
    namespace_root: str = '__init__',
) -> Namespace:
    ...  # pragma: no cover


@overload
def generate_api(
    path: str,
    db: Any = None,
    *,
    target: T,
    file_as_namespace: bool = False,
    extension: str = '.sql',
    namespace_root: str = '__init__',
) -> T:
    ...  # pragma: no cover


def generate_api(
    path: str,
    db: Any = None,
    *,
    target: Optional[T] = None,
    file_as_namespace: bool = False,
    extension: str = '.sql',
    namespace_root: str = '__init__',
) -> Union[T, Namespace]:
    ns: Union[T, Namespace]
    if target is None:
        ns = Namespace()
    else:
        ns = target

    for entry, queries in iter_query_dir(path, extension):
        if file_as_namespace and entry.namespace_path[-1] != namespace_root:
            namespace_path = entry.namespace_path
        else:
            namespace_path = entry.namespace_path[:-1]

        for query in queries:
            inject_method(
                ns,
                namespace_path + [query.func_def.name],
                _maybe_bind(query, db)
            )

    return ns
