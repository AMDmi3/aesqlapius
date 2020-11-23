import functools
from typing import Any, Callable, Iterator, List

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


def generate_api(db: Any, path: str, file_as_namespace=False) -> Namespace:
    ns = Namespace()

    for entry, queries in iter_query_dir(path, '.sql'):
        for query in queries:
            namespace_path = entry.namespace_path if file_as_namespace else entry.namespace_path[:-1]
            inject_method(
                ns,
                namespace_path + [query.func_def.name],
                functools.partial(_generate_method(query), db)
            )

    return ns
