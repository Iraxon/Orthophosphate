import enum
import functools
import os
import re
import string
import typing

# NOT IMPLEMENTED YET
#
# class DefaultFolder(enum.StrEnum):
#     DATA = "data"
#     FUNCTION = "function"

DEFAULT_MC_META = """
{
  "pack": {
    "description": "Orthophosphate data pack",
    "pack_format": 18,
    "supported_formats": [18, 48]
  }
}
"""

def frozenset_(*args: typing.Any) -> frozenset:
    """
    Custom constructor for frozenset
    objects that takes multiple args

    > frozenset("like", "this")

    the built in one expects its
    arguments

    > frozenset(["like", "this"])
    """
    return frozenset([arg for arg in args])

class FileRep(typing.NamedTuple):
    """
    An immutable object representation
    of an individual file that can be
    realized
    """
    name: str
    content: str = ""

    def realize(self, directory: str) -> None:
        """
        Creates this file inside the specified
        directory; now that it exists, other
        parts of the code may add data
        """
        with open(os.path.join(directory, self.name), "x") as f:
            f.write(self.content)

    def __str__(self):
        return self.render()

    def render(self, pre="") -> str:
        """
        Not exactly incomprehensible but still
        not good for your sanity either
        """
        pre_len = len(pre)
        return(
            f"{"" if pre == "" else'═'} {self.name}"
            + f"\n{pre}{"".join(tuple('-' for _ in range(50 - pre_len) ))}\n"
            + f"{"".join(tuple(pre + str(i) + ' | ' + ln + "\n" for i, ln in enumerate(self.content.split("\n")) ))}"
            + f"{pre}{"".join(tuple('=' for _ in range(50 - pre_len) ))}"
            )

class FolderRep(typing.NamedTuple):
    """
    An immutable object representation
    of a folder that can be realized
    """
    name: str
    content: frozenset["FolderRep | FileRep"] = frozenset_()

    def realize(self, directory: str) -> None:
        """
        Creates this folder and its contents
        inside the specified directory
        """
        new_path = os.path.join(directory, self.name)
        os.makedirs(new_path, exist_ok=True)
        for item in self.content:
                item.realize(new_path)

    def __str__(self):
        return self.render()

    def render(self, pre="") -> str:
        """
        It's dark sorcery just like the AST one;
        do not touch if you value your sanity
        """
        line_tuple = tuple(
            element.render(pre + ("║ " if i < len(self.content) - 1 else "  "))
            if isinstance(element, (FolderRep, FileRep))
            else "═ " + str(element)
            for i, element in enumerate(self.content)
        ) if len(self.content) > 0 else tuple()
        # if len(self.content) > 1 else ("═ " + str(self.content),)

        return (
            f"{'' if pre == '' else'═ '}{self.name}"
            + (
                (
                    "\n" + "".join(
                        tuple(
                            f"{pre}╠{element}\n"
                            if i < len(line_tuple) - 1
                            else f"{pre}╚{element}"
                            for i, element in enumerate(line_tuple)
                        )
                    )
                ) if len(line_tuple) > 0 else ""
            )
        )

@functools.cache
def namespacify(name: str) -> str:
    """
    Converts an arbitrarily-formatted
    datapack name into a suitable namespace
    by removing special characters and
    lowercasing it
    """
    return "".join(
        (
            char
            if char != " "
            else "_"
            # Convert spaces to underscores
        )
        for char in name
        if (
            char in string.ascii_letters or char in string.digits or char in ("_", "-", ".", " ")
            # Omit chars that aren't legal Minecraft resource location characters or space
        )
    ).lower() # Lowercase capitals

@functools.cache
def tagify(set: frozenset[str], namespace: str, replace=False) -> str:
    """
    Takes a frozenset of strings
    and returns the JSON for
    a tag file
    """

    new_set = frozenset_(
        *(
            ((namespace + ":") if re.search(r"^.*:",item) is None else "") + item
            for i, item in enumerate(set)
        )
    )

    return (
        "{\n"
        + f"  \"replace\": {'true' if replace else 'false'},\n"
        + "  \"values\": [\n"
        + "".join(tuple(
            f"    \"{item}\"{',' if i != len(new_set) - 1 else ''}\n" for i, item in enumerate(new_set)
        ))
        + "  ]\n"
        + "}"
    )

def file_tagify(tag_name, set: frozenset[str], namespace, replace=False):
    """
    Like tagify, but it returns the whole FileRep instead
    """
    return (
        FileRep(
            name=tag_name,
            content=tagify(set, namespace, replace)
        )
    )

def namespace_directory(
        namespace: str,
        functions: frozenset[FileRep],
        function_tags: frozenset[FileRep] = frozenset()
) -> FolderRep:
    return (
        FolderRep(namespace, frozenset_(
                FolderRep("function", functions),
                FolderRep("structure", frozenset_()),
                FolderRep("tags", frozenset_(
                    FolderRep("function", function_tags)
                )),
                FolderRep("advancement", frozenset_()),
                FolderRep("banner_patern", frozenset_()),
                FolderRep("chat_type", frozenset_()),
                FolderRep("damage_type", frozenset_()),
                FolderRep("dimension", frozenset_()),
                FolderRep("dimension_type", frozenset_()),
                FolderRep("enchantment", frozenset_()),
                FolderRep("enchantment_provider", frozenset_()),
                FolderRep("instrument", frozenset_()),
                FolderRep("item_modifier", frozenset_()),
                FolderRep("jukebox_song", frozenset_()),
                FolderRep("loot_table", frozenset_()),
                FolderRep("painting_variant", frozenset_()),
                FolderRep("predicate", frozenset_()),
                FolderRep("recipe", frozenset_()),
                FolderRep("trim_material", frozenset_()),
                FolderRep("trim_pattern", frozenset_()),
                FolderRep("wolf_variant", frozenset_()),
                FolderRep("worldgen", frozenset_(
                    # There are subfolders that go in here, but we probably won't
                    # have to worry about them for a long time
                ))
        ))
    )

# These overloads tell the type checker
# That this function always returns a FolderRep if given a FolderRep
# and a FileRep or None if given a FileRep

@typing.overload
def strip_empty_folders(folder: FolderRep) -> FolderRep: ...

@typing.overload
def strip_empty_folders(folder: FileRep) -> FileRep | None: ...

def strip_empty_folders(folder: FolderRep | FileRep) -> FolderRep | FileRep | None:

    if isinstance(folder, FileRep):
        return folder
    assert not isinstance(folder, FileRep)

    if len(folder.content) == 0:
        return None

    new_folder_contents = frozenset(
        tuple(
            strip_empty_folders(item) for item in folder.content
            if strip_empty_folders(item) is not None
        )
    )

    new_folder = FolderRep(name=folder.name, content=new_folder_contents) #type: ignore
    # Type checker does not realize new_folder_contents cannot include None

    return new_folder if len(new_folder.content) > 0 else None

def datapack_directory(
    name,
    primary_namespace: typing.Optional[str] = None,
    tick_functions: frozenset[str]=frozenset_(),
    load_functions: frozenset[str]=frozenset_(),
    namespace_folders: frozenset[FolderRep]=frozenset_()
) -> FolderRep:
    """
    Returns a
    representation of a datapack
    directory structure, using "name" as the
    root folder name
    """

    namespace = primary_namespace if primary_namespace is not None else namespacify(name)

    tick_json = FileRep(
        "tick.json",
        tagify(
            tick_functions,
            namespace=namespace
        )
    )
    load_json = FileRep(
        "load.json",
        tagify(
            load_functions,
            namespace=namespace
        )
    )

    output = FolderRep(name, frozenset_(
        FileRep("pack.mcmeta", DEFAULT_MC_META),
        FolderRep(
            "data",
            frozenset(
                (
                    namespace_directory("minecraft", functions=frozenset(), function_tags=frozenset_(
                        tick_json,
                        load_json
                    )),
                ) + (tuple(
                    namespace_folders
                ))
            )
        )
    ))

    return strip_empty_folders(output)

ROOT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
