import os
from typing import Any

type DataPack = dict[str, Any] # Correct later


def generate_datapack(ast, pack_name: str) -> DataPack:
    raise NotImplementedError


def write_to_files(pack: DataPack, target_path: str | None) -> None:
    raise NotImplementedError
