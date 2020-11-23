from dataclasses import dataclass
from typing import List, Optional

from aesqlapius.function_def import FunctionDefinition, parse_function_definition


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
