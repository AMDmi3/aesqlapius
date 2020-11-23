import inspect
from typing import Any, Callable, Dict, List, Tuple, Union

from aesqlapius.function_def import ReturnValueInnerFormat

def generate_row_processor(inner_format: Union[ReturnValueInnerFormat, str], field_names: List[str], stack_depth: int = 2) -> Callable[[Tuple[Any]], Any]:
    if isinstance(inner_format, str):
        def process_row(row: Tuple[Any]) -> Dict[str, Any]:
            # get the frame of method caller; usually,
            # [0] is process_row
            # [1] is generated method
            # [2] is caller
            # but stack depth is customizable to simplify testing the function
            caller_frame = inspect.stack()[stack_depth].frame

            if inner_format in caller_frame.f_locals:
                custom_format = caller_frame.f_locals[inner_format]
            elif inner_format in caller_frame.f_globals:
                custom_format = caller_frame.f_globals[inner_format]
            else:
                raise NameError(f"name '{inner_format}' is not defined")

            return custom_format(**dict(zip(field_names, row)))

    elif inner_format == ReturnValueInnerFormat.TUPLE:
        def process_row(row: Tuple[Any]) -> Tuple[Any]:
            return row

    elif inner_format == ReturnValueInnerFormat.DICT:
        def process_row(row: Tuple[Any]) -> Dict[str, Any]:
            return dict(zip(field_names, row))

    elif inner_format == ReturnValueInnerFormat.LIST:
        def process_row(row: Tuple[Any]) -> List[Any]:
            return list(row)

    else:
        raise NotImplementedError(f"unsupported inner return type format '{inner_format}'")  # pragma: no cover

    return process_row

