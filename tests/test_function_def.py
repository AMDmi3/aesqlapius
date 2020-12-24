import pytest

from aesqlapius.function_def import (
    ArgumentDefinition,
    FunctionDefinition,
    ReturnValueDefinition,
    ReturnValueInnerFormat,
    ReturnValueOuterFormat,
    parse_function_definition
)


def test_simple():
    assert parse_function_definition(
        'def Foo() -> None: ...'
    ) == FunctionDefinition(
        name='Foo'
    )


def test_args_unannotated():
    assert parse_function_definition(
        'def Foo(a, b, c) -> None: ...'
    ) == FunctionDefinition(
        name='Foo',
        args=[
            ArgumentDefinition(name='a'),
            ArgumentDefinition(name='b'),
            ArgumentDefinition(name='c'),
        ]
    )


def test_args():
    assert parse_function_definition(
        'def Foo(a: int, b: str, c: float) -> None: ...'
    ) == FunctionDefinition(
        name='Foo',
        args=[
            ArgumentDefinition(name='a'),
            ArgumentDefinition(name='b'),
            ArgumentDefinition(name='c'),
        ]
    )


def test_default_args():
    assert parse_function_definition(
        'def Foo(a: int, b: int=2, c: int=3) -> None: ...'
    ) == FunctionDefinition(
        name='Foo',
        args=[
            ArgumentDefinition(name='a'),
            ArgumentDefinition(name='b', has_default=True, default=2),
            ArgumentDefinition(name='c', has_default=True, default=3),
        ]
    )


def test_returns_outer_iterator():
    assert parse_function_definition(
        'def Foo() -> Iterator[Tuple]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.ITERATOR,
            inner_format=ReturnValueInnerFormat.TUPLE
        )
    )


def test_returns_outer_list():
    assert parse_function_definition(
        'def Foo() -> List[Tuple]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.LIST,
            inner_format=ReturnValueInnerFormat.TUPLE
        )
    )


def test_returns_outer_single():
    assert parse_function_definition(
        'def Foo() -> Single[Tuple]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.SINGLE,
            inner_format=ReturnValueInnerFormat.TUPLE
        )
    )


def test_returns_outer_dict():
    assert parse_function_definition(
        'def Foo() -> Dict[0, Tuple]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.DICT,
            inner_format=ReturnValueInnerFormat.TUPLE,
            outer_dict_by=0
        )
    )

    assert parse_function_definition(
        'def Foo() -> Dict["colname", Tuple]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.DICT,
            inner_format=ReturnValueInnerFormat.TUPLE,
            outer_dict_by='colname'
        )
    )


def test_returns_outer_dict_remove_key():
    assert parse_function_definition(
        'def Foo() -> Dict[-0, Tuple]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.DICT,
            inner_format=ReturnValueInnerFormat.TUPLE,
            outer_dict_by=0,
            remove_key_column=True
        )
    )

    assert parse_function_definition(
        'def Foo() -> Dict[-"colname", Tuple]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.DICT,
            inner_format=ReturnValueInnerFormat.TUPLE,
            outer_dict_by='colname',
            remove_key_column=True
        )
    )


def test_returns_inner_tuple():
    assert parse_function_definition(
        'def Foo() -> Single[Tuple]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.SINGLE,
            inner_format=ReturnValueInnerFormat.TUPLE
        )
    )


def test_returns_inner_dict():
    assert parse_function_definition(
        'def Foo() -> Single[Dict]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.SINGLE,
            inner_format=ReturnValueInnerFormat.DICT
        )
    )


def test_returns_inner_value():
    assert parse_function_definition(
        'def Foo() -> Single[Value]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.SINGLE,
            inner_format=ReturnValueInnerFormat.VALUE
        )
    )


def test_accepts_complex_arg_annotations():
    assert parse_function_definition(
        'def Foo(arg: Tuple[str, int]) -> None: ...'
    ) == FunctionDefinition(
        name='Foo',
        args=[
            ArgumentDefinition(name='arg'),
        ]
    )


def test_accepts_complex_return_annotations():
    assert parse_function_definition(
        'def Foo() -> Single[Value[bool]]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.SINGLE,
            inner_format=ReturnValueInnerFormat.VALUE
        )
    )
    assert parse_function_definition(
        'def Foo() -> Single[Value[Optional[str]]]: ...'
    ) == FunctionDefinition(
        name='Foo',
        returns=ReturnValueDefinition(
            outer_format=ReturnValueOuterFormat.SINGLE,
            inner_format=ReturnValueInnerFormat.VALUE
        )
    )


def test_syntax_requires_single_statement():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> None: ...\ndef B() -> None: ...')


def test_syntax_requires_function_definition():
    with pytest.raises(SyntaxError):
        parse_function_definition('foo = 1')


def test_syntax_requires_constant_default_arg():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A(foo=1+1) -> None: ...')


def test_syntax_requires_body_ellipsis():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> None: 1')

    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> None:\n    ...\n    ...')


def test_syntax_requires_returns():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A(): ...')


def test_syntax_requires_returns_rows_subscript():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> Single: ...')


def test_syntax_requires_returns_rows_subscript_name():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> 1[1]: ...')


def test_syntax_requires_returns_rows_corrent():
    with pytest.raises(TypeError):
        parse_function_definition('def Foo() -> BadType[List]: ...')


def test_syntax_requires_returns_row_subscript():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> Single[1]: ...')


def test_syntax_requires_returns_row_subscript_name():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> Single[1[1]]: ...')


def test_syntax_requires_returns_row_corrent():
    with pytest.raises(TypeError):
        parse_function_definition('def A() -> List[BadType]: ...')


def test_syntax_requires_returns_dict_nargs():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> Dict[1, 2, Value]: ...')

    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> Dict[Value]: ...')


def test_syntax_requires_returns_dict_colref():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> Dict[0.0, Value]: ...')


def test_syntax_requires_returns_dict_colref_modifier():
    with pytest.raises(SyntaxError):
        parse_function_definition('def A() -> Dict[+1, Value]: ...')
