#!/usr/bin/env python3

from os import path

from setuptools import find_packages, setup


here = path.abspath(path.dirname(__file__))


def get_version():
    with open(path.join(here, 'aesqlapius', '__init__.py')) as source:
        for line in source:
            if line.startswith('__version__'):
                return line.strip().split(' = ')[-1].strip("'")

    raise RuntimeError('Cannot determine package version from package source')


def get_long_description():
    try:
        return open(path.join(here, 'README.md')).read()
    except:
        return None


setup(
    name='aesqlapius',
    version=get_version(),
    description='Manage SQL queries as a Python API',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Dmitry Marakasov',
    author_email='amdmi3@amdmi3.ru',
    url='https://github.com/AMDmi3/aesqlapius',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: SQL',
        'Topic :: Database',
    ],
    python_requires='>=3.6',
    packages=find_packages(),
)
