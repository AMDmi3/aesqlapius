PYTEST?=	pytest
FLAKE8?=	flake8
MYPY?=		mypy

all: test flake8 mypy

test::
	${PYTEST} ${PYTEST_ARGS} -v -rs -p pytest-datadir

flake8::
	${FLAKE8} ${FLAKE8_ARGS} aesqlapius tests

mypy::
	${MYPY} ${MYPY_ARGS} aesqlapius
