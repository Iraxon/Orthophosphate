import os.path

import src.orthophosphate.compiler.compiler as compiler
import src.orthophosphate.compiler.datapack_generator.datapack_directory_management as ddm

def compile_hello_world() -> ddm.FolderRep:
    return compiler.pure_function_compile(
            os.path.join(os.path.abspath("."), "src", "orthophosphate", "compiler", "test_src_files", "hello_world.opo4")
        )

def test_compiler():
    assert isinstance(
        compile_hello_world(),
        ddm.FolderRep
    )
