import io

from aesqlapius.function_def import ArgumentDefinition, FunctionDefinition
from aesqlapius.query import Query, parse_queries_from_fd


def test_simple():
    prefix = (
        '-- some strings not related to any method\n'
        '-- some more strings\n'
        '\n'
    )
    foo_text = (
        '-- def foo() -> None: ...\n'
        'SELECT\n'
        '    1 + 1;\n'
    )
    bar_text = (
        '-- def bar() -> None: ...\n'
        'SELECT 2;\n'
    )

    assert parse_queries_from_fd(
        io.StringIO(prefix + foo_text + bar_text)
    ) == [
        Query(
            func_def=FunctionDefinition(
                name='foo',
                args=[],
                returns=None
            ),
            text=foo_text
        ),
        Query(
            func_def=FunctionDefinition(
                name='bar',
                args=[],
                returns=None
            ),
            text=bar_text
        )
    ]


def test_multiline_definition():
    text_foo = (
        '-- def foo(a) -> None:\n'
        '--     ...\n'
        'SELECT 1;\n'
    )

    text_bar = (
        '--\n'
        '-- Start bar function\n'
        '--\n'
        '-- def bar(\n'
        '--     a\n'
        '-- ) -> None: ...\n'
        '--\n'
        '-- End bar function\n'
        '--\n'
        '\n'
        'SELECT 1;\n'
        '\n'
    )

    text_baz = (
        '--------------------------------------------------\n'
        '-- def baz(\n'
        '--     a\n'
        '-- ) -> None:\n'
        '--     ...\n'
        '--------------------------------------------------\n'
        '\n'
        'SELECT\n'
        '-- this following line calculates sum of 1 and 1\n'
        '1+1;\n'
    )

    assert parse_queries_from_fd(
        io.StringIO(text_foo + text_bar + text_baz)
    ) == [
        Query(
            func_def=FunctionDefinition(
                name='foo',
                args=[ArgumentDefinition(name='a')],
                returns=None
            ),
            text=text_foo
        ),
        Query(
            func_def=FunctionDefinition(
                name='bar',
                args=[ArgumentDefinition(name='a')],
                returns=None
            ),
            text=text_bar
        ),
        Query(
            func_def=FunctionDefinition(
                name='baz',
                args=[ArgumentDefinition(name='a')],
                returns=None
            ),
            text=text_baz
        ),
    ]
