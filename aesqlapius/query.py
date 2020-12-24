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

import re
from dataclasses import dataclass
from typing import IO, Iterator, List, Optional, Tuple

from aesqlapius.function_def import (
    FunctionDefinition,
    parse_function_definition
)


@dataclass
class Query:
    func_def: FunctionDefinition
    text: str


def _iterate_blocks(fd: IO[str]) -> Iterator[Tuple[bool, List[str]]]:
    block_is_comment = False
    lines: List[str] = []

    for line in fd:
        line_is_comment = line.startswith('--')
        if block_is_comment != line_is_comment and lines:
            yield block_is_comment, lines
            lines = []

        block_is_comment = line_is_comment
        lines.append(line)

    yield block_is_comment, lines


def _find_annotation(lines: List[str]) -> Optional[str]:
    def_idx = 0

    while def_idx < len(lines):
        if lines[def_idx].startswith('-- def '):
            break
        def_idx += 1
    else:
        return None

    # in future, we may trace backwards here to include preceeding @decorators
    start_idx = def_idx

    end_idx = def_idx + 1
    while end_idx < len(lines) and re.match(r'-- .*[^-\s]', lines[end_idx]):
        end_idx += 1

    return ''.join(line[3:] for line in lines[start_idx:end_idx])


def parse_queries_from_fd(fd: IO[str]) -> List[Query]:
    res = []
    current_annotation = ''
    current_text = ''

    def flush() -> None:
        nonlocal current_annotation, current_text, res
        if current_annotation and current_text:
            res.append(Query(parse_function_definition(current_annotation), current_text))

    for is_comment, lines in _iterate_blocks(fd):
        if is_comment and (annotation := _find_annotation(lines)) is not None:
            flush()
            current_annotation = annotation
            current_text = ''
        current_text += ''.join(lines)

    flush()

    return res


def parse_queries_from_path(path: str) -> List[Query]:
    with open(path, 'r') as fd:
        return parse_queries_from_fd(fd)
