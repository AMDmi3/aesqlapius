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

from typing import Any, Callable, List, TYPE_CHECKING


class Namespace:
    if TYPE_CHECKING:
        def __getattr__(self, name: str) -> Any:  # pragma: no cover
            pass  # pragma: no cover


def inject_method(root: Any, namespace_path: List[str], method: Callable[..., Any]) -> None:
    target = root

    for name in namespace_path[:-1]:
        if not hasattr(target, name):
            setattr(target, name, Namespace())
        target = getattr(target, name)
        if not isinstance(target, Namespace):
            raise ValueError(f"Intermediate namespace element '{name}' is not a namespace")

    if hasattr(target, namespace_path[-1]):
        raise ValueError(f"Target method '{namespace_path[-1]}' already exists in the namespace")

    setattr(target, namespace_path[-1], method)
