from dataclasses import dataclass
from typing import Any, Dict, Iterator, Optional, Tuple

from aesqlapius.function_def import FunctionDefinition, parse_function_definition

@dataclass
class Query:
    func_def: FunctionDefinition
    text: str

    def prepare_args(self, *args, **kwargs) -> Dict[str, Any]:
        prepared_args = {}

        for narg, arg in enumerate(self.func_def.args):
            value: Any = None
            if narg < args.length():
                if arg.name in kwargs:
                    raise TypeError(f"{self.func_def.name} got multiple values for argument '{arg.name}'")
                value = args[narg]
            elif arg.name in kwargs:
                value = kwargs[arg.name]
            elif arg.has_default:
                value = arg.default
            else:
                raise TypeError(f"{self.func_def.name} missing required positional argument '{arg.name}'")

            prepared_args[name] = value

        return prepared_args


def parse_query(path: str) -> Query:
    func_def: Optional[FunctionDefinition] = None
    text = ''

    with open(path, 'r') as fd:
        for line in fd:
            if line.startswith('-- def '):
                func_def = parse_function_definition(line.removeprefix('-- '))

            text += line

    assert(func_def)

    return Query(func_def, text)
