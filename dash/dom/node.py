from __future__ import annotations
from typing import Union

def indent(string: str, spaces: int=2):
    """
    Indents a string by an arbitrary number of spaces.
    """
    lines = string.split("\n")
    indentation = "\n" + " " * spaces
    return indentation.join(lines)

class Node:
    """
    Represents a single HTML element.
    """
    def __init__(self,
        name: str,
        attrs: dict[str, str]=None,
        parent: Node=None,
        children: list[Node]=None
    ) -> None:
        self.name = name
        self.attrs = attrs or {}
        self.parent = parent
        self.children = children or []
        self.nullish = False

    def __repr__(self) -> str:
        children = ""
        for child in self.children:
            if isinstance(child, Text):
                children += "\n" + indent(child.data).strip()
            else:
                children += "\n" + indent(repr(child))
        return f"<{self.name}; {self.attrs}>:{children}"

    def __bool__(self) -> bool:
        return not self.nullish

    def __getattr__(self, name: str):
        for child in self.children:
            if child.name == name.lower():
                return child
        return self.null()

    def is_text(self) -> Union[Text, Node]:
        """
        Returns `self` if `self.type` is `"CHAR"`.
        """
        return self if self.name == "<text>" else Node.null()

    def adopt(self, child: Node) -> Node:
        """
        Adopts a node as a child.
        """
        self.children.append(child)
        child.parent = self

    def walk(self):
        """
        Walks through every descendant node of this node.
        """
        for child in self.children:
            yield child
            if child.children:
                yield from child.walk()

    @classmethod
    def null(cls) -> Node:
        """
        Creates a null node.
        """
        node = cls("")
        node.nullish = True
        node.name = "<null>"
        node.data = "<null>"
        return node

class Root(Node):
    """
    Represents a root node during the tree construction.
    """
    def __init__(self) -> None:
        super().__init__("")

    def unpack(self):
        """
        Unpacks the root node.
        """
        for child in self.children:
            if child.name == "html":
                return child
        return Node("html", children=self.children)

class Text(Node):
    """
    Represents text inside an element.
    """
    def __init__(self, data: str="") -> None:
        super().__init__("<text>")
        self.data = data
