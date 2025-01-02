import random
import typing
from .datapack_directory_management import FolderRep, FileRep, datapack_directory, namespacify, frozenset_, namespace_directory

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
    
    return FileRep(ast.value[0].value + ".mcfunction", "\n".join(command_list))

def generate_namespace(ast, arg_namespace: typing.Optional[str] = None) -> tuple[FolderRep, tuple[str], tuple[str]]:
    if ast.value[0].type == "placeholder" and ast.value[0].value == "default_namespace":
        namespace = arg_namespace
    else:
        namespace = ast.value[0].value # The first item in the block attached to the
        # namespace is the name
    
    func_list = [] # list of ("name", "contents") tuples

    # These two just contain function names;
    # full function data goes in func_list
    tick_functions = []
    load_functions = []

    for statement in ast.value[1].value:
        for item in statement.value:
            match (item.type, item.value, item.data_type):
                case ("func_def" | "tick_func_def" as def_type, _, _):
                    func_list.append(compile_function(item))
                    if def_type == "tick_func_def":
                        tick_functions.append(item.value[0].value)
                        # The name of the function
                case ("namespace", v, dt):
                    raise ValueError(f"Nesting namespaces is not permitted")
                case _:
                    raise ValueError(f"Namespace generator does not recognize this:\n{item}")
    
    return (
        namespace_directory(
            namespace=namespace,
            functions=frozenset(func_list),
            function_tags=frozenset() # to be supported
        ),
        tuple(tick_functions),
        tuple(load_functions)
    )

def generate_datapack(ast, name: typing.Optional[str]=None, in_secondary_namespace=None) -> FolderRep:
    """
    Generates a FolderRep of the entire datapack from a
    post-parsed AST
    """

    namespace = namespacify(name) if name is not None else "unnamed_datapack_" + str(random.randint(0, 99999))

    if name is None:
        name = "Unnamed Datapack " + str(random.randint(0, 99999))
    
    namespace_folders = []
    tick_functions = tuple()
    load_functions = tuple()

    for statement in ast.value:
        for item in statement.value: # The root node always has statements as its children;
            # we are interested in those, not the statements themselves

            match (item.type, item.value, item.data_type):
                case ("namespace", v, dt):
                    next_namespace, new_tick_functions, new_load_functions = generate_namespace(item, arg_namespace=namespace)
                    namespace_folders.append(next_namespace)
                    tick_functions += new_tick_functions
                    load_functions += new_load_functions
                case _:
                    raise ValueError(
                        f"Datapack generator does not recognize this\n"
                        f"as a permitted top-level item:\n"
                        f"{item}"
                    )
    
    return datapack_directory(
        name=name,
        tick_functions=frozenset(tick_functions),
        load_functions=frozenset(load_functions),
        namespace_folders=frozenset(namespace_folders)
    )