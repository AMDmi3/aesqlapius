-- def ping() -> Single[Dict]: ...
SELECT TRUE AS pong;

-- def swap_args(a: int = 0, b: str = 'a') -> Single[Tuple]: ...
SELECT %(b)s AS a, %(a)s AS b;