import random
import typing
from .datapack_directory_management import FolderRep, FileRep, datapack_directory, namespacify, frozenset_, namespace_directory

def compile_function(ast) -> FileRep:
    """
    Function for parsing Orthophosphate functions
    """
    command_list = []
    for statement in ast.value[1].value:
        for line in statement.value:
            match (line.type, line.value, line.data_type):
                case ("literal_value", _ as cmd, "cmd"):
                    command_list.append(cmd)
                case ("obj_def", _ as obj_tuple, _):
                    command_list.append(f"scoreboard objectives add {obj_tuple[0].value} dummy")
                case ("scoreboard_operation", _ as contents, _):
                    targ_name = contents[0].value
                    targ_obj = contents[1].value
                    operation = contents[2].value
                    if len(contents) == 5:
                        source_name = contents[3].value
                        source_obj = contents[4].value
                    else:
                        constant_node = contents[3]
                        source_name = "C" + str(constant_node.value[0].value) # Looking in the int literal node that is in the constant node
                        source_obj = "opo4.constants"
                        # If we are using a constant, we guarantee the existence of the constant
                        # No issues arise if the obj or value already exist
                        command_list.append("scoreboard objectives add opo4.constants dummy")
                        command_list.append(
                            f"scoreboard players set "
                            f"{source_name} opo4.constants {constant_node.value[0].value}"
                        )
                    command_list.append(
                        f"scoreboard players operation "
                        f"{targ_name} {targ_obj} "
                        f"{operation} "
                        f"{source_name} {source_obj}"
                    )
                case _:
                    raise ValueError(f"Datapack function generator does not recognize this:\n{line}")
    
    return FileRep(ast.value[0].value + ".mcfunction", "\n".join(command_list))

def generate_namespace(ast, arg_namespace: typing.Optional[str] = None) -> tuple[FolderRep, tuple[str], tuple[str]]:
    """
    The ast parameter is a namespace statement

    This function returns a FolderRep of the namespace folder and tuples for tick and load functions
    """
    if ast.value[0].type == "placeholder" and ast.value[0].value == "default_namespace":
        if arg_namespace is None:
            raise ValueError(f"No namespace provided to fill placeholder")
        namespace = arg_namespace
    else:
        namespace = ast.value[0].value # The first item in the block attached to the
        # namespace is the name
    
    func_list = [] # list of ("name", "contents") tuples

    # These two just contain function names;
    # full function data goes in func_list
    tick_functions = []
    load_functions = []

    for item in ast.value[1].value: # in the block attached to the namespace keyword
        match (item.type, item.value, item.data_type):
            case ("func_def" | "tick_func_def" as def_type, _, _):
                func_list.append(compile_function(item))
                if def_type == "tick_func_def":
                    tick_functions.append(item.value[0].value)
                    # The name of the function
            case ("namespace", _, _):
                raise ValueError(f"Nesting namespaces is not permitted")
            case ("statement", _, _):
                raise ValueError(f"Unexpected statement:\n{item}")
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

    if name is None:
        name = (
            "Unnamed Datapack "
            + " ".join(tuple(
                "".join(tuple(
                    str(random.randint(0, 9))
                    for _ in range(4)
                ))
                for _ in range(2)
            ))
        )
    namespace = namespacify(name)
    
    namespace_folders = []
    tick_functions = tuple()
    load_functions = tuple()

    for item in ast.value:

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