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

import inspect
from typing import Any, Callable, Dict, List, Tuple, Union

from aesqlapius.function_def import ReturnValueInnerFormat


def generate_row_processor(inner_format: Union[ReturnValueInnerFormat, str], field_names: List[str], stack_depth: int = 2) -> Callable[[Tuple[Any]], Any]:
    if isinstance(inner_format, str):
        def process_row_custom(row: Tuple[Any]) -> Dict[str, Any]:
            # get the frame of method caller; usually,
            # [0] is process_row
            # [1] is generated method
            # [2] is caller
            # but stack depth is customizable to simplify testing the function
            caller_frame = inspect.stack()[stack_depth].frame

            assert isinstance(inner_format, str)  # XXX: for mypy

            if inner_format in caller_frame.f_locals:
                custom_format = caller_frame.f_locals[inner_format]
            elif inner_format in caller_frame.f_globals:
                custom_format = caller_frame.f_globals[inner_format]
            else:
                raise NameError(f"name '{inner_format}' is not defined")

            return custom_format(**dict(zip(field_names, row)))

        return process_row_custom

    elif inner_format == ReturnValueInnerFormat.TUPLE:
        def process_row_tuple(row: Tuple[Any]) -> Tuple[Any]:
            return row

        return process_row_tuple

    elif inner_format == ReturnValueInnerFormat.DICT:
        def process_row_dict(row: Tuple[Any]) -> Dict[str, Any]:
            return dict(zip(field_names, row))

        return process_row_dict

    elif inner_format == ReturnValueInnerFormat.LIST:
        def process_row_list(row: Tuple[Any]) -> List[Any]:
            return list(row)

        return process_row_list

    elif inner_format == ReturnValueInnerFormat.SINGLE:
        def process_row_single(row: Tuple[Any]) -> Any:
            return row[0] if row else None

        return process_row_single

    else:
        raise NotImplementedError(f"unsupported inner return type format '{inner_format}'")  # pragma: no cover
