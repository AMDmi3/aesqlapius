import pytest

from aesqlapius import generate_api

from .fixtures import *  # noqa
from .helpers import convert_api_to_async


# checks loading from single file and database connection binding
@pytest.mark.asyncio
async def test_default(queries_dir, dbenv):
    api = generate_api(queries_dir / 'ping.sql', dbenv.driver, dbenv.db)
    convert_api_to_async(api)

    assert await api.ping() == {'pong': True}


@pytest.mark.asyncio
async def test_nobind(queries_dir, dbenv):
    api = generate_api(queries_dir / 'ping.sql', dbenv.driver)
    convert_api_to_async(api)

    assert await api.ping(dbenv.db) == {'pong': True}


@pytest.mark.asyncio
async def test_target(queries_dir, dbenv):
    class MyDB():
        def __init__(self) -> None:
            self.db = dbenv.db
            generate_api(queries_dir / 'ping.sql', dbenv.driver, self.db, target=self)

    mydb = MyDB()
    convert_api_to_async(mydb)

    assert await mydb.ping() == {'pong': True}


@pytest.mark.asyncio
async def test_ns_dirs(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='dirs')
    convert_api_to_async(api)

    assert await api.root.func_a() == ('a',)
    assert await api.root.func_b() == ('b',)


@pytest.mark.asyncio
async def test_ns_files(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='files')
    convert_api_to_async(api)

    assert await api.root.file_a.func_a() == ('a',)
    assert await api.root.file_b.func_b() == ('b',)


@pytest.mark.asyncio
async def test_ns_files_altroot(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='files', namespace_root='file_a')
    convert_api_to_async(api)

    assert await api.root.func_a() == ('a',)
    assert await api.root.file_b.func_b() == ('b',)


@pytest.mark.asyncio
async def test_ns_flat(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='flat')
    convert_api_to_async(api)

    assert await api.func_a() == ('a',)
    assert await api.func_b() == ('b',)


@pytest.mark.asyncio
async def test_query_hook(queries_dir, dbenv):
    def hook(text, kwargs):
        return text.replace('TRUE', 'FALSE')

    api = generate_api(queries_dir / 'ping.sql', dbenv.driver, dbenv.db, hook=hook)
    convert_api_to_async(api)

    assert await api.ping() == {'pong': False}  # pong value was replaced to False
