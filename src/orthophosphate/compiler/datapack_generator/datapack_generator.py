from dataclasses import dataclass
import json
from ..parser.term_graph import Term, ProgramTerm


@dataclass(frozen=True)
class DataPack:
    files: dict[str, str]
    """
    Mapping of file paths to contents
    """


def generate_datapack(ast: ProgramTerm, pack_name: str) -> DataPack:
    files: dict[str, str] = {}
    files["pack.mcmeta"] = json.dumps(
        {
            "pack": {
                "description": "Built with Orthophosphate",
                "pack_format": 15,  # 1.20.1
            }
        }
    )
    return DataPack(files)


def write_to_files(pack: DataPack, target_path: str | None) -> None:
    raise NotImplementedError
