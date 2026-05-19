from collections.abc import Callable


def inline_print[T](
    x: T, prefix: str = "", print_msg: Callable[[T], str] | str = str
) -> T:
    print(f"{prefix}{print_msg(x) if callable(print_msg) else print_msg}")
    return x
