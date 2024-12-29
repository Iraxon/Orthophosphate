import random
from .datapack_directory_management import FolderRep, FileRep, datapack_directory, namespacify, frozenset_

def compile_function(ast) -> FileRep:
    """
    Function for parsing Orthophosphate functions
    """
    command_list = []
    for line in ast.value[1].value[0].value: # for the content of each statement node in the block node child of the function def
        match (line.type, line.value, line.data_type):
            case ("literal_value", cmd, "cmd"):
                command_list.append(line.value)
            case _:
                raise ValueError(f"Datapack function generator does not recognize this:\n{line}")
    
    return FileRep(ast.value[0].value, "\n".join(command_list))

def generate_datapack(ast, name=None) -> FolderRep:
    """
    Generates a FolderRep of the entire datapack from a
    post-parsed AST
    """

    if name is None:
        name = "Unnamed Datapack " + str(random.randint(0, 99999))

    func_list = [] # list of ("name", "contents") tuples
    # that will be used to make function files
    tick_functions = []

    for statement in ast.value:
        for item in statement.value: # The root node always has statements as its children;
            # we are interested in those, not the statements themselves

            match (item.type, item.value, item.data_type):
                case ("func_def" | "tick_func_def" as def_type, _, _):
                    func_list.append(compile_function(item))
                    if def_type == "tick_func_def":
                        tick_functions.append(item.value[0].value)
                case _:
                    pass
                    # raise ValueError(f"Datapack generator does not recognize this:\n{item}")

    print(
        name,
        namespacify(name),
        frozenset(func_list),
        frozenset(tick_functions),
        frozenset_()
    )
    return datapack_directory(
        name=name,
        namespace=namespacify(name),
        functions=frozenset(func_list),
        tick_functions=frozenset(tick_functions),
        load_functions=frozenset_()

    )