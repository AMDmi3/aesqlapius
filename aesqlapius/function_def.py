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
    DICT = 4


@unique
class ReturnValueInnerFormat(Enum):
    TUPLE = 1
    DICT = 2
    LIST = 3
    SINGLE = 4


@dataclass
class ReturnValueDefinition:
    outer_format: ReturnValueOuterFormat
    inner_format: Union[ReturnValueInnerFormat, str]
    outer_dict_by: Union[None, str, int] = None
    remove_key_column: bool = False


@dataclass
class FunctionDefinition:
    name: str
    args: List[ArgumentDefinition] = field(default_factory=list)
    returns: Optional[ReturnValueDefinition] = None


def _parse_return_value_inner(node: ast.AST) -> Union[ReturnValueInnerFormat, str]:
    # in future, support subscripts with detailed type specifications
    assert isinstance(node, ast.Name)

    if node.id == 'Tuple':
        return ReturnValueInnerFormat.TUPLE
    elif node.id == 'Dict':
        return ReturnValueInnerFormat.DICT
    elif node.id == 'List':
        return ReturnValueInnerFormat.LIST
    elif node.id == 'Single':
        return ReturnValueInnerFormat.SINGLE
    else:  # custom type
        return node.id


def _parse_return_value_outer(node: ast.Subscript) -> ReturnValueDefinition:
    assert isinstance(node.value, ast.Name)

    if node.value.id == 'Dict':
        # requre two args, e.g. Dict[a, b]
        assert isinstance(node.slice, ast.Tuple)
        assert len(node.slice.elts) == 2

        # handle unary minus for the first arg, e.g. Dict[-a, b]
        if isinstance(node.slice.elts[0], ast.UnaryOp):
            assert isinstance(node.slice.elts[0].op, ast.USub)
            remove_key_column = True
            dict_by = node.slice.elts[0].operand
        else:
            remove_key_column = False
            dict_by = node.slice.elts[0]

        assert isinstance(dict_by, ast.Constant)
        assert isinstance(dict_by.value, int) or isinstance(dict_by.value, str)

        return ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.DICT,
            inner_format=_parse_return_value_inner(node.slice.elts[1]),
            outer_dict_by=dict_by.value,
            remove_key_column=remove_key_column
        )

    if node.value.id == 'List':
        outer_format = ReturnValueOuterFormat.LIST
    elif node.value.id == 'Iterator':
        outer_format = ReturnValueOuterFormat.ITERATOR
    elif node.value.id == 'Single':
        outer_format = ReturnValueOuterFormat.SINGLE
    else:
        raise TypeError(f'Unexpected return value type {node.value.id}')

    return ReturnValueDefinition(
        outer_format=outer_format,
        inner_format=_parse_return_value_inner(node.slice)
    )


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
        assert isinstance(returns, ast.Subscript)
        func_def.returns = _parse_return_value_outer(returns)

    # check body
    assert(len(func.body) == 1)
    assert(isinstance(func.body[0], ast.Expr))
    assert(isinstance(func.body[0].value, ast.Constant))
    assert(func.body[0].value.value is Ellipsis)

    return func_def
