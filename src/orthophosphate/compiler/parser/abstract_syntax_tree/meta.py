from abc import ABC, abstractmethod
import dataclasses
import typing

from ...tokenizer.token import Token


type Children = "tuple[Node | str, ...]"

@dataclasses.dataclass(frozen=True)
class Node(ABC):
    """
    A node in the abstract syntax tree

    Other than the specified abstract methods, many Node subclasses
    have a compile() method that returns a str or bytes object
    that the node will compile to.

    Some may also implement a ref() method that returns a Ref pointing
    to the object itself given a ParseState
    """
    @abstractmethod
    def children(self) -> Children:
        """
        Provides that which the node should display as its children when rendered
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return self.render()

    def render(self, pre="") -> str:
        """
        Provides a nice readable string
        rep of the AST with nesting

        This function is recursive and
        dangerous to the sanity of anyone
        who works on it
        """
        children = self.children()

        render_contents: tuple[str, ...] = tuple(
            child.render(f"{pre}{'║ ' if i < len(children) - 1 else '  '}")
            if isinstance(child, Node)
            else f"═ {child}"
            for i, child in enumerate(children)
        )
        return (
            f"{'' if pre == '' else'═'} {self.__class__.__name__}\n"
            + "".join(
                    tuple(
                        f"{pre}╠{element}\n"
                        if i < len(render_contents) - 1
                        else f"{pre}╚{element}"
                        for i, element in enumerate(render_contents)
                    )
                )
        )
