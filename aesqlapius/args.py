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

from typing import Any, Dict, Iterator, List, Tuple

from aesqlapius.function_def import ArgumentDefinition, FunctionDefinition


def _iter_args(func_def: FunctionDefinition, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Iterator[Tuple[ArgumentDefinition, Any]]:
    for narg, arg in enumerate(func_def.args):
        value: Any = None
        if narg < len(args):
            if arg.name in kwargs:
                raise TypeError(f"{func_def.name} got multiple values for argument '{arg.name}'")
            value = args[narg]
        elif arg.name in kwargs:
            value = kwargs[arg.name]
        elif arg.has_default:
            value = arg.default
        else:
            raise TypeError(f"{func_def.name} missing required argument '{arg.name}'")

        yield arg, value


def prepare_args_as_dict(func_def: FunctionDefinition, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    return {arg.name: value for arg, value in _iter_args(func_def, args, kwargs)}


def prepare_args_as_list(func_def, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> List[Any]:
    return [value for arg, value in _iter_args(func_def, args, kwargs)]
