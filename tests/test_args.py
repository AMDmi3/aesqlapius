import pytest

from aesqlapius.args import prepare_args_as_dict, prepare_args_as_list
from aesqlapius.function_def import parse_function_definition


@pytest.fixture
def func_def():
    func_code = """def foo(a: str,
                b: int,
                c: str="c",
                d: int=4,
                e: str="e",
                f: int=6) -> None: ...
    """

    return parse_function_definition(func_code)


def test_dict_as_dict(func_def):
    assert prepare_args_as_dict(
        func_def,
        [
            'a',
            2,
            'cc',
            44
        ],
        {}
    ) == {
        'a': 'a',
        'b': 2,
        'c': 'cc',
        'd': 44,
        'e': 'e',
        'f': 6
    }


def test_list_as_dict(func_def):
    assert prepare_args_as_dict(
        func_def,
        [],
        {
            'a': 'a',
            'b': 2,
            'c': 'cc',
            'd': 44
        }
    ) == {
        'a': 'a',
        'b': 2,
        'c': 'cc',
        'd': 44,
        'e': 'e',
        'f': 6
    }


def test_dict_as_list(func_def):
    assert prepare_args_as_list(
        func_def,
        [
            'a',
            2,
            'cc',
            44
        ],
        {}
    ) == [
        'a',
        2,
        'cc',
        44,
        'e',
        6
    ]


def test_list_as_list(func_def):
    assert prepare_args_as_list(
        func_def,
        [],
        {
            'a': 'a',
            'b': 2,
            'c': 'cc',
            'd': 44
        }
    ) == [
        'a',
        2,
        'cc',
        44,
        'e',
        6
    ]


def test_missing_args(func_def):
    with pytest.raises(TypeError):
        prepare_args_as_list(func_def, [], {})


def test_duplicate_args(func_def):
    with pytest.raises(TypeError):
        prepare_args_as_list(func_def, ['a'], {'a': 'a'})


def test_incorrect_default_arguments():
    with pytest.raises(SyntaxError):
        parse_function_definition('def foo(a=1,b): ...')
