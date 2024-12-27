import typing
from enum import Enum

class PrimitiveVariableType(Enum):
    STRING = 1
    INTEGER = 1

class PrimitiveVariable(typing.NamedTuple):
    type: PrimitiveVariableType
    
    #keep in mind that variables are represented as scoreboards. This means that a primitive variable is typically only one scoreboard which has to be represented as an integer
    value: int

    def __repr__(self):
        return f"Token(type={self.type!r}, value={self.value!r})"

    

