import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import pytest

__all__ = [
    'dbenv',
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


@pytest.fixture(params=[
    'psycopg2',
    'sqlite3',
    'mysql',
    'aiopg_pool',
    'aiopg_conn',
    'asyncpg_pool',
    'asyncpg_pool_conn',
    'asyncpg_conn',
])
async def dbenv(request, tmp_path):
    try:
        if request.param == 'psycopg2':
            import psycopg2
            yield DBEnv('psycopg2', psycopg2.connect(**DSN('POSTGRESQL_DSN', 'psycopg2').get()))
        elif request.param == 'mysql':
            import mysql.connector
            yield DBEnv('mysql', mysql.connector.connect(**DSN('MYSQL_DSN', 'mysql').get()))
        elif request.param == 'sqlite3':
            import sqlite3
            yield DBEnv('sqlite3', sqlite3.connect(tmp_path / 'db.sqlite'))
        elif request.param == 'aiopg_pool':
            import aiopg
            async with aiopg.create_pool(**DSN('POSTGRESQL_DSN', 'aiopg').get()) as pool:
                yield DBEnv('aiopg', pool)
        elif request.param == 'aiopg_conn':
            import aiopg
            async with aiopg.create_pool(**DSN('POSTGRESQL_DSN', 'aiopg').get()) as pool:
                async with pool.acquire() as conn:
                    yield DBEnv('aiopg', conn)
        elif request.param == 'asyncpg_pool':
            import asyncpg
            async with asyncpg.create_pool(**DSN('POSTGRESQL_DSN', 'asyncpg').get()) as pool:
                yield DBEnv('asyncpg', pool)
        elif request.param == 'asyncpg_pool_conn':
            import asyncpg
            async with asyncpg.create_pool(**DSN('POSTGRESQL_DSN', 'asyncpg').get()) as pool:
                async with pool.acquire() as conn:
                    yield DBEnv('asyncpg', conn)
        elif request.param == 'asyncpg_conn':
            import asyncpg
            conn = await asyncpg.connect(**DSN('POSTGRESQL_DSN', 'asyncpg').get())
            yield DBEnv('asyncpg', conn)
        else:
            assert(False)

    except ImportError as e:
        pytest.skip(f'Cannot import {e.name}, skipping related tests', allow_module_level=True)


@pytest.fixture
def queries_dir():
    return Path(os.path.dirname(__file__)) / 'queries'
