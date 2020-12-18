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


def test_value(row, field_names):
    rp = generate_row_processor(ReturnValueInnerFormat.VALUE, field_names)

    assert rp(row) == 1
