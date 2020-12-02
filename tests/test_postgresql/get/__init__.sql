-- def nothing() -> None: ...
SELECT;

-- def single_dict() -> Single[Dict]: ...
SELECT 0 AS a, 'a' AS b;

-- def single_list() -> Single[List]: ...
SELECT 0 AS a, 'a' AS b;

-- def single_tuple() -> Single[Tuple]: ...
SELECT 0 AS a, 'a' AS b;

-- def single_single() -> Single[Single]: ...
SELECT 0 AS a;

-- def iterator_dict() -> Iterator[Dict]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def iterator_list() -> Iterator[List]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def iterator_tuple() -> Iterator[Tuple]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def iterator_single() -> Iterator[Single]: ...
SELECT a FROM generate_series(0, 2) a;

-- def list_dict() -> List[Dict]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def list_list() -> List[List]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def list_tuple() -> List[Tuple]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def list_single() -> List[Single]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def dict_of_tuples_by_column_name() -> Dict['a', Tuple]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def dict_of_tuples_by_column_index() -> Dict[0, Tuple]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def dict_of_tuples_by_column_name_removed_key() -> Dict[-'a', Tuple]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def dict_of_tuples_by_column_index_removed_key() -> Dict[-0, Tuple]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def dict_of_tuples_by_column_name_out_of_range() -> Dict['z', Tuple]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;

-- def dict_of_tuples_by_column_index_out_of_range() -> Dict[3, Tuple]: ...
SELECT a, chr(ascii('a') + a) AS b FROM generate_series(0, 2) a;
