import dataclasses
from .abstract_syntax_tree import *

@dataclasses.dataclass
class ParseState:
    """
    Stores the current state of the parser, including
    cursor position
    """
    tokens: typing.Sequence[Token]
    cursor: int = 0

    def next_token(self) -> Token:
        r_val = self.tokens[self.cursor]
        self.skip()
        return r_val

    def skip(self) -> None:
        self.cursor += 1

    def peek(self, i: int = 0) -> Token:
        return self.tokens[self.cursor + i]

    def in_range(self) -> bool:
        return 0 <= self.cursor < len(self.tokens)

    def token_str(self, n: int = 0) -> str:
        """
        Returns a str representation of the token at the
        provided (default 0) offset from the cursor unless
        it would cause an index error, in which case "" is returned
        """
        return str(self.peek(n)) if (self.cursor + n >= 0 and self.cursor + n < len(self.tokens)) else ""

    def error_readout(self, i: int = -1) -> str:
        """
        Returns a str displaying the tokens near the cursor, with a ' <<< HERE ' arrow
        pointing to the last token grabbed (this method is to be used when making error messages)
        """
        return f"".join(
            tuple(
                f"\t{self.token_str(n)}{' <<< HERE' if n == i else ''}\n" for n in range(-20, 10)
            )
        )

    def bind_name[T](self, name: str, value: Ref[T], type: type[T], allow_overwrite: bool = False) -> None:
        env = self._ref_dict(type)
        if (not allow_overwrite and name in env.keys()):
            err(self, f"{name} cannot be defined because it is already bound:")
        env[name] = value

    def checkref[T](self, name: str, type: type[T]) -> None:
        self.get_ref(name, type)

    def get_ref[T](self, name: str, type: type[T]) -> Ref[T]:
        value = self._ref_dict(type).get(name)
        if value is None:
            err(self, "Unknown function:")
        return value


    def _ref_dict[T](self, type: type[T]) -> dict[str, Ref[T]]:
        """
        Returns the dict of name bindings for the provided type,
        creating a new one if necessary
        """
        if type not in self._ref_dict_cache.keys():
            self._ref_dict_cache[type] = dict()
        return self._ref_dict_cache[type]

    _ref_dict_cache: dict[type, dict[str, Ref]] = dict()

def err(state: ParseState, message: str | None = None) -> typing.Never:
    """
    Raises a ValueError with the provided message
    (or a default "Invalid token" message) and the
    token display from state.error_readout()
    """
    raise ValueError(f"{f'Invalid token {state.peek(-1)} at:' if message is None else message}\n{state.error_readout()}")
