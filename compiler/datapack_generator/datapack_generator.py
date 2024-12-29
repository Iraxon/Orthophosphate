import os
from .datapack_directory_management import FolderRep, FileRep, datapack_directory, namespacify, frozenset_

def compile_function(ast, src_file_path) -> FileRep:
    """
    Function for parsing Orthophosphate functions
    """
    command_list = []
    for item in ast.value[1]:
        match (item.type, item.value, item.data_type):
            case ("literal_value", cmd, "cmd"):
                pass
            case _:
                raise ValueError(f"Datapack function generator does not recognize this:\n{item}")

    raise NotImplementedError

def generate_datapack(ast, src_file_path="") -> FolderRep:
    """
    Generates a FolderRep of the entire datapack from a
    post-parsed AST
    """
    name = (os.path.split(src_file_path)[1]).title()
    namespace = namespacify(name)

    func_list = [] # list of ("name", "contents") tuples
    # that will be used to make function files
    tick_functions = []

    for item in ast.value:
        match (item.type, item.value, item.data_type):
            case ("func_def" | "tick_func_def" as def_type, _, _):
                func_list.append(compile_function(item))
                if def_type == "tick_func_def":
                    tick_functions.append(item.value[0])
            case _:
                pass

    return datapack_directory(
        name=name,
        namespace=namespace,
        functions=frozenset(func_list),
        tick_functions=frozenset_(),
        load_functions=frozenset_()

    )