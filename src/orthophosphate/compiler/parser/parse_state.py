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
    _ref_dict_cache: dict[type, dict[str, Ref]] = dataclasses.field(default_factory=dict)

    def next_token(self) -> Token:
        """
        Returns the token under the cursor
        and increments the cursor
        """
        t = self.tokens[self.cursor]
        self.skip()
        return t

    def skip(self) -> None:
        """
        Increments the cursor
        """
        self.cursor += 1

    def reset(self) -> None:
        """
        Decrements the cursor,
        setting it back to where it was
        before the previous next_token()
        call
        """
        self.cursor -= 1

    def peek(self, i: int = 0) -> Token:
        """
        Returns the token at the provided
        offset from the cursor (zero by default)
        without changing the cursor
        """
        return self.tokens[self.cursor + i]

    def cursor_in_range(self) -> bool:
        return 0 <= self.cursor < len(self.tokens)

    def display_token(self, n: int = 0) -> str:
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
                f"\t{self.display_token(n)}{' <<< HERE' if n == i else ''}\n" for n in range(-20, 10)
            )
        )

    def bind_name[T](self, name: str, value: Ref[T], type: type[T], allow_overwrite: bool = False) -> None:
        env = self._ref_dict(type)
        if (not allow_overwrite and name in env.keys()):
            err(self, f"{name} cannot be defined because it is already bound:")
        env[name] = value

    def checkref[T](self, id: str, type: type[T]) -> str:
        """
        Throws an error if the provided
        id does not refer to a valid content
        item of the given type

        Returns the id unchanged
        """
        self.get_ref(id, type) # Using side effect
        return id

    def get_ref[T](self, id: str, type: type[T]) -> Ref[T]:
        """
        Returns a Ref object pointing to the content item
        of the provided type that has the provided id
        or throws an error if there is no such item
        """
        value = self._ref_dict(type).get(id)
        if value is None:
            err(self, "This is not a valid reference:")
        return value


    def _ref_dict[T](self, type: type[T]) -> dict[str, Ref[T]]:
        """
        Returns the dict of name bindings for the provided type,
        creating a new one if necessary
        """
        if type not in self._ref_dict_cache.keys():
            self._ref_dict_cache[type] = dict()
        return self._ref_dict_cache[type]

def err(state: ParseState, message: str | None = None) -> typing.Never:
    """
    Raises a ValueError with the provided message
    (or a default "Invalid token" message) and the
    token display from state.error_readout()
    """
    raise ValueError(f"{f'Invalid token {state.peek(-1)} at:' if message is None else message}\n{state.error_readout()}")
