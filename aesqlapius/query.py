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

from dataclasses import dataclass
from typing import List, Optional

from aesqlapius.function_def import (
    FunctionDefinition,
    parse_function_definition
)


@dataclass
class Query:
    func_def: FunctionDefinition
    text: str


def parse_query_file(path: str) -> List[Query]:
    func_def: Optional[FunctionDefinition] = None
    text = ''
    res = []

    def flush():
        nonlocal func_def, text, res
        if func_def and text:
            res.append(Query(func_def, text))
        func_def = None
        text = ''

    with open(path, 'r') as fd:
        for line in fd:
            if line.startswith('-- def '):
                flush()
                func_def = parse_function_definition(line.removeprefix('-- '))

            text += line

    flush()

    return res
