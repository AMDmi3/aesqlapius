from dataclasses import dataclass

import pytest

from aesqlapius.function_def import ReturnValueInnerFormat
from aesqlapius.output import generate_row_processor


@pytest.fixture
def row():
    return (1, 2, 3)


@pytest.fixture
def field_names():
    return ['a', 'b', 'c']


def test_tuple(row, field_names):
    rp = generate_row_processor(ReturnValueInnerFormat.TUPLE, field_names)

    assert rp(row) == (1, 2, 3)


def test_dict(row, field_names):
    rp = generate_row_processor(ReturnValueInnerFormat.DICT, field_names)

    assert rp(row) == {'a': 1, 'b': 2, 'c': 3}


def test_list(row, field_names):
    rp = generate_row_processor(ReturnValueInnerFormat.LIST, field_names)

    assert rp(row) == [1, 2, 3]


def test_custom_local(row, field_names):
    @dataclass
    class MyLocalType:
        a: int
        b: int
        c: int

    rp = generate_row_processor('MyLocalType', field_names, 1)

    assert rp(row) == MyLocalType(1, 2, 3)


@dataclass
class MyGlobalType:
    a: int
    b: int
    c: int


def test_custom_global(row, field_names):
    rp = generate_row_processor('MyGlobalType', field_names, 1)

    assert rp(row) == MyGlobalType(1, 2, 3)


def test_custom_not_found(row, field_names):
    rp = generate_row_processor('MyNonexistingType', field_names, 1)

    with pytest.raises(NameError):
        rp(row)
