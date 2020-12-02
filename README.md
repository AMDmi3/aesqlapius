# aeSQLAPIus

<a href="https://repology.org/project/python:aesqlapius/versions">
	<img src="https://repology.org/badge/vertical-allrepos/python:aesqlapius.svg" alt="Packaging status" align="right">
</a>

![CI](https://github.com/AMDmi3/aesqlapius/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/AMDmi3/aesqlapius/branch/master/graph/badge.svg?token=87aZsxlja2)](https://codecov.io/gh/AMDmi3/aesqlapius)
[![PyPI downloads](https://img.shields.io/pypi/dm/aesqlapius.svg)](https://pypi.org/project/aesqlapius/)
[![Github commits (since latest release)](https://img.shields.io/github/commits-since/AMDmi3/aesqlapius/latest.svg)](https://github.com/AMDmi3/aesqlapius)


## Summary

So you don't want to use ORM, and want to organize your SQL queries
in a convenient way. Don't mix them with your python code, don't
write `execute` and `fetchrow`s by hand for each query. With
**aesqlapius**:

- Store your SQL queries separate from the code, in a dedicated
  file or directory hierarchy
- Annotate each query with python-like function definition specifying
  input arguments and output types and patterns

**aesqlapius** builds a class out of this, where you can call your
queries as plain methods. It handles arguments (pass positional
or keyword arguments as you like, default values are also handled) and
output types and patterns (you may specify whether a method returns
iterator, list, dict of rows, or a single row, where row may
be represented as a tuple, list, dict, single value or a custom
type such as a dataclass).

## Example

queries.sql:
```sql
-- def add_city(name, population = None) -> None: ...
INSERT INTO cities VALUES (%(name)s, %(population)s);

-- def list_cities() -> List[Single]: ...
SELECT name FROM cities ORDER BY name;

-- def get_population(city: str) -> Single[Single]: ...
SELECT population FROM cities WHERE name = %(city)s;

-- def get_city(city: str) -> Single[City]: ...
SELECT * FROM cities WHERE name = %(city)s;
```

script.py:
```python
from aesqlapius import generate_api

db = psycopg2.connect('...')
api = generate_api('queries.sql', 'psycopg2', db)

api.add_city('Moscow', 12500000)
api.add_city('Paris')
api.add_city(population=380000, name='Berlin')

assert api.list_cities() == ['Berlin', 'Moscow', 'Paris']
assert api.get_population('Moscow') == 12500000

@dataclass
class City:
    name: str
    population: Optional[int]

assert api.get_city('Berlin') == City('Berlin', 3800000)
```

## Reference

### Python API

The module has a single entry point in form of a function:

```python
def generate_api(path, driver, db=None, *, target=None, extension='.sql', namespace_mode='dirs', namespace_root='__init__')
```

This loads SQL queries from *path* (a file or directory) and returns an API class to use with specified database *driver* (`psycopg2`, `sqlite3`).

If *db* is specified, all generated methods are bound to the given database connection object:

```python
db = psycopg2.connect('...')
api = generate_api('queries.sql', 'psycopg2', db)
api.my_method('arg1', 'arg2')
```
otherwise caller is expected to pass database connection object to each call:
```python
db = psycopg2.connect('...')
api = generate_api('queries.sql', 'psycopg2')
api.my_method(db, 'arg1', 'arg2')
```

If *target* is specified, methods are injected into the given object (which is also returned from `generate_api`):
```python
db = psycopg2.connect('...')
generate_api('queries.sql', 'psycopg2', db, target=db)
db.my_method('arg1', 'arg2')
```

*extension* (by default `.sql`) specifies which files are loaded from the queries directory.

*namespace_mode* controls how hierarchy of files is converted into hierarchy of objects when constructing the API class. There are 3 modes supported:

* `dirs` (the default), which maps each subdirectory to a nested method namespace ignoring file names:

| path under query dir | function definition | resulting API    |
|----------------------|---------------------|------------------|
| `root.sql`           | `-- def a(): ...`   | `api.a()`        |
| `subdir/foo.sql`     | `-- def b(): ...`   | `api.subdir.b()` |
| `subdir/bar.sql`     | `-- def c(): ...`   | `api.subdir.c()` |

* `files` which uses file names (after stripping the extension) as an extra nesting level:

| path under query dir | function          | resulting API        |
|----------------------|-------------------|----------------------|
| `root.sql`           | `-- def a(): ...` | `api.root.a()`       |
| `subdir/foo.sql`     | `-- def b(): ...` | `api.subdir.foo.b()` |
| `subdir/bar.sql`     | `-- def c(): ...` | `api.subdir.bar.c()` |

In this mode, *namespace_root* allows to specify a special file name which circumvents this behavior, allowing to mimic how Python handles module namespaces. For example, when *namespace_root* = `"__init__"` (the default):

| path under query dir  | function          | resulting API        |
|-----------------------|-------------------|----------------------|
| `__init__.sql`        | `-- def a(): ...` | `api.a()`            |
| `foo.sql`             | `-- def b(): ...` | `api.foo.b()`        |
| `subdir/__init__.sql` | `-- def c(): ...` | `api.subdir.c()`     |
| `subdir/bar.sql`      | `-- def d(): ...` | `api.subdir.bar.d()` |

* `flat` mode which ignores hierarchy:

| path under query dir | function          | resulting API |
|----------------------|-------------------|---------------|
| `root.sql`           | `-- def a(): ...` | `api.a()`     |
| `subdir/foo.sql`     | `-- def b(): ...` | `api.b()`     |
| `subdir/bar.sql`     | `-- def c(): ...` | `api.c()`     |

### Query annotations

Each query managed by **aesqlapius** must be preceded with a `-- ` (SQL comment) followed by a Python-style function definition:

```sql
-- def function_name(parameters, ...) -> return_type: ...
...some SQL code...
```

#### Parameters

Parameters allow optional literal default values and optional type annotations (which are currently ignored) and may be specified in both positional, keyword or mixed style in the resulting API:

```sql
-- def myfunc(foo, bar: str, baz=123) -> None: ...`
...some SQL code...
```
```pyton
api.myfunc(1, bar="sometext")  # foo=1, bar="sometext", baz=123
```

#### Return value

Return value annotation is required and may either be `None` (when query does not return anything) or a nested type annotation with specific structure `RowsFormat[RowFormat]`.

Outer `RowsFormat` specifies how multiple rows returned by the query are handled. Allowed values are:
* `Iterator[RowFormat]` - return a row iterator.
* `List[RowFormat]` - return a list of rows.
* `Single[RowFormat]` - return a single row.
* `Dict[KeyColumn, RowFormat]` - return a dictionary of rows. The column to be used as a dictionary key is specified in the first argument, e.g. `Dict[0, ...]` uses first returned column as key and `Dict['colname', ...] uses column named *colname*. Precede column index or name with unary minus to make it removed from the row contents.

Inner `RowFormat` specifies how data for each row is presented:
* `Tuple` - return row as a tuple of values.
* `List` - return row as a list of values.
* `Dict` - return row as a dict, where keys are set to the column names returned by the query.
* arbitrary type - TODO

Examples:
```sql
-- def example1() -> List[Tuple]: ...
SELECT 1, 'foo' UNION SELECT 2, 'bar';
-- def example2() -> Single[Tuple]: ...
SELECT 1, 'foo';
-- def example3() -> Iterator[Dict]: ...
SELECT 1 AS n, 'foo' AS s UNION SELECT 2 AS n, 'bar' AS s;
-- def example4() -> Dict['key', Dict]: ...
SELECT 'foo' AS key, 1 AS a, 2 AS b;
-- def example5() -> Dict[-'key', Dict]: ...
SELECT 'foo' AS key, 1 AS a, 2 AS b;
```
```
>>> api.example1()
[(1, 'foo'), (2, 'bar')]
>>> api.example2()
(1, 'foo')
>>> it = api.example3()
>>> next(it)
{'n': 1, 's': 'foo'}
>>> next(it)
{'n': 2, 's': 'bar'}
>>> api.example4()
{'foo': {'key': 'foo', 'a': 1, 'b': 2}}
>>> api.example5()
{'foo': {'a': 1, 'b': 2}}
```

#### Body

Function body is required to contain a single ellipsis.

## License

MIT license, copyright (c) 2020 Dmitry Marakasov amdmi3@amdmi3.ru.
