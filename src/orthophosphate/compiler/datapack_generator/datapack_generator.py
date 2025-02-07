import random
import typing

from ..parser.abstract_syntax_tree import Node, NodeType
from .datapack_directory_management import FolderRep, FileRep, datapack_directory, namespacify, frozenset_, namespace_directory

def _compile_line(command_list: list[str], statement: Node, namespace: str, cursor=0, exec_pre = "") -> tuple[list[str], int]:
    """
    Private function: Compiles a single node into its corresponding commands;
    it operates recursively on constructions involving blocks of statements

    exec_pre appends should always begin with `execute` and end with `run ` (WITH THE SPACE).
    Chained exec_pre output will look like `execute ... run execute ... run execute ... run <cmd>`
    """

    def add_to_cmd_list(cmd: str) -> None:
        command_list.append(exec_pre + cmd)

    assert isinstance(statement.value, tuple)
    for line in statement.value:
        assert isinstance(line, Node)
        match (line.type, line.value, line.data_type):
            case (NodeType.LITERAL_VALUE, cmd, "cmd"):
                assert isinstance(cmd, str)
                add_to_cmd_list(cmd)

            case (NodeType.CONCAT, contents, _):
                assert isinstance(contents, tuple)
                literal, block_or_statement = contents

                assert isinstance(literal.value, str)
                concat_statement = f"execute {literal.value.strip()} run "

                if block_or_statement.type == NodeType.STATEMENT:
                    command_list, cursor = _compile_line()

                elif block_or_statement.type == NodeType.BLOCK:
                    assert isinstance(block_or_statement.value, tuple)

                    for inner_Line in block_or_statement.value:
                        command_list, cursor = _compile_line(
                            command_list, inner_Line, namespace, cursor, exec_pre + concat_statement
                        )
                else:
                    raise ValueError(
                        f"Unexpected children of CONCAT node:\n{block_or_statement}"
                    )

            case (NodeType.OBJ_DEF, obj_tuple, _):
                assert isinstance(obj_tuple, tuple)
                add_to_cmd_list(f"scoreboard objectives add {obj_tuple[0].value} dummy")

            case (NodeType.SCOREBOARD_OPERATION, contents, _):
                assert isinstance(contents, tuple)
                targ_name = contents[0].value
                targ_obj = contents[1].value
                operation = contents[2].value if contents[2].value not in ("<==", ">==") else contents[2].value[0]

                if operation not in ("=", "+=", "-=", "*=", "/=", "%=", "<==", ">==", "><"):
                    raise ValueError(f"Unsupported scoreboard operation: {operation}")

                if len(contents) == 5:
                    source_name = contents[3].value
                    source_obj = contents[4].value
                else:
                    constant_node = contents[3]
                    source_name = "C" + str(constant_node.value[0].value) # Looking in the int literal node that is in the constant node
                    source_obj = "opo4.constants"
                    # If we are using a constant, we guarantee the existence of the constant
                    # No issues arise if the obj or value already exist
                    add_to_cmd_list("scoreboard objectives add opo4.constants dummy")
                    add_to_cmd_list(
                        f"scoreboard players set "
                        f"{source_name} opo4.constants {constant_node.value[0].value}"
                    )
                add_to_cmd_list(
                    f"scoreboard players operation "
                    f"{targ_name} {targ_obj} "
                    f"{operation} "
                    f"{source_name} {source_obj}"
                )
            case (NodeType.SCOREBOARD_RESET, contents, _):
                assert isinstance(contents, tuple)
                name, obj = contents
                add_to_cmd_list(f"scoreboard players reset {name.value} {obj.value}")
            case (NodeType.AFTER, contents, _):
                raise ValueError(f"After statements are currently not supported")
                assert isinstance(contents, tuple)
                times, block = contents
                add_to_cmd_list(f"scoreboard objectives add opo4.after_timers dummy")
                add_to_cmd_list(
                    f"execute unless score $after{hash(contents)} opo4.after_timers = $after{hash(contents)} opo4.after_timers "
                    f"scoreboard players $after{hash(contents)} opo4.after_timers set 0"
                )
                for inner_line in block.value:
                    command_list, cursor = _compile_line(
                        command_list=command_list,
                        statement=inner_line,
                        namespace=namespace,
                        cursor=cursor,
                        exec_pre=f"execute if score $after{hash(contents)} opo4.after_timers matches {times.value} run "
                    )
                add_to_cmd_list(
                    f"execute if score $after{hash(contents)} opo4.after_timers matches ..{times.value} run "
                    f"scoreboard players add $after{hash(contents)} opo4.after_timers 1"
                )
            case (NodeType.CALL, contents, _):
                assert isinstance(contents, tuple)
                function = contents[0]
                add_to_cmd_list(f"function {namespace}:{function.value}")
            case _:
                raise ValueError(f"Datapack function generator does not recognize this:\n{line}")
    return command_list, cursor

def compile_function(ast: Node, namespace: str) -> FileRep:
    """
    Takes a function node and
    returns the mcfunction FileRep
    """
    assert isinstance(ast.value, tuple)

    command_list: list[str] = []
    cursor: int = 0
    for statement in ast.value[1].value:
        command_list, cursor = _compile_line(command_list, statement, namespace, cursor)

    return FileRep(ast.value[0].value + ".mcfunction", "\n".join(command_list))

def generate_namespace(ast: Node, arg_namespace: str | None = None) -> tuple[FolderRep, tuple[str, ...], tuple[str, ...]]:
    """
    The ast parameter is a namespace statement

    This function returns a FolderRep of the namespace folder and tuples for tick and load functions
    """
    assert isinstance(ast.value, tuple)

    if ast.value[0].type == "placeholder" and ast.value[0].value == "default_namespace":
        if arg_namespace is None:
            raise ValueError(f"No namespace provided to fill placeholder")
        namespace = arg_namespace
    else:
        namespace = ast.value[0].value # The first item in the tuple attached to the
        # namespace is the name

    func_list: list[FileRep] = []

    # These two just contain function names;
    # full function data goes in func_list
    tick_functions: list[str] = []
    load_functions: list[str] = []

    block_nodes = ast.value[1].value
    assert isinstance(block_nodes, tuple)

    for item in block_nodes:
        match (item.type, item.value, item.data_type):
            case ("func_def" | "tick_func_def" as def_type, _, _):
                func_list.append(compile_function(item, namespace))
                if def_type == "tick_func_def":
                    tick_functions.append(item.value[0].value)
                    # The name of the function
            case ("namespace", _, _):
                raise ValueError(f"Nesting namespaces is not permitted")
            case ("statement", _, _):
                raise ValueError(f"Node incorrectly encased in statement; check Node.check_statement method:\n{item}")
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

def generate_datapack(ast: Node, name: typing.Optional[str]=None, in_secondary_namespace=None) -> FolderRep:
    """
    Generates a FolderRep of the entire datapack from a
    post-parsed AST
    """
    assert isinstance(ast.value, tuple)

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
    tick_functions: tuple[str, ...] = tuple()
    load_functions: tuple[str, ...] = tuple()

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
