import io

import pytest

from aesqlapius.function_def import ArgumentDefinition, FunctionDefinition
from aesqlapius.query import Query, parse_queries_from_fd


def test_simple():
    prefix = (
        '-- some strings not related to any method\n'
        '-- some more strings\n'
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


@pytest.mark.xfail
def test_multiline_definition():
    text = (
        '-- def foo(\n'
        '--     a,\n'
        '--     b,\n'
        '-- ) -> None: ...\n'
        'SELECT 1;\n'
    )

    assert parse_queries_from_fd(
        io.StringIO(text)
    ) == [
        Query(
            func_def=FunctionDefinition(
                name='foo',
                args=[
                    ArgumentDefinition(name='a'),
                    ArgumentDefinition(name='b')
                ],
                returns=None
            ),
            text=text
        ),
    ]
