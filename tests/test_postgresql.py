import os
from typing import Iterator

import pytest

from aesqlapius.apis.psycopg2 import generate_api


psycopg2 = pytest.importorskip('psycopg2')
pytest_datadir = pytest.importorskip('pytest_datadir')


pytestmark = pytest.mark.skipif(
    not os.environ.get('POSTGRESQL_DSN'),
    reason='no POSTGRESQL_DSN defined, skipping PostgreSQL tests'
)


@pytest.fixture(scope='module')
def api(original_datadir):
    db = psycopg2.connect(os.environ.get('POSTGRESQL_DSN'))
    return generate_api(db, original_datadir)


def test_init(api):
    api.create()
    api.insert()  # 0, 'foo' as default
    api.insert(1, 'bar')
    api.insert(2, 'baz')


def test_getall_iterator_tuple(api):
    it = api.getall_iterator_tuple()
    assert(isinstance(it, Iterator))
    assert(next(it) == (0, 'foo'))
    assert(next(it) == (1, 'bar'))
    assert(next(it) == (2, 'baz'))


def test_getall_iterator_dict(api):
    it = api.getall_iterator_dict()
    assert(isinstance(it, Iterator))
    assert(next(it) == {'a': 0, 'b': 'foo'})
    assert(next(it) == {'a': 1, 'b': 'bar'})
    assert(next(it) == {'a': 2, 'b': 'baz'})


def test_getall_iterator_list(api):
    it = api.getall_iterator_list()
    assert(isinstance(it, Iterator))
    assert(next(it) == [0, 'foo'])
    assert(next(it) == [1, 'bar'])
    assert(next(it) == [2, 'baz'])


def test_getall_list_tuple(api):
    assert api.getall_list_tuple() == [
        (0, 'foo'),
        (1, 'bar'),
        (2, 'baz'),
    ]


def test_getall_list_dict(api):
    assert api.getall_list_dict() == [
        {'a': 0, 'b': 'foo'},
        {'a': 1, 'b': 'bar'},
        {'a': 2, 'b': 'baz'},
    ]


def test_getall_list_list(api):
    assert api.getall_list_list() == [
        [0, 'foo'],
        [1, 'bar'],
        [2, 'baz'],
    ]


def test_get_single_tuple(api):
    assert api.get_single_tuple() == (0, 'foo')


def test_get_single_dict(api):
    assert api.get_single_dict() == {'a': 0, 'b': 'foo'}


def test_get_single_list(api):
    assert api.get_single_list() == [0, 'foo']
