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

from contextlib import AsyncExitStack
from typing import Any, AsyncIterator, Callable, Dict

import aiopg

from aesqlapius.asyncmethod import (
    AbstractDriverDetail,
    generate_method_generic
)
from aesqlapius.hook import QueryHook
from aesqlapius.query import Query


class AiopgDetail(AbstractDriverDetail):
    async def yield_cursor(self, db: Any, **kwargs: Dict[str, Any]) -> AsyncIterator[Any]:
        async with AsyncExitStack() as stack:
            if isinstance(db, aiopg.Pool):
                db = await stack.enter_async_context(db.acquire())

            async with db.cursor() as cur:
                yield cur


def generate_method(query: Query, hook: QueryHook) -> Callable[..., Any]:
    return generate_method_generic(query, AiopgDetail(), hook)
