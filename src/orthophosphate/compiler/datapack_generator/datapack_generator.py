import json
from dataclasses import dataclass
from os import makedirs
from os.path import dirname, join

from ..parser.term_graph import FunctionCallTerm, ProgramTerm, file


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
        },
        indent=2,
    )
    ast_evaled = ast.eval_default()
    print(ast_evaled.display_node())
    for tle in ast_evaled.top_level_exprs:
        assert isinstance(tle, FunctionCallTerm)
        if tle.head == file:
            args = tle.args
            assert len(args) == 2
            files[args[0].render_contents()[0]] = args[1].render_contents()[0]
        else:
            raise ValueError(f"Could not understand top-level term:\n{tle}")
    return DataPack(files)


def write_to_files(pack: DataPack, target_path: str | None) -> None:
    for path, content in pack.files.items():
        if target_path is None:
            print(f"File at path {path}")
            print(content)
            print("---------")
        else:

            full_path = join(target_path, path)

            makedirs(dirname(full_path), exist_ok=True)

            with open(full_path, "w") as f:
                f.write(content)
