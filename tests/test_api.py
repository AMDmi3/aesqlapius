import pytest

from aesqlapius import generate_api

from .fixtures import *  # noqa
from .helpers import convert_api_to_async


@pytest.fixture()
async def api(queries_dir, dbenv):
    api = generate_api(queries_dir / 'api', dbenv.driver, dbenv.db, hook=dbenv.query_adaptor)
    convert_api_to_async(api)
    await api.cleanup_test_table()
    await api.create_test_table()
    await api.fill_test_table()
    yield api
    await api.cleanup_test_table()


@pytest.mark.asyncio
async def test_pass_args(api):
    assert await api.swap_args() == ('a', 0)
    assert await api.swap_args(1) == ('a', 1)
    assert await api.swap_args(a=1) == ('a', 1)
    assert await api.swap_args(b='b') == ('b', 0)
    assert await api.swap_args(1, 'b') == ('b', 1)
    assert await api.swap_args(a=1, b='b') == ('b', 1)
    assert await api.swap_args(b='b', a=1) == ('b', 1)


@pytest.mark.asyncio
async def test_get_nothing(api):
    await api.get.nothing()


@pytest.mark.asyncio
async def test_get_single_tuple(api):
    assert await api.get.single_tuple() == (0, 'a')


@pytest.mark.asyncio
async def test_get_single_dict(api):
    assert await api.get.single_dict() == {'a': 0, 'b': 'a'}


@pytest.mark.asyncio
async def test_get_single_value(api):
    assert await api.get.single_value() == 0


@pytest.mark.asyncio
async def test_get_iterator_tuple(api):
    assert [v async for v in api.get.iterator_tuple()] == [
        (0, 'a'),
        (1, 'b'),
        (2, 'c'),
    ]


@pytest.mark.asyncio
async def test_get_iterator_dict(api):
    assert [v async for v in api.get.iterator_dict()] == [
        {'a': 0, 'b': 'a'},
        {'a': 1, 'b': 'b'},
        {'a': 2, 'b': 'c'},
    ]


@pytest.mark.asyncio
async def test_get_iterator_value(api):
    assert [v async for v in api.get.iterator_value()] == [0, 1, 2]


@pytest.mark.asyncio
async def test_get_list_tuple(api):
    assert await api.get.list_tuple() == [
        (0, 'a'),
        (1, 'b'),
        (2, 'c'),
    ]


@pytest.mark.asyncio
async def test_get_list_dict(api):
    assert await api.get.list_dict() == [
        {'a': 0, 'b': 'a'},
        {'a': 1, 'b': 'b'},
        {'a': 2, 'b': 'c'},
    ]


@pytest.mark.asyncio
async def test_get_list_value(api):
    assert await api.get.list_value() == [0, 1, 2]


@pytest.mark.asyncio
async def test_get_dict_of_tuples_by_column_name(api):
    assert await api.get.dict_of_tuples_by_column_name() == {
        0: (0, 'a'),
        1: (1, 'b'),
        2: (2, 'c'),
    }


@pytest.mark.asyncio
async def test_get_dict_of_tuples_by_column_index(api):
    assert await api.get.dict_of_tuples_by_column_index() == {
        0: (0, 'a'),
        1: (1, 'b'),
        2: (2, 'c'),
    }


@pytest.mark.asyncio
async def test_get_dict_of_tuples_by_column_name_removed_key(api):
    assert await api.get.dict_of_tuples_by_column_name_removed_key() == {
        0: ('a',),
        1: ('b',),
        2: ('c',),
    }


@pytest.mark.asyncio
async def test_get_dict_of_tuples_by_column_index_removed_key(api):
    assert await api.get.dict_of_tuples_by_column_index_removed_key() == {
        0: ('a',),
        1: ('b',),
        2: ('c',),
    }


@pytest.mark.asyncio
async def test_get_dict_of_tuples_by_column_name_out_of_range(api):
    with pytest.raises(KeyError):
        await api.get.dict_of_tuples_by_column_name_out_of_range()


@pytest.mark.asyncio
async def test_get_dict_of_tuples_by_column_index_out_of_range(api):
    with pytest.raises(IndexError):
        await api.get.dict_of_tuples_by_column_index_out_of_range()


@pytest.mark.asyncio
async def test_get_dict_of_empties(api):
    assert await api.get.dict_of_empty_dicts() == {0: {}, 1: {}, 2: {}}
    assert await api.get.dict_of_empty_tuples() == {0: (), 1: (), 2: ()}
    assert await api.get.dict_of_empty_singles() == {0: None, 1: None, 2: None}
