import os
from typing import Iterator

import pytest

from aesqlapius import generate_api

psycopg2 = pytest.importorskip('psycopg2')
pytest_datadir = pytest.importorskip('pytest_datadir')


pytestmark = pytest.mark.skipif(
    not os.environ.get('POSTGRESQL_DSN'),
    reason='no POSTGRESQL_DSN defined, skipping PostgreSQL tests'
)


@pytest.fixture
def db():
    return psycopg2.connect(os.environ.get('POSTGRESQL_DSN'))


def test_generate_default(original_datadir, db):
    api = generate_api(original_datadir, 'psycopg2', db)

    assert api.ping() == {'pong': True}


def test_generate_nobind(original_datadir, db):
    api = generate_api(original_datadir, 'psycopg2')

    assert api.ping(db) == {'pong': True}


def test_generate_target(original_datadir, db):
    class MyDB():
        def __init__(self) -> None:
            self.db = db
            generate_api(original_datadir, 'psycopg2', self.db, target=self)

    mydb = MyDB()

    assert mydb.ping() == {'pong': True}


def test_generate_from_file(original_datadir, db):
    api = generate_api(original_datadir / '__init__.sql', 'psycopg2', db)

    assert api.ping() == {'pong': True}


def test_generate_ns_dirs(original_datadir, db):
    api = generate_api(original_datadir / 'sub', 'psycopg2', db, namespace_mode='dirs')

    assert api.root.func_a() == ('a',)
    assert api.root.func_b() == ('b',)


def test_generate_ns_files(original_datadir, db):
    api = generate_api(original_datadir / 'sub', 'psycopg2', db, namespace_mode='files')

    assert api.root.file_a.func_a() == ('a',)
    assert api.root.file_b.func_b() == ('b',)


def test_generate_ns_files_altroot(original_datadir, db):
    api = generate_api(original_datadir / 'sub', 'psycopg2', db, namespace_mode='files', namespace_root='file_a')

    assert api.root.func_a() == ('a',)
    assert api.root.file_b.func_b() == ('b',)


def test_generate_ns_flat(original_datadir, db):
    api = generate_api(original_datadir / 'sub', 'psycopg2', db, namespace_mode='flat')

    assert api.func_a() == ('a',)
    assert api.func_b() == ('b',)


@pytest.fixture()
def api(original_datadir, db):
    return generate_api(original_datadir, 'psycopg2', db)


def test_pass_args(api):
    assert(api.swap_args() == ('a', 0))
    assert(api.swap_args(1) == ('a', 1))
    assert(api.swap_args(a=1) == ('a', 1))
    assert(api.swap_args(b='b') == ('b', 0))
    assert(api.swap_args(1, 'b') == ('b', 1))
    assert(api.swap_args(a=1, b='b') == ('b', 1))
    assert(api.swap_args(b='b', a=1) == ('b', 1))


def test_get_nothing(api):
    api.get.nothing()


def test_get_single_tuple(api):
    assert api.get.single_tuple() == (0, 'a')


def test_get_single_dict(api):
    assert api.get.single_dict() == {'a': 0, 'b': 'a'}


def test_get_single_list(api):
    assert api.get.single_list() == [0, 'a']


def test_get_single_single(api):
    assert api.get.single_single() == 0


def test_get_iterator_tuple(api):
    it = api.get.iterator_tuple()
    assert(isinstance(it, Iterator))
    assert(next(it) == (0, 'a'))
    assert(next(it) == (1, 'b'))
    assert(next(it) == (2, 'c'))


def test_get_iterator_dict(api):
    it = api.get.iterator_dict()
    assert(isinstance(it, Iterator))
    assert(next(it) == {'a': 0, 'b': 'a'})
    assert(next(it) == {'a': 1, 'b': 'b'})
    assert(next(it) == {'a': 2, 'b': 'c'})


def test_get_iterator_list(api):
    it = api.get.iterator_list()
    assert(isinstance(it, Iterator))
    assert(next(it) == [0, 'a'])
    assert(next(it) == [1, 'b'])
    assert(next(it) == [2, 'c'])


def test_get_iterator_single(api):
    it = api.get.iterator_single()
    assert(isinstance(it, Iterator))
    assert(next(it) == 0)
    assert(next(it) == 1)
    assert(next(it) == 2)


def test_get_list_tuple(api):
    assert api.get.list_tuple() == [
        (0, 'a'),
        (1, 'b'),
        (2, 'c'),
    ]


def test_get_list_dict(api):
    assert api.get.list_dict() == [
        {'a': 0, 'b': 'a'},
        {'a': 1, 'b': 'b'},
        {'a': 2, 'b': 'c'},
    ]


def test_get_list_list(api):
    assert api.get.list_list() == [
        [0, 'a'],
        [1, 'b'],
        [2, 'c'],
    ]


def test_get_list_single(api):
    assert api.get.list_single() == [0, 1, 2]


def test_get_dict_of_tuples_by_column_name(api):
    assert api.get.dict_of_tuples_by_column_name() == {
        0: (0, 'a'),
        1: (1, 'b'),
        2: (2, 'c'),
    }


def test_get_dict_of_tuples_by_column_index(api):
    assert api.get.dict_of_tuples_by_column_index() == {
        0: (0, 'a'),
        1: (1, 'b'),
        2: (2, 'c'),
    }


def test_get_dict_of_tuples_by_column_name_removed_key(api):
    assert api.get.dict_of_tuples_by_column_name_removed_key() == {
        0: ('a',),
        1: ('b',),
        2: ('c',),
    }


def test_get_dict_of_tuples_by_column_index_removed_key(api):
    assert api.get.dict_of_tuples_by_column_index_removed_key() == {
        0: ('a',),
        1: ('b',),
        2: ('c',),
    }


def test_get_dict_of_tuples_by_column_name_out_of_range(api):
    with pytest.raises(KeyError):
        api.get.dict_of_tuples_by_column_name_out_of_range()


def test_get_dict_of_tuples_by_column_index_out_of_range(api):
    with pytest.raises(IndexError):
        api.get.dict_of_tuples_by_column_index_out_of_range()


def test_get_dict_of_empties(api):
    assert api.get.dict_of_empty_dicts() == {0: {}, 1: {}, 2: {}}
    assert api.get.dict_of_empty_lists() == {0: [], 1: [], 2: []}
    assert api.get.dict_of_empty_tuples() == {0: (), 1: (), 2: ()}
    assert api.get.dict_of_empty_singles() == {0: None, 1: None, 2: None}
