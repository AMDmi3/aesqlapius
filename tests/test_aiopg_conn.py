import pytest

from aesqlapius import generate_api

from .fixtures import *  # noqa
from .helpers import convert_api_to_async


@pytest.mark.asyncio
async def test_default(queries_dir, dbenv_aiopg):
    api = generate_api(queries_dir / 'ping.sql', 'aiopg_conn')
    convert_api_to_async(api)

    async with dbenv_aiopg.db.acquire() as conn:
        assert await api.ping(conn) == {'pong': True}
