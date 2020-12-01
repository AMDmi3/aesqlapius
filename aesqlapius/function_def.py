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

import ast
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any, List, Optional, Union


@dataclass
class ArgumentDefinition:
    name: str
    type_: Any = None
    has_default: bool = False
    default: Any = None


@unique
class ReturnValueOuterFormat(Enum):
    ITERATOR = 1
    LIST = 2
    SINGLE = 3
    # DICT = 4  # TODO


@unique
class ReturnValueInnerFormat(Enum):
    TUPLE = 1
    DICT = 2
    LIST = 3


@dataclass
class ReturnValueDefinition:
    outer_format: ReturnValueOuterFormat
    inner_format: Union[ReturnValueInnerFormat, str]


@dataclass
class FunctionDefinition:
    name: str
    args: List[ArgumentDefinition] = field(default_factory=list)
    returns: Optional[ReturnValueDefinition] = None


def parse_function_definition(source: str) -> FunctionDefinition:
    tree = ast.parse(source)

    assert(len(tree.body) == 1)
    assert(isinstance(tree.body[0], ast.FunctionDef))

    func = tree.body[0]

    func_def = FunctionDefinition(name=func.name)

    # parse arguments
    for arg in func.args.args:
        arg_def = ArgumentDefinition(
            name=arg.arg,
            type_=arg.annotation.id if arg.annotation else None  # type: ignore
        )

        func_def.args.append(arg_def)

    # parse default values
    first_default_idx = len(func.args.args) - len(func.args.defaults)

    for argn, default in enumerate(func.args.defaults, first_default_idx):
        assert(isinstance(default, ast.Constant))

        func_def.args[argn].has_default = True
        func_def.args[argn].default = default.value

    # parse return value
    returns = func.returns

    if isinstance(returns, ast.Constant) and returns.value is None:
        func_def.returns = None
    else:
        assert(isinstance(returns, ast.Subscript))

        if returns.value.id in ('List', 'list'):  # type: ignore
            outer_format = ReturnValueOuterFormat.LIST
        elif returns.value.id == 'Iterator':  # type: ignore
            outer_format = ReturnValueOuterFormat.ITERATOR
        elif returns.value.id == 'Single':  # type: ignore
            outer_format = ReturnValueOuterFormat.SINGLE
        else:
            raise TypeError(f'Unexpected return value type {returns.value.id}')  # type: ignore

        if returns.slice.id in ('Tuple', 'tuple'):  # type: ignore
            inner_format = ReturnValueInnerFormat.TUPLE
        elif returns.slice.id in ('Dict', 'dict'):  # type: ignore
            inner_format = ReturnValueInnerFormat.DICT
        elif returns.slice.id in ('List', 'list'):  # type: ignore
            inner_format = ReturnValueInnerFormat.LIST
        else:  # custom type
            inner_format = returns.slice.id  # type: ignore

        func_def.returns = ReturnValueDefinition(outer_format, inner_format)

    # check body
    assert(len(func.body) == 1)
    assert(isinstance(func.body[0], ast.Expr))
    assert(isinstance(func.body[0].value, ast.Constant))
    assert(func.body[0].value.value is Ellipsis)

    return func_def
