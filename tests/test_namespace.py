import pytest

from aesqlapius.namespace import Namespace, inject_method


@pytest.fixture
def method():
    pass


@pytest.fixture
def root():
    return Namespace()


def test_inject_into_root(root, method):
    inject_method(root, ['method'], method)
    assert root.method is method


def test_inject_into_subns(root, method):
    inject_method(root, ['subns1', 'subns2', 'method'], method)
    assert root.subns1.subns2.method is method


def test_duplicate_method(root, method):
    inject_method(root, ['method'], method)
    with pytest.raises(ValueError):
        inject_method(root, ['method'], method)


def test_duplicate_method_ns(root, method):
    inject_method(root, ['subns'], method)
    with pytest.raises(ValueError):
        inject_method(root, ['subns', 'method'], method)
