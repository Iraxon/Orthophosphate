from dataclasses import dataclass
import json
from ..parser.term_graph import FunctionCallTerm, ReferenceTerm, ProgramTerm


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
    for child in ast.top_level_exprs:
        assert isinstance(child, FunctionCallTerm)
        if child.head == ReferenceTerm("file"):
            args = child.args
            assert len(args) == 2
            files[args[0].render_contents()[0]] = args[1].render_contents()[0]
        else:
            raise ValueError(f"Could not understand top-level term:\n{child}")
    return DataPack(files)


def write_to_files(pack: DataPack, target_path: str | None) -> None:
    for path, content in pack.files.items():
        if target_path is None:
            print(f"File at path {path}")
            print(content)
            print("---------")
        else:
            # with open(path.join(target_path, path), "x") as f:
            #     f.write(content)
            # Commented out because it is untested
            raise NotImplementedError
