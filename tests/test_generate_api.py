from aesqlapius import generate_api

from .fixtures import *  # noqa


def test_default(queries_dir, dbenv):
    api = generate_api(queries_dir / 'ping.sql', dbenv.driver, dbenv.db)

    assert api.ping() == {'pong': True}


def test_nobind(queries_dir, dbenv):
    api = generate_api(queries_dir / 'ping.sql', dbenv.driver, dbenv.db)

    assert api.ping(dbenv.db) == {'pong': True}


def test_target(queries_dir, dbenv):
    class MyDB():
        def __init__(self) -> None:
            self.db = dbenv.db
            generate_api(queries_dir / 'ping.sql', dbenv.driver, self.db, target=self)

    mydb = MyDB()

    assert mydb.ping() == {'pong': True}


def test_ns_dirs(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='dirs')

    assert api.root.func_a() == ('a',)
    assert api.root.func_b() == ('b',)


def test_ns_files(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='files')

    assert api.root.file_a.func_a() == ('a',)
    assert api.root.file_b.func_b() == ('b',)


def test_ns_files_altroot(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='files', namespace_root='file_a')

    assert api.root.func_a() == ('a',)
    assert api.root.file_b.func_b() == ('b',)


def test_ns_flat(queries_dir, dbenv):
    api = generate_api(queries_dir / 'namespace', dbenv.driver, dbenv.db, namespace_mode='flat')

    assert api.func_a() == ('a',)
    assert api.func_b() == ('b',)


def test_query_hook(queries_dir, dbenv):
    def hook(text, kwargs):
        return text.replace('TRUE', 'FALSE')

    api = generate_api(queries_dir / 'ping.sql', dbenv.driver, dbenv.db, hook=hook)

    assert api.ping() == {'pong': False}  # pong value was replaced to False
