import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import pytest

from aesqlapius import generate_api


@dataclass
class DBEnv:
    driver: str
    db: Any
    hook: Any = None


@pytest.fixture(params=['psycopg2', 'sqlite3', 'mysql'])
def dbenv(request, tmp_path):
    if request.param == 'psycopg2':
        try:
            import psycopg2
        except ImportError:
            pytest.skip('Cannot import psycopg2, skipping related tests', allow_module_level=True)

        if not os.environ.get('POSTGRESQL_DSN'):
            pytest.skip('No POSTGRESQL_DSN envvar defined, skipping postgresql related tests', allow_module_level=True)

        return DBEnv(
            request.param,
            psycopg2.connect(os.environ.get('POSTGRESQL_DSN'))
        )

    elif request.param == 'mysql':
        try:
            import mysql.connector
        except ImportError:
            pytest.skip('Cannot import mysql.connector, skipping related tests', allow_module_level=True)

        if not os.environ.get('MYSQL_DSN'):
            pytest.skip('No MYSQL_DSN envvar defined, skipping mysql related tests', allow_module_level=True)

        return DBEnv(
            request.param,
            mysql.connector.connect(**{
                k: v
                for k, v in map(
                    lambda s: s.split('=', 1),
                    os.environ.get('MYSQL_DSN').split()
                )
            })
        )

    elif request.param == 'sqlite3':
        try:
            import sqlite3
        except ImportError:
            pytest.skip('Cannot import sqlite3, skipping related tests', allow_module_level=True)

        def convert_query_to_sqlite(text, kwargs):
            return re.sub(r'%\(([^()]+)\)s', r':\1', text)

        return DBEnv(
            request.param,
            sqlite3.connect(tmp_path / 'db.sqlite'),
            convert_query_to_sqlite
        )

    else:
        assert(False)


@pytest.fixture
def queries_dir():
    return Path(os.path.dirname(__file__)) / 'queries'


def test_generate_default(queries_dir, dbenv):
    api = generate_api(queries_dir / 'ping.sql', dbenv.driver, dbenv.db)

    assert api.ping() == {'pong': True}


def test_generate_nobind(queries_dir, dbenv):
    api = generate_api(queries_dir / 'ping.sql', dbenv.driver, dbenv.db)

    assert api.ping(dbenv.db) == {'pong': True}


def test_generate_target(queries_dir, dbenv):
    class MyDB():
        def __init__(self) -> None:
            self.db = dbenv.db
            generate_api(queries_dir / 'ping.sql', dbenv.driver, self.db, target=self)

    mydb = MyDB()

    assert mydb.ping() == {'pong': True}


def test_generate_ns_dirs(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='dirs')

    assert api.root.func_a() == ('a',)
    assert api.root.func_b() == ('b',)


def test_generate_ns_files(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='files')

    assert api.root.file_a.func_a() == ('a',)
    assert api.root.file_b.func_b() == ('b',)


def test_generate_ns_files_altroot(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='files', namespace_root='file_a')

    assert api.root.func_a() == ('a',)
    assert api.root.file_b.func_b() == ('b',)


def test_generate_ns_flat(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='flat')

    assert api.func_a() == ('a',)
    assert api.func_b() == ('b',)


def test_query_hook(queries_dir, dbenv):
    def hook(text, kwargs):
        return text.replace('TRUE', 'FALSE')

    api = generate_api(queries_dir / 'ping.sql', dbenv.driver, dbenv.db, hook=hook)

    assert api.ping() == {'pong': False}  # pong value was replaced to False


@pytest.fixture()
def api(queries_dir, dbenv):
    api = generate_api(queries_dir / 'api', dbenv.driver, dbenv.db, hook=dbenv.hook)
    api.cleanup_test_table()
    api.create_test_table()
    api.fill_test_table()
    yield api
    api.cleanup_test_table()


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


def test_get_single_value(api):
    assert api.get.single_value() == 0


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


def test_get_iterator_value(api):
    it = api.get.iterator_value()
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


def test_get_list_value(api):
    assert api.get.list_value() == [0, 1, 2]


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
    assert api.get.dict_of_empty_tuples() == {0: (), 1: (), 2: ()}
    assert api.get.dict_of_empty_singles() == {0: None, 1: None, 2: None}
