import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict

import pytest

__all__ = ['dbenv', 'queries_dir']


@dataclass
class DBEnv:
    driver: str
    db: Any
    query_adaptor: Callable[[str, Dict[str, Any]], str] = None


@pytest.fixture(params=['psycopg2', 'sqlite3', 'mysql', 'aiopg'])
async def dbenv(request, tmp_path):
    if request.param == 'psycopg2':
        try:
            import psycopg2
        except ImportError:
            pytest.skip('Cannot import psycopg2, skipping related tests', allow_module_level=True)

        if not os.environ.get('POSTGRESQL_DSN'):
            pytest.skip('No POSTGRESQL_DSN envvar defined, skipping postgresql related tests', allow_module_level=True)

        yield DBEnv(
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

        yield DBEnv(
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

        yield DBEnv(
            request.param,
            sqlite3.connect(tmp_path / 'db.sqlite'),
            convert_query_to_sqlite
        )

    elif request.param == 'aiopg':
        try:
            import aiopg
        except ImportError:
            pytest.skip('Cannot import aiopg, skipping related tests', allow_module_level=True)

        if not os.environ.get('POSTGRESQL_DSN'):
            pytest.skip('No POSTGRESQL_DSN envvar defined, skipping postgresql related tests', allow_module_level=True)

        async with aiopg.create_pool(os.environ.get('POSTGRESQL_DSN')) as pool:
            yield DBEnv(
                request.param,
                pool
            )

    else:
        assert(False)


@pytest.fixture
def queries_dir():
    return Path(os.path.dirname(__file__)) / 'queries'
