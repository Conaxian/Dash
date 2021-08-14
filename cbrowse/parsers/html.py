from __future__ import annotations
from sys import setrecursionlimit
from re import IGNORECASE, DOTALL, compile as regex, sub, Match
from textwrap import indent

setrecursionlimit(5000)

doctype_regex = regex(r"\s*<!DOCTYPE\s+html\s*>\s*", IGNORECASE)
open_tag_regex = regex(
    r"\s*<(?P<name>[a-zA-Z0-9]+)\s*(?P<attrs>(?:[^\s'\">/=]+\s*(?:=\s*[^\s'\"`<>=]+)?|(?:=\s*'[^']+')?|(?:=\s*\"[^\"]+\")?\s*)*)\s*/?>\s*"
)
close_tag_regex = regex(
    r"\s*</(?P<name>[a-zA-Z0-9]+)\s*>\s*"
)
comment_regex = regex(
    r"\s*<!--(?=>|->).*?-->\s*",
DOTALL)
text_regex = regex(
    r"[^<]+"
)
VOID_ELEMENTS = (
    "area",
    "base",
    "br",
    "col",
    "command",
    "embed",
    "hr",
    "img",
    "input",
    "keygen",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr"
)

def clean(match: Match) -> str:
    return sub(match.re, "", match.string, 1)

class Token:
    """
    Represents a parser token.
    """
    def __init__(self, type_: str, value: str="") -> None:
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        return f"{self.type}|{self.value}|"

class Node:
    """
    Represents a single HTML element.
    """
    def __init__(self,
        name: str,
        text: str="",
        attrs: dict[str, str]=None,
        children: list[Node]=None
    ) -> None:
        self.name = name
        self.text = text
        self.attrs = attrs or {}
        self.children = children or []

    def __repr__(self) -> str:
        children = ""
        for child in self.children:
            children += "\n" + indent(repr(child), "  ")
        return f"<{self.name} {self.attrs}>|{self.text}|:{children}"

    def __bool__(self) -> bool:
        return self.name != "null"

    def __getattr__(self, name: str):
        for child in self.children:
            if child.name == name.lower():
                return child
        return self.__class__("null")

    def walk(self):
        """
        Returns all children of the node.
        """
        for child in self.children:
            yield child
            for grandchild in child.walk():
                yield grandchild

    @classmethod
    def construct(cls,
        name: str,
        tokens: list[Token]
    ) -> tuple[Node, list[Token]]:
        """
        Constructs a HTML element from a list of tokens.
        """
        node = cls(name)
        while tokens:
            token = tokens[0]
            tokens = tokens[1:]

            if token.type == "ELEM_OPEN":
                child_node, tokens = Node.construct(token.value, tokens)
                node.children.append(child_node)

            elif token.type == "ATTR_NAME":
                next_token = tokens[0]
                tokens = tokens[1:]
                node.attrs[token.value] = next_token.value

            elif token.type == "TEXT":
                node.text += token.value

            elif token.type == "ELEM_CLOSE" and token.value == node.name:
                break

        return node, tokens

class Parser:
    """
    Parses HTML into a DOM tree.
    """
    def __init__(self) -> None:
        pass

    def _tokenize_attrs(self, attrs: str) -> list[Token]:
        """
        Tokenizes an attribute string.
        """
        tokens = []
        name, value = "", ""
        full_name = False
        while attrs:
            char = attrs[0]

            if not full_name:
                full_name = char == "="
                if char not in " \t\n=": name += char

            else:
                if not value:
                    value += char
                else:
                    if char in "'\"":
                        value += char
                        tokens.append(Token(
                            "ATTR_NAME",
                            name.lower()
                        ))
                        if value.startswith("'"):
                            value = value.strip("'")
                        elif value.startswith('"'):
                            value = value.strip('"')
                        tokens.append(Token(
                            "ATTR_VALUE",
                            value
                        ))
                        name, value = "", ""
                        full_name = False
                    elif value[0] not in "'\"" and \
                    char in " \t\n":
                        tokens.append(Token(
                            "ATTR_NAME",
                            name.lower()
                        ))
                        if value.startswith("'"):
                            value = value.strip("'")
                        elif value.startswith('"'):
                            value = value.strip('"')
                        tokens.append(Token(
                            "ATTR_VALUE",
                            value
                        ))
                        name, value = "", ""
                        full_name = False
                    else:
                        value += char

            attrs = attrs[1:]
        return tokens

    def tokenize(self, html: str) -> list[Token]:
        """
        Tokenizes a HTML string into tokens.
        """
        tokens = []
        while html:

            if match := doctype_regex.match(html):
                tokens.append(Token("DOCTYPE"))
                html = clean(match)

            elif match := open_tag_regex.match(html):
                name = match.group(1).lower()
                tokens.append(Token("ELEM_OPEN", name))
                tokens.extend(self._tokenize_attrs(match.group(2)))
                if name in VOID_ELEMENTS:
                    tokens.append(Token("ELEM_CLOSE", name))
                html = clean(match)

            elif match := close_tag_regex.match(html):
                name = match.group(1).lower()
                tokens.append(Token("ELEM_CLOSE", name))
                html = clean(match)

            elif match := comment_regex.match(html):
                html = clean(match)

            elif match := text_regex.match(html):
                tokens.append(Token("TEXT", match.group(0)))
                html = clean(match)

            else:
                html = html[1:]
        return tokens

    def parse(self, tokens: list[Token]) -> Node:
        """
        Parses tokens into a DOM tree.
        """
        doctype = "none"
        if tokens[0].type == "DOCTYPE":
            doctype = "html"
            tokens = tokens[1:]

        root, _ = Node.construct("root", tokens)
        root.attrs["doctype"] = doctype
        for child in root.children:
            if child.name == "html":
                return child
        return root
