import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict

import pytest

__all__ = [
    'dbenv',
    'dbenv_psycopg2',
    'dbenv_sqlite3',
    'dbenv_mysql',
    'dbenv_aiopg',
    'queries_dir'
]


class DSN:
    args: Dict[str, str]

    def __init__(self, envname: str, dbtype: str) -> None:
        if not (dsn := os.environ.get(envname)):
            pytest.skip(f'No {envname} environment variable set, skipping {dbtype} database tests', allow_module_level=True)

        if dbtype in ('psycopg2', 'aiopg'):
            dbname_arg = 'dbname'
        else:
            dbname_arg = 'database'

        self.args = {}

        for item in dsn.split():
            k, v = item.split('=', 1)

            if k in ('database', 'dbname'):
                self.args[dbname_arg] = v
            else:
                self.args[k] = v

    def get(self):
        return self.args


@dataclass
class DBEnv:
    driver: str
    db: Any

    def get_query_preprocessor(self):
        def hook(text, kwargs):
            output = []

            conditionals = defaultdict(list)

            def flush():
                nonlocal conditionals, output
                if conditionals:
                    if self.driver in conditionals:
                        output += conditionals[self.driver]
                    elif 'others' in conditionals:
                        output += conditionals['others']
                    elif 'other' in conditionals:
                        output += conditionals['other']
                    conditionals = defaultdict(list)

            for line in text.split('\n'):
                if match := re.fullmatch('(.*?)[ \t]+-- ([a-z0-9_]+)', line):
                    conditionals[match.group(2)].append(match.group(1))
                else:
                    flush()
                    output.append(line)

            flush()

            res = '\n'.join(output)
            if res != text:
                print(text)
                print(res)
            return '\n'.join(output)

        return hook


async def create_dbenv_psycopg2():
    try:
        import psycopg2
    except ImportError:
        pytest.skip('Cannot import psycopg2, skipping related tests', allow_module_level=True)

    yield DBEnv(
        'psycopg2',
        psycopg2.connect(**DSN('POSTGRESQL_DSN', 'psycopg2').get())
    )


async def create_dbenv_mysql():
    try:
        import mysql.connector
    except ImportError:
        pytest.skip('Cannot import mysql.connector, skipping related tests', allow_module_level=True)

    yield DBEnv(
        'mysql',
        mysql.connector.connect(**DSN('MYSQL_DSN', 'mysql').get())
    )


async def create_dbenv_sqlite3(tmp_path):
    try:
        import sqlite3
    except ImportError:
        pytest.skip('Cannot import sqlite3, skipping related tests', allow_module_level=True)

    yield DBEnv(
        'sqlite3',
        sqlite3.connect(tmp_path / 'db.sqlite')
    )


async def create_dbenv_aiopg():
    try:
        import aiopg
    except ImportError:
        pytest.skip('Cannot import aiopg, skipping related tests', allow_module_level=True)

    async with aiopg.create_pool(**DSN('POSTGRESQL_DSN', 'aiopg').get()) as pool:
        yield DBEnv(
            'aiopg',
            pool
        )


@pytest.fixture
async def dbenv_psycopg2():
    async for dummy in create_dbenv_psycopg2():
        yield dummy


@pytest.fixture
async def dbenv_mysql():
    async for dummy in create_dbenv_mysql():
        yield dummy


@pytest.fixture
async def dbenv_sqlite3(tmp_path):
    async for dummy in create_dbenv_sqlite3(tmp_path):
        yield dummy


@pytest.fixture
async def dbenv_aiopg():
    async for dummy in create_dbenv_aiopg():
        yield dummy


@pytest.fixture(params=['psycopg2', 'sqlite3', 'mysql', 'aiopg'])
async def dbenv(request, tmp_path):
    if request.param == 'psycopg2':
        async for dummy in create_dbenv_psycopg2():
            yield dummy
    elif request.param == 'mysql':
        async for dummy in create_dbenv_mysql():
            yield dummy
    elif request.param == 'sqlite3':
        async for dummy in create_dbenv_sqlite3(tmp_path):
            yield dummy
    elif request.param == 'aiopg':
        async for dummy in create_dbenv_aiopg():
            yield dummy
    else:
        assert(False)


@pytest.fixture
def queries_dir():
    return Path(os.path.dirname(__file__)) / 'queries'
