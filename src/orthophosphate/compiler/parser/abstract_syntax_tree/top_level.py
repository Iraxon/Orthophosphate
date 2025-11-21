from abc import abstractmethod
import dataclasses
import enum
import typing

from .references import Ref
from .meta import Node, Children
from .mcfunction import Block

class MCVersion(enum.Enum):
    V1_20_1 = enum.auto()
    DEFAULT = V1_20_1

    @typing.override
    def __str__(self) -> str:
        return self.name[1:].replace("_", ".")

@dataclasses.dataclass(frozen=True)
class PackRoot(Node):
    files: "tuple[PackFile, ...]"
    # pack_version: MCVersion = MCVersion.DEFAULT

    def compile(self) -> dict[str, str | bytes]:
        return {
            f.path(): f.compile()
            for f in self.files
        }

    @typing.override
    def children(self) -> Children:
        return self.files

@dataclasses.dataclass(frozen=True)
class PackFile(Node):
    @abstractmethod
    def path(self) -> str:
        """
        Returns the file path this file will
        be written to, relative to the pack root
        (the directory that contains pack.mcmeta)
        """
        raise NotImplementedError
    @abstractmethod
    def compile(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class MCFunction(PackFile):
    id: str
    body: "Block"

    @typing.override
    def path(self):
        namespace, name = self.id.split(":", 1)
        return f"data/{namespace}/functions/{name}"

    @typing.override
    def children(self) -> Children:
        return (self.id, self.body)

    @typing.override
    def compile(self):
        return (self.id, self.body)

type Taggable = MCFunction

# class TagType(Enum):
#     BLOCK = "blocks"
#     ITEM = "items"
#     FUNCTION = "function"
#     FLUID = "fluids"
#     ENTITY_TYPE = "entity_types"
#     GAME_EVENT = "game_events"
#     BIOME = "biome"
#     FLAT_LEVEL_GENERATOR_PRESET = "flat_level_generator_preset"
#     WORLD_PRESET = "world_preset"
#     STRUCTURE = "structure"
#     CAT_VARIANT = "cat_variant"
#     POINT_OF_INTERST_TYPE = "point_of_interest_type"
#     PAINTING_VARIANT = "painting_variant"
#     BANNER_PATTERN = "banner_pattern"
#     INSTRUMENT = "instrument"
#     DAMAGE_TYPE = "damage_type"

@dataclasses.dataclass(frozen=True)
class Tag[T: Taggable](PackFile):
    id: str
    content: "tuple[Ref[T] | Ref[Tag[T]], ...]"
    replace: bool = False

    @typing.override
    def children(self) -> Children:
        return (str(self.replace),) + tuple(item for item in self.content)

    @typing.override
    def path(self) -> str:
        raise NotImplementedError

    @typing.override
    def compile(self) -> str:
        return (
            "{\n"
            + f"  \"replace\": {'true' if self.replace else 'false'},\n"
            + "  \"values\": [\n"
            + "".join(tuple(
                f"    \"{item.compile()}\"{',' if i < len(self.content) - 1 else ''}\n" for i, item in enumerate(self.content)
            ))
            + "  ]\n"
            + "}"
        )
