PYTEST?=	pytest
FLAKE8?=	flake8
MYPY?=		mypy
ISORT?=		isort

all: test flake8 mypy

test::
	${PYTEST} ${PYTEST_ARGS} -v -rs -p pytest-datadir

flake8::
	${FLAKE8} ${FLAKE8_ARGS} --application-import-names=aesqlapius aesqlapius tests

mypy::
	${MYPY} ${MYPY_ARGS} aesqlapius

isort::
	${ISORT} ${ISORT_ARGS} aesqlapius/**/*.py tests/*.py
