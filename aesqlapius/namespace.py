from typing import Any, Callable, List


class Namespace:
    pass


def inject_method(root: Namespace, namespace_path: List[str], method: Callable[..., Any]) -> None:
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
