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

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List

from aesqlapius.args import prepare_args_as_dict
from aesqlapius.function_def import ReturnValueOuterFormat
from aesqlapius.hook import QueryHook
from aesqlapius.output import generate_row_processor
from aesqlapius.query import Query


class AbstractDriverDetail(ABC):
    @abstractmethod
    def yield_cursor(self, db: Any, **kwargs: Dict[str, Any]) -> Iterator[Any]:
        pass  # pragma: no cover


def generate_method_generic(query: Query, detail: AbstractDriverDetail, hook: QueryHook) -> Callable[..., Any]:
    func_def = query.func_def
    returns = func_def.returns

    get_cursor = contextmanager(detail.yield_cursor)

    if returns is None:
        def method_returning_none(db: Any, *args: Any, **kwargs: Any) -> None:
            with get_cursor(db) as cur:
                prepared_args = prepare_args_as_dict(func_def, args, kwargs)
                cur.execute(hook(query.text, prepared_args), prepared_args)

        return method_returning_none

    elif returns.outer_format == ReturnValueOuterFormat.ITERATOR:
        def method_returning_iterator(db: Any, *args: Any, **kwargs: Any) -> Iterator[Any]:
            assert(returns is not None)  # mypy bug
            with get_cursor(db) as cur:
                prepared_args = prepare_args_as_dict(func_def, args, kwargs)
                cur.execute(hook(query.text, prepared_args), prepared_args)
                names = [desc[0] for desc in cur.description]
                process_row = generate_row_processor(returns.inner_format, names)
                yield from map(process_row, cur)

        return method_returning_iterator

    elif returns.outer_format == ReturnValueOuterFormat.LIST:
        def method_returning_list(db: Any, *args: Any, **kwargs: Any) -> List[Any]:
            assert(returns is not None)  # mypy bug
            with get_cursor(db) as cur:
                prepared_args = prepare_args_as_dict(func_def, args, kwargs)
                cur.execute(hook(query.text, prepared_args), prepared_args)
                names = [desc[0] for desc in cur.description]
                process_row = generate_row_processor(returns.inner_format, names)
                return [process_row(row) for row in cur]

        return method_returning_list

    elif returns.outer_format == ReturnValueOuterFormat.SINGLE:
        def method_returning_single(db: Any, *args: Any, **kwargs: Any) -> Any:
            assert(returns is not None)  # mypy bug
            with get_cursor(db) as cur:
                prepared_args = prepare_args_as_dict(func_def, args, kwargs)
                cur.execute(hook(query.text, prepared_args), prepared_args)
                names = [desc[0] for desc in cur.description]
                process_row = generate_row_processor(returns.inner_format, names)
                return process_row(cur.fetchone())

        return method_returning_single

    elif returns.outer_format == ReturnValueOuterFormat.DICT:
        def method_returning_dict(db: Any, *args: Any, **kwargs: Any) -> Any:
            assert(returns is not None)  # mypy bug
            with get_cursor(db) as cur:
                prepared_args = prepare_args_as_dict(func_def, args, kwargs)
                cur.execute(hook(query.text, prepared_args), prepared_args)
                names = [desc[0] for desc in cur.description]

                if isinstance(returns.outer_dict_by, int):
                    keyidx = returns.outer_dict_by
                else:
                    try:
                        keyidx = names.index(returns.outer_dict_by)
                    except ValueError:
                        raise KeyError(f'key column {returns.outer_dict_by} not found')

                if keyidx >= len(names):
                    raise IndexError(f'key column index {keyidx} is out of range')

                if returns.remove_key_column:
                    trimmed_names = names[0:keyidx] + names[keyidx + 1:]
                    process_row = generate_row_processor(returns.inner_format, trimmed_names)
                    return {
                        row[keyidx]: process_row(row[0:keyidx] + row[keyidx + 1:])
                        for row in cur
                    }
                else:
                    process_row = generate_row_processor(returns.inner_format, names)
                    return {
                        row[keyidx]: process_row(row)
                        for row in cur
                    }

        return method_returning_dict

    else:
        raise NotImplementedError(f"unsupported outer return type format '{returns.outer_format}'")  # pragma: no cover
