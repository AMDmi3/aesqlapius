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

from typing import Any, Callable, Dict, List, Tuple, Union

from aesqlapius.function_def import ReturnValueInnerFormat


def generate_row_processor(inner_format: Union[ReturnValueInnerFormat, str], field_names: List[str], stack_depth: int = 2) -> Callable[[Tuple[Any, ...]], Any]:
    if inner_format == ReturnValueInnerFormat.TUPLE:
        def process_row_tuple(row: Tuple[Any, ...]) -> Tuple[Any, ...]:
            return row

        return process_row_tuple

    elif inner_format == ReturnValueInnerFormat.DICT:
        def process_row_dict(row: Tuple[Any, ...]) -> Dict[str, Any]:
            return dict(zip(field_names, row))

        return process_row_dict

    elif inner_format == ReturnValueInnerFormat.VALUE:
        def process_row_single(row: Tuple[Any, ...]) -> Any:
            return row[0] if row else None

        return process_row_single

    else:
        raise NotImplementedError(f"unsupported inner return type format '{inner_format}'")  # pragma: no cover
