import typing

class Token(typing.NamedTuple):
    type: str
    value: str

    def __repr__(self):
        return f"Token(type={self.type!r}, value={self.value!r})"