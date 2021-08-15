from __future__ import annotations
from typing import Union

class Token:
    """
    Represents a base HTML token.
    """
    def __init__(self, type_: str) -> None:
        self.type = type_
        self.new_state = None
        self.nullish = False

    def __repr__(self) -> str:
        return f"<{self.type}>"

    def __bool__(self) -> bool:
        return not self.nullish

    def is_doctype(self) -> Union[Doctype, Token]:
        """
        Returns `self` if `self.type` is `"DOCTYPE"`.
        """
        return self if self.type == "DOCTYPE" else Token.null()

    def is_start_tag(self) -> Union[StartTag, Token]:
        """
        Returns `self` if `self.type` is `"START_TAG"`.
        """
        return self if self.type == "START_TAG" else Token.null()

    def is_end_tag(self) -> Union[EndTag, Token]:
        """
        Returns `self` if `self.type` is `"END_TAG"`.
        """
        return self if self.type == "END_TAG" else Token.null()

    def is_comment(self) -> Union[Comment, Token]:
        """
        Returns `self` if `self.type` is `"COMMENT"`.
        """
        return self if self.type == "COMMENT" else Token.null()

    def is_char(self) -> Union[Character, Token]:
        """
        Returns `self` if `self.type` is `"CHAR"`.
        """
        return self if self.type == "CHAR" else Token.null()

    def is_eof(self) -> Union[Eof, Token]:
        """
        Returns `self` if `self.type` is `"CHAR"`.
        """
        return self if self.type == "EOF" else Token.null()

    @classmethod
    def null(cls) -> Token:
        """
        Creates a null token.
        """
        token = cls("")
        token.nullish = True
        token.name = "<null>"
        token.data = "<null>"
        return token

class Doctype(Token):
    """
    Represents a DOCTYPE token.
    """
    def __init__(self,
        name: str="",
        pub_id: str=None,
        sys_id: str=None,
        force_quirks: bool=False
    ) -> None:
        super().__init__("DOCTYPE")
        self.name = name
        self.pub_id = pub_id
        self.sys_id = sys_id
        self.force_quirks = force_quirks

    def __repr__(self) -> str:
        return f"<{self.type}>|{self.name}|{self.pub_id}|\
{self.sys_id}|{self.force_quirks}|"

class StartTag(Token):
    """
    Represents a start tag token.
    """
    def __init__(self,
        name: str="",
        self_closing: bool=False,
        attrs: dict[str, str]=None
    ) -> None:
        super().__init__("START_TAG")
        self.name = name
        self.self_closing = self_closing
        self.attrs = attrs or {}
        self.temp_attr = ["", ""]
        self.temp_attr_invalid = False

    def __repr__(self) -> str:
        return f"<{self.type}>|{self.name}|\
{self.self_closing}|{self.attrs}|"

    def new_attr(self, name: str, value: str) -> None:
        """
        Creates a new attribute. If this is the last attribute
        of this tag to be created, `self.save_attr` needs to be
        called afterwards to save the attribute.
        """
        self.save_attr()
        self.temp_attr = [name, value]

    def save_attr(self) -> None:
        """
        Adds the current temporary attribute to the tag's attributes.
        """
        if self.temp_attr[0] and not self.temp_attr_invalid:
            name, value = self.temp_attr
            self.attrs[name] = value
        self.temp_attr = ["", ""]

class EndTag(Token):
    """
    Represents an end tag token.
    """
    def __init__(self, name: str="") -> None:
        super().__init__("END_TAG")
        self.name = name

    def __repr__(self) -> str:
        return f"<{self.type}>|{self.name}|"

class Comment(Token):
    """
    Represents a comment token.
    """
    def __init__(self, data: str="") -> None:
        super().__init__("COMMENT")
        self.data = data

    def __repr__(self) -> str:
        return f"<{self.type}>|{self.data}|"

class Character(Token):
    """
    Represents a character token.
    """
    def __init__(self, data: str="") -> None:
        super().__init__("CHAR")
        self.data = data

    def __repr__(self) -> str:
        return f"<{self.type}>|{self.data}|"

class Eof(Token):
    """
    Represents an end-of-file token.
    """
    def __init__(self) -> None:
        super().__init__("EOF")
