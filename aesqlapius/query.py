from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple

from aesqlapius.function_def import FunctionDefinition, parse_function_definition

@dataclass
class Query:
    func_def: FunctionDefinition
    text: str


def parse_query_file(path: str) -> List[Query]:
    func_def: Optional[FunctionDefinition] = None
    text = ''

    with open(path, 'r') as fd:
        for line in fd:
            if line.startswith('-- def '):
                func_def = parse_function_definition(line.removeprefix('-- '))

            text += line

    assert(func_def)

    return [Query(func_def, text)]
