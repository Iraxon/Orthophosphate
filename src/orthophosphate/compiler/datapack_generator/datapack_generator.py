import os

from ..parser.abstract_syntax_tree import Node, PackRoot

type DataPack = dict[Path, Node]
type Path = str | os.PathLike

def generate_datapack(ast: PackRoot, pack_name: str) -> DataPack:
    raise NotImplementedError

def write_to_files(pack: DataPack, target: Path) -> None:
    raise NotImplementedError
