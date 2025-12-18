import os

from ..parser.abstract_syntax_tree import Node, PackRoot

type DataPack = dict[str, Node]


def generate_datapack(ast: PackRoot, pack_name: str) -> DataPack:
    raise NotImplementedError


def write_to_files(pack: DataPack, target_path: str | None) -> None:
    raise NotImplementedError
