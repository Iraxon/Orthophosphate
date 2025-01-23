import os.path

import src.orthophosphate.compiler.compiler as compiler
import src.orthophosphate.compiler.datapack_generator.datapack_directory_management as ddm

TEST_SRC_PATH = os.path.join(os.path.abspath("."), "src", "orthophosphate", "compiler", "test_src_files")

def compile_test_src(name: str, nameIncludesExtension: bool = False) -> ddm.FolderRep:
    """
    Name should not include the .opo4 extension unless
    specified by boolean arg
    """
    return compiler.pure_function_compile(
            os.path.join(TEST_SRC_PATH, name + (".opo4" if not nameIncludesExtension else ""))
        )

def compile_hello_world() -> ddm.FolderRep:
    return compile_test_src("hello_world")

def compile_all() -> tuple[ddm.FolderRep, ...]:
    return tuple(
        compile_test_src(name, nameIncludesExtension=True) for name in os.listdir(TEST_SRC_PATH)
    )

def test_types():
    for item in compile_all():
        assert isinstance(
            item,
            ddm.FolderRep
        )
