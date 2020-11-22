from typing import Any, Dict, Iterator, List, Tuple

from aesqlapius.function_def import ArgumentDefinition, FunctionDefinition


def _iter_args(func_def: FunctionDefinition, args: List[Any], kwargs: Dict[str, Any]) -> Iterator[Tuple[ArgumentDefinition, Any]]:
    for narg, arg in enumerate(func_def.args):
        print(arg)
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


def prepare_args_as_dict(func_def: FunctionDefinition, args: List[Any], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    return {arg.name: value for arg, value in _iter_args(func_def, args, kwargs)}


def prepare_args_as_list(func_def, args: List[Any], kwargs: Dict[str, Any]) -> List[Any]:
    return [value for arg, value in _iter_args(func_def, args, kwargs)]
