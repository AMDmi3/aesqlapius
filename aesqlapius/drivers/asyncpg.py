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

from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, AsyncIterator, Callable, Dict, List, Tuple, Union

import asyncpg

from aesqlapius.args import prepare_args_as_dict, prepare_args_as_list
from aesqlapius.function_def import (
    ReturnValueInnerFormat,
    ReturnValueOuterFormat
)
from aesqlapius.hook import QueryHook
from aesqlapius.query import Query


def _generate_row_processor(inner_format: Union[ReturnValueInnerFormat, str]) -> Callable[[Tuple[Any]], Any]:
    if inner_format == ReturnValueInnerFormat.TUPLE:
        def process_row_tuple(row: asyncpg.Record) -> Tuple[Any, ...]:
            return tuple(row)
        return process_row_tuple
    elif inner_format == ReturnValueInnerFormat.DICT:
        def process_row_dict(row: asyncpg.Record) -> Dict[str, Any]:
            return dict(row)
        return process_row_dict
    elif inner_format == ReturnValueInnerFormat.VALUE:
        def process_row_single(row: asyncpg.Record) -> Any:
            return row[0] if len(row) > 0 else None
        return process_row_single
    else:
        raise NotImplementedError(f"unsupported inner return type format '{inner_format}'")  # pragma: no cover


def _generate_row_processor_removing_index(inner_format: Union[ReturnValueInnerFormat, str], remove: int) -> Callable[[Tuple[Any]], Any]:
    if inner_format == ReturnValueInnerFormat.TUPLE:
        def process_row_tuple(row: asyncpg.Record) -> Tuple[Any, ...]:
            return tuple(row[0:remove]) + tuple(row[remove + 1:])
        return process_row_tuple
    elif inner_format == ReturnValueInnerFormat.DICT:
        def process_row_dict(row: asyncpg.Record) -> Dict[str, Any]:
            d = dict(row)
            del d[list(row.keys())[remove]]
            return d
        return process_row_dict
    elif inner_format == ReturnValueInnerFormat.VALUE:
        def process_row_single(row: asyncpg.Record) -> Any:
            return row[0 if remove > 0 else 1] if len(row) > 1 else None
        return process_row_single
    else:
        raise NotImplementedError(f"unsupported inner return type format '{inner_format}'")  # pragma: no cover


def _generate_row_processor_removing_name(inner_format: Union[ReturnValueInnerFormat, str], remove: str) -> Callable[[Tuple[Any]], Any]:
    if inner_format == ReturnValueInnerFormat.TUPLE:
        def process_row_tuple(row: asyncpg.Record) -> Tuple[Any, ...]:
            d = dict(row)
            del d[remove]
            return tuple(d.values())
        return process_row_tuple
    elif inner_format == ReturnValueInnerFormat.DICT:
        def process_row_dict(row: asyncpg.Record) -> Dict[str, Any]:
            d = dict(row)
            del d[remove]
            return d
        return process_row_dict
    elif inner_format == ReturnValueInnerFormat.VALUE:
        def process_row_single(row: asyncpg.Record) -> Any:
            return row[0 if next(iter(row.keys())) != remove else 1] if len(row) > 1 else None
        return process_row_single
    else:
        raise NotImplementedError(f"unsupported inner return type format '{inner_format}'")  # pragma: no cover


@asynccontextmanager
async def _get_connection(conn: Union[asyncpg.Connection, asyncpg.pool.Pool], force_transaction: bool = False) -> asyncpg.Connection:
    async with AsyncExitStack() as stack:
        if isinstance(conn, asyncpg.pool.Pool):
            conn = await stack.enter_async_context(conn.acquire())

        if force_transaction and not conn.is_in_transaction():
            await stack.enter_async_context(conn.transaction())

        yield conn


def generate_method(query: Query, hook: QueryHook) -> Callable[..., Any]:
    func_def = query.func_def
    returns = func_def.returns

    if returns is None:
        async def method_returning_none(db: Any, *args: Any, **kwargs: Any) -> None:
            prepared_args = prepare_args_as_dict(func_def, args, kwargs)
            prepared_args_list = prepare_args_as_list(func_def, args, kwargs)

            async with _get_connection(db) as conn:
                await conn.execute(hook(query.text, prepared_args), *prepared_args_list)

        return method_returning_none

    elif returns.outer_format == ReturnValueOuterFormat.ITERATOR:
        async def method_returning_iterator(db: Any, *args: Any, **kwargs: Any) -> AsyncIterator[Any]:
            assert(returns is not None)  # mypy bug
            prepared_args = prepare_args_as_dict(func_def, args, kwargs)
            prepared_args_list = prepare_args_as_list(func_def, args, kwargs)
            process_row = _generate_row_processor(returns.inner_format)

            async with _get_connection(db, True) as conn:
                async for row in conn.cursor(hook(query.text, prepared_args), *prepared_args_list):
                    yield process_row(row)

        return method_returning_iterator

    elif returns.outer_format == ReturnValueOuterFormat.LIST:
        async def method_returning_list(db: Any, *args: Any, **kwargs: Any) -> List[Any]:
            assert(returns is not None)  # mypy bug
            prepared_args = prepare_args_as_dict(func_def, args, kwargs)
            prepared_args_list = prepare_args_as_list(func_def, args, kwargs)
            process_row = _generate_row_processor(returns.inner_format)
            async with _get_connection(db) as conn:
                return [
                    process_row(row)
                    for row in await conn.fetch(hook(query.text, prepared_args), *prepared_args_list)
                ]

        return method_returning_list

    elif returns.outer_format == ReturnValueOuterFormat.SINGLE:
        async def method_returning_single(db: Any, *args: Any, **kwargs: Any) -> Any:
            assert(returns is not None)  # mypy bug
            prepared_args = prepare_args_as_dict(func_def, args, kwargs)
            prepared_args_list = prepare_args_as_list(func_def, args, kwargs)
            process_row = _generate_row_processor(returns.inner_format)

            async with _get_connection(db) as conn:
                return process_row(await conn.fetchrow(hook(query.text, prepared_args), *prepared_args_list))

        return method_returning_single

    elif returns.outer_format == ReturnValueOuterFormat.DICT:
        async def method_returning_dict(db: Any, *args: Any, **kwargs: Any) -> Any:
            assert(returns is not None)  # mypy bug
            assert(returns.outer_dict_by is not None)
            prepared_args = prepare_args_as_dict(func_def, args, kwargs)
            prepared_args_list = prepare_args_as_list(func_def, args, kwargs)

            if not returns.remove_key_column:
                process_row = _generate_row_processor(returns.inner_format)
            elif isinstance(returns.outer_dict_by, int):
                process_row = _generate_row_processor_removing_index(returns.inner_format, returns.outer_dict_by)
            else:
                process_row = _generate_row_processor_removing_name(returns.inner_format, returns.outer_dict_by)

            async with _get_connection(db) as conn:
                return {
                    row[returns.outer_dict_by]: process_row(row)
                    for row in await conn.fetch(hook(query.text, prepared_args), *prepared_args_list)
                }

        return method_returning_dict

    else:
        raise NotImplementedError(f"unsupported outer return type format '{returns.outer_format}'")  # pragma: no cover
