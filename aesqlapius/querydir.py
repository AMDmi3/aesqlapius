# Copyright (c) 2020 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
                yield from _walk_dir_tree(
                    os.path.join(path, entry.name),
                    extension,
                    (namespace_path or []) + [entry.name]
                )
            elif entry.is_file() and entry.name.endswith(extension):
                yield QueryDirEntry(
                    (namespace_path or []) + [entry.name.removesuffix(extension)],
                    os.path.join(path, entry.name)
                )


def iter_queries(path: str, extension: str) -> Iterator[Tuple[QueryDirEntry, List[Query]]]:
    if os.path.isdir(path):
        for entry in _walk_dir_tree(path, extension):
            yield (entry, parse_query_file(entry.filesystem_path))
    else:
        entry = QueryDirEntry(
            [str(os.path.basename(path)).removesuffix(extension)],
            path
        )
        yield (entry, parse_query_file(path))
