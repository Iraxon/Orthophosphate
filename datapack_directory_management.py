import os
import string
import typing # Note that Python itself doesn't enforce type hints. It just allows them. VSCode by default also ignores them.
# I included them for your benefit, and also because typing.NamedTuple does require its arguments to be statically typed.
# (Python won't bother to enforce that the type is *correct* though; it only makes sure that there *is* a type assigned)
import enum

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

def frozenset_(*args) -> frozenset:
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

    def realize(self, directory) -> None:
        """
        Creates this file inside the specified
        directory; now that it exists, other
        parts of the code may add data
        """
        with open(os.path.join(directory, self.name), "x") as f:
            f.write(self.content)

class FolderRep(typing.NamedTuple):
    """
    An immutable object representation
    of a folder that can be realized
    """
    name: str
    content: frozenset["FolderRep | FileRep"] = frozenset_()

    def realize(self, directory) -> None:
        """
        Creates this folder and its contents
        inside the specified directory
        """
        os.makedirs(os.path.join(directory, self.name), exist_ok=True)
        for item in self.content:
                item.realize(os.path.join(directory, self.name))

def namespacify(name) -> str:
    """
    Converts an arbitrarily-formatted
    datapack name into a suitable namespace
    by removing special characters and
    lowercasing it
    """
    return "".join(
        (
            char
            if char is not " "
            else "_"
            # Convert spaces to underscores
        )
        for char in name
        if (
            char in string.ascii_letters or char in string.digits or char in ("_", "-", ".", " ")
            # Omit chars that aren't legal Minecraft resource location characters or space
        )
    ).lower() # Lowercase capitals

def datapack_directory(name, namespace=None) -> dict:
    """
    Returns a dictionary
    representation of a datapack
    directory structure, using "name" as the
    datapack namespace
    """
    if namespace is None:
        namespace = name
    return FolderRep(name, frozenset_(
        FileRep("pack.mcmeta", DEFAULT_MC_META),
        FolderRep("data", frozenset_(
            FolderRep(namespace, frozenset_(
                FolderRep("function", frozenset_()),
                FolderRep("structure", frozenset_()),
                FolderRep("tags", frozenset_(
                    FolderRep("function", frozenset_())
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
            )),
            FolderRep("minecraft", frozenset_(
                FolderRep("tags", frozenset_(
                    FolderRep("function", frozenset_(
                        FileRep("tick.json"),
                        FileRep("load.json")
                    ))
                ))
            ))
        ))
    ))

ROOT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    print(ROOT_DIR_PATH)
    print(os.path.join("data", "function"))

    print(test_namespace := namespacify(test_name :="My very cool DATAPACK"))
    print(test_directory := datapack_directory(test_name, test_namespace))

    if input("Do you want to test the creation of datapack folders? (Y/N) "
          "This will create a test directory inside the testing_grounds "
          "directory. \n> ") == "Y":
        test_directory.realize(os.path.join(ROOT_DIR_PATH, "testing_grounds"))