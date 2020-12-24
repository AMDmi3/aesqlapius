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
    VALUE = 3


@dataclass
class ReturnValueDefinition:
    outer_format: ReturnValueOuterFormat
    inner_format: ReturnValueInnerFormat
    outer_dict_by: Union[None, str, int] = None
    remove_key_column: bool = False


@dataclass
class FunctionDefinition:
    name: str
    args: List[ArgumentDefinition] = field(default_factory=list)
    returns: Optional[ReturnValueDefinition] = None


def _parse_return_value_inner(node: ast.AST) -> ReturnValueInnerFormat:
    if isinstance(node, ast.Subscript):
        if not isinstance(node.value, ast.Name):
            raise SyntaxError(f"unexpected row format '{ast.unparse(node)}'")
        row_format_name = node.value.id
    elif isinstance(node, ast.Name):
        row_format_name = node.id
    else:
        raise SyntaxError(f"unexpected row format '{ast.unparse(node)}'")

    if row_format_name == 'Tuple':
        return ReturnValueInnerFormat.TUPLE
    elif row_format_name == 'Dict':
        return ReturnValueInnerFormat.DICT
    elif row_format_name == 'Value':
        return ReturnValueInnerFormat.VALUE
    else:
        raise TypeError(f"unexpected row format '{row_format_name}'")


def _parse_return_value_outer(node: ast.Subscript) -> ReturnValueDefinition:
    if not isinstance(node.value, ast.Name):
        raise SyntaxError(f"unexpected rows format '{ast.unparse(node)}'")

    if node.value.id == 'Dict':
        if not isinstance(node.slice, ast.Tuple) or len(node.slice.elts) != 2:
            raise SyntaxError(f"unexpected Dict row format specification '{ast.unparse(node)}'")

        # handle unary minus for the first arg, e.g. Dict[-a, b]
        if isinstance(node.slice.elts[0], ast.UnaryOp):
            if not isinstance(node.slice.elts[0].op, ast.USub):
                raise SyntaxError(f"unexpected column reference format '{ast.unparse(node.slice.elts[0])}'")
            remove_key_column = True
            dict_by = node.slice.elts[0].operand
        else:
            remove_key_column = False
            dict_by = node.slice.elts[0]

        if not isinstance(dict_by, ast.Constant) or not (isinstance(dict_by.value, int) or isinstance(dict_by.value, str)):
            raise SyntaxError(f"expected string or numeric column reference, not '{ast.unparse(dict_by)}'")

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
        raise TypeError(f"unexpected rows format '{node.value.id}'")

    return ReturnValueDefinition(
        outer_format=outer_format,
        inner_format=_parse_return_value_inner(node.slice)
    )


def parse_function_definition(source: str) -> FunctionDefinition:
    tree = ast.parse(source)

    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise SyntaxError('single function definition expected')

    func = tree.body[0]

    func_def = FunctionDefinition(name=func.name)

    # parse arguments
    for arg in func.args.args:
        arg_def = ArgumentDefinition(
            name=arg.arg
        )

        func_def.args.append(arg_def)

    # parse default values
    first_default_idx = len(func.args.args) - len(func.args.defaults)

    for argn, default in enumerate(func.args.defaults, first_default_idx):
        if not isinstance(default, ast.Constant):
            raise SyntaxError(f"constant default expected, not '{ast.unparse(default)}'")

        func_def.args[argn].has_default = True
        func_def.args[argn].default = default.value

    # parse return value
    returns = func.returns

    if isinstance(returns, ast.Constant) and returns.value is None:
        func_def.returns = None
    else:
        if returns is None:
            raise SyntaxError('return value annotation required')
        elif not isinstance(returns, ast.Subscript):
            raise SyntaxError(f"unexpected rows format '{ast.unparse(returns)}'")
        func_def.returns = _parse_return_value_outer(returns)

    # check body
    if len(func.body) != 1 or not isinstance(func.body[0], ast.Expr) or not isinstance(func.body[0].value, ast.Constant) or func.body[0].value.value is not Ellipsis:
        raise SyntaxError('single ellipsis expected as function body')

    return func_def
