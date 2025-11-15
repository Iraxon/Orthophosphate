import enum
import functools
import os
import string

from ..parser.abstract_syntax_tree import *

class MCVersion(enum.Enum):
    V1d20d1 = enum.auto()
    VDefault = V1d20d1

    def render(self) -> str:
        return self.name.replace("d", ".").replace("V", "")

type DataPack = dict[Path, Node]
type Path = str | os.PathLike

def realize(pack: DataPack, root: Path) -> None:
        for path, content in pack.items():
            with open(os.path.join(root, path), "x") as osFile:
                osFile.write(str(content))

def renderPack(input: DataPack) -> str:
    return "\n\n---\n\n".join(
        hanging_indent(f"{path}\n{str(content)}")
        for path, content in input.items()
    )

def merge(pack: DataPack, path: Path, content: Node) -> DataPack:
    output_copy = pack.copy()
    if path not in pack.keys():
        output_copy[path] = content
        return output_copy
    output_copy[path] = resolve_conflict(output_copy[path], content)
    return output_copy

def resolve_conflict[T: Node](existing: T, new: T) -> T:
    raise NotImplementedError

def hanging_indent(s: str) -> str:
        return "\n    ".join(s.splitlines())

@functools.cache
def namespace_from_str(name: str) -> str:
    """
    Converts an arbitrarily-formatted
    datapack name into a suitable namespace
    by removing special characters and
    lowercasing it
    """
    return "".join(
        (
            char
            if char != " "
            else "_"
            # Convert spaces to underscores
        )
        for char in name
        if (
            char in string.ascii_letters or char in string.digits or char in ("_", "-", ".", " ")
            # Omit chars that aren't legal Minecraft resource location characters or space
        )
    ).lower() # Lowercase capitals
