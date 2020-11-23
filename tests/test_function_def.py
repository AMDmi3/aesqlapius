import pytest

from aesqlapius.function_def import *


def test_simple():
    assert parse_function_definition(
        'def Foo() -> None: ...'
    ) == FunctionDefinition(
        name='Foo',
        args=[],
        returns=None
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
        ],
        returns=None
    )


def test_args():
    assert parse_function_definition(
        'def Foo(a: int, b: str, c: float) -> None: ...'
    ) == FunctionDefinition(
        name='Foo',
        args=[
            ArgumentDefinition(name='a', type_='int'),
            ArgumentDefinition(name='b', type_='str'),
            ArgumentDefinition(name='c', type_='float'),
        ],
        returns=None
    )


def test_default_args():
    assert parse_function_definition(
        'def Foo(a: int, b: int=2, c: int=3) -> None: ...'
    ) == FunctionDefinition(
        name='Foo',
        args=[
            ArgumentDefinition(name='a', type_='int'),
            ArgumentDefinition(name='b', type_='int', has_default=True, default=2),
            ArgumentDefinition(name='c', type_='int', has_default=True, default=3),
        ],
        returns=None
    )


def test_returns():
    cases = [
        ('Iterator[Tuple]', ReturnValueOuterFormat.ITERATOR, ReturnValueInnerFormat.TUPLE),
        ('Iterator[Dict]', ReturnValueOuterFormat.ITERATOR, ReturnValueInnerFormat.DICT),
        ('Iterator[List]', ReturnValueOuterFormat.ITERATOR, ReturnValueInnerFormat.LIST),
        ('List[Tuple]', ReturnValueOuterFormat.LIST, ReturnValueInnerFormat.TUPLE),
        ('List[Dict]', ReturnValueOuterFormat.LIST, ReturnValueInnerFormat.DICT),
        ('List[List]', ReturnValueOuterFormat.LIST, ReturnValueInnerFormat.LIST),
        ('Single[Tuple]', ReturnValueOuterFormat.SINGLE, ReturnValueInnerFormat.TUPLE),
        ('Single[Dict]', ReturnValueOuterFormat.SINGLE, ReturnValueInnerFormat.DICT),
        ('Single[List]', ReturnValueOuterFormat.SINGLE, ReturnValueInnerFormat.LIST),
        ('Single[MyType]', ReturnValueOuterFormat.SINGLE, 'MyType'),
    ]

    for returns, outer_format, inner_format in cases:
        assert parse_function_definition(
            f'def Foo() -> {returns}: ...'
        ) == FunctionDefinition(
            name='Foo',
            args=[],
            returns=ReturnValueDefinition(outer_format=outer_format, inner_format=inner_format)
        )


def test_returns_invalid():
    with pytest.raises(TypeError):
        parse_function_definition('def Foo() -> BadType[List]: ...')
