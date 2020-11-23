import os
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

from aesqlapius.query import Query, parse_query_file


@dataclass
class QueryDirEntry:
    namespace_path: List[str]
    filesystem_path: str


def _walk_dir_tree(path: str, extension: str, namespace_path: Optional[List[str]] = None) -> Iterator[QueryDirEntry]:
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                yield from _walk_dir_path(
                    os.path.join(path, entry.name),
                    extension,
                    (namespace_path or []) + [entry.name]
                )
            elif entry.is_file() and entry.name.endswith(extension):
                yield QueryDirEntry(
                    (namespace_path or []) + [entry.name.removesuffix(extension)],
                    os.path.join(path, entry.name)
                )


def iter_query_dir(path: str, extension: str) -> Iterator[Tuple[QueryDirEntry, List[Query]]]:
    for entry in _walk_dir_tree(path, extension):
        yield (entry, parse_query_file(entry.filesystem_path))
