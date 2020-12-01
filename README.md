# aeSQLAPIus

![CI](https://github.com/AMDmi3/aesqlapius/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/AMDmi3/aesqlapius/branch/master/graph/badge.svg?token=87aZsxlja2)](https://codecov.io/gh/AMDmi3/aesqlapius)

## Summary

So you don't want to use ORM, and want to organize your SQL queries
in a convenient way. Don't mix them with your python code, don't
write `execute` and `fetchrow`s by hand for each query. With
**aesqlapius**:

- Store your SQL queries separate from the code, in a dedicated
  file (TODO) or directory hierarchy
- Annotate each query with python-like function definition specifying
  input arguments and output types and patterns

**aesqlapius** builds a class out of this, where you can call your
queries as plain methods. It handles arguments (pass positional
or keyword arguments as you like, default values are also handled) and
output types and patterns (you may specify whether a method returns
iterator, list, dict (TODO) of rows, or a single row, where row may
be represented as a tuple, list, dict, single value or a custom
type such as a dataclass).

## Example

queries.sql:
```sql
-- def add_city(name, population = None) -> None: ...
INSERT INTO cities VALUES (%(name)s, %(population)s);

-- def list_cities() -> List[Scalar]: ...  # TODO: Scalar doesn't work yet
SELECT name FROM cities ORDER BY name;

-- def get_population(city: str) -> Single[Scalar]: ...  # TODO: Scalar doesn't work yet
SELECT population FROM cities WHERE name = %(city)s;

-- def get_city(city: str) -> Single[City]: ...
SELECT * FROM cities WHERE name = %(city)s;
```

script.py:
```python
from aesqlapius.apis.psycopg2 import generate_api

db = psycopg2.connect('...')
api = generate_api('queries.sql', db)

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

TODO

### Query directory organization

TODO

### Query annotations

TODO

## License

MIT license, copyright (c) 2020 Dmitry Marakasov amdmi3@amdmi3.ru.
