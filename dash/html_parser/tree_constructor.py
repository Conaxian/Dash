from html_parser.constants import *
from html_parser.tokens import Token
from html_parser.node import Node, Root, Text

class TreeConstructor:
    """
    Represents a single stream of tokens from which
    a Node tree can be constructed.
    """
    def reset(self) -> None:
        """
        Resets the tree constructor state.
        """
        self.mode = "INITIAL"
        self.quirks_mode = False
        self.scripting = False
        self.frameset_ok = True
        self.reprocess = True
        self.open_nodes: list[Node] = []
        self.head = None
        self.root = Root()

    def insert_node(self, node: Node) -> None:
        """
        Inserts the node into the last open node.
        """
        parent = self.open_nodes[-1]
        parent.adopt(node)
        self.open_nodes.append(node)

    def insert_char(self, char: str) -> None:
        """
        Inserts the character into the last open node.
        """
        parent = self.open_nodes[-1]
        if parent.children and (text := parent.children[-1].is_text()):
            text.data += char
        else:
            node = Text(char)
            parent.adopt(node)

    def parse_raw_text(self, algorithm: str) -> None:
        """
        Parses either raw text or RCDATA elements.
        """
        node = Node(self.token.name, self.token.attrs)
        self.insert_node(node)
        self.token.new_state = algorithm
        self.return_mode = self.mode
        self.mode = "TEXT"

    def html_in_body(self) -> None:
        """
        Handles the `<html>` tag in a `<body>` tag.
        """
        for node in self.open_nodes:
            if node.name == "template":
                return
        html_node = self.open_nodes[0]
        for key, value in self.token.attrs.values():
            html_node.attrs.setdefault(key, value)

    def handle(self, token: Token) -> Node:
        """
        Handles an incoming token from a token stream.
        """
        self.token = token
        print(f"Token: {token}")
        while self.reprocess:
            self.reprocess = False
            mode_func = self.mode.lower() + "_mode"
            getattr(self, mode_func)()
        self.reprocess = True

    def initial_mode(self):
        if self.token.is_char().data in SPACE_CR:
            pass
        elif self.token.is_comment():
            pass
        elif doctype := self.token.is_doctype():
            if doctype.name != "html" or doctype.pub_id or \
            (doctype.sys_id and doctype.sys_id != "about:legacy-compat"):
                # Parse Error
                pass
            self.mode = "BEFORE_HTML"
            if doctype.force_quirks:
                self.quirks_mode = True
                return
            if doctype.name != "html":
                self.quirks_mode = True
                return
            if doctype.pub_id is not None:
                for string in PUB_ID_EQUALS:
                    if string.lower() == doctype.pub_id.lower():
                        self.quirks_mode = True
                        return
                for string in PUB_ID_STARTS:
                    if doctype.pub_id.lower().startswith(string.lower()):
                        self.quirks_mode = True
                        return
            if doctype.sys_id is not None:
                for string in SYS_ID_EQUALS:
                    if string.lower() == doctype.sys_id.lower():
                        self.quirks_mode = True
                        return
            if doctype.pub_id is not None and doctype.sys_id is None:
                for string in PUB_ID_STARTS_NO_SYS_ID:
                    if doctype.pub_id.lower().startswith(string.lower()):
                        self.quirks_mode = True
                        return
            if doctype.pub_id is not None and doctype.sys_id is not None:
                for string in PUB_ID_STARTS_HAS_SYS_ID:
                    if doctype.pub_id.lower().startswith(string.lower()):
                        self.quirks_mode = True
                        return
        else:
            # Parse Error
            self.quirks_mode = True
            self.mode = "BEFORE_HTML"
            self.reprocess = True

    def before_html_mode(self):
        if self.token.is_doctype():
            # Parse Error
            pass
        elif self.token.is_comment():
            pass
        elif self.token.is_char().data in SPACE_CR:
            pass
        elif self.token.is_start_tag().name == "html":
            node = Node("html", self.token.attrs)
            self.root.adopt(node)
            self.open_nodes.append(node)
            self.mode = "BEFORE_HEAD"
        elif self.token.is_end_tag().name not in \
        ("<null>", "head", "body", "html", "br"):
            # Parse Error
            pass
        else:
            node = Node("html")
            self.root.adopt(node)
            self.open_nodes.append(node)
            self.mode = "BEFORE_HEAD"
            self.reprocess = True

    def before_head_mode(self):
        if self.token.is_char().data in SPACE_CR:
            pass
        elif self.token.is_comment():
            pass
        elif self.token.is_doctype():
            # Parse Error
            pass
        elif self.token.is_start_tag().name == "html":
            # Parse Error
            self.html_in_body()
        elif self.token.is_start_tag().name == "head":
            node = Node("head", self.token.attrs)
            self.insert_node(node)
            self.head = node
            self.mode = "IN_HEAD"
        elif self.token.is_end_tag().name not in \
        ("<null>", "head", "body", "html", "br"):
            # Parse Error
            pass
        else:
            node = Node("head")
            self.insert_node(node)
            self.head = node
            self.mode = "IN_HEAD"
            self.reprocess = True

    def in_head_mode(self):
        if self.token.is_char().data in SPACE_CR:
            self.insert_char(self.token.data)
        elif self.token.is_comment():
            pass
        elif self.token.is_doctype():
            # Parse Error
            pass
        elif self.token.is_start_tag().name == "html":
            # Parse Error
            self.html_in_body()
        elif self.token.is_start_tag().name in \
        ("base", "basefont", "bgsound", "link", "meta"):
            node = Node(self.token.name, self.token.attrs)
            self.insert_node(node)
            self.open_nodes.pop()
        elif self.token.is_start_tag().name == "title":
            self.parse_raw_text("RCDATA")
        elif self.token.is_start_tag().name in ("noframes", "style"):
            self.parse_raw_text("RAWTEXT")
        elif self.token.is_end_tag().name == "head":
            self.open_nodes.pop()
            self.mode = "AFTER_HEAD"
        elif self.token.is_end_tag().name in ("body", "html", "br"):
            self.open_nodes.pop()
            self.mode = "AFTER_HEAD"
            self.reprocess = True
        else:
            self.open_nodes.pop()
            self.mode = "AFTER_HEAD"
            self.reprocess = True

    def after_head_mode(self):
        if self.token.is_char().data in SPACE_CR:
            self.insert_char(self.token.data)
        elif self.token.is_comment():
            pass
        elif self.token.is_doctype():
            # Parse Error
            pass
        elif self.token.is_start_tag().name == "html":
            # Parse Error
            self.html_in_body()
        elif self.token.is_start_tag().name == "body":
            node = Node("body", self.token.attrs)
            self.insert_node(node)
            self.frameset_ok = False
            self.mode = "IN_BODY"
        elif self.token.is_start_tag().name == "frameset":
            node = Node("frameset", self.token.attrs)
            self.insert_node(node)
            self.mode = "IN_FRAMESET"
        elif self.token.is_start_tag().name in \
        ("base", "basefont", "bgsound", "link", "meta", "noframes",
        "script", "style", "template", "title"):
            # Parse Error
            self.open_nodes.append(self.head)
            self.in_head_mode()
            self.open_nodes.pop()
        elif self.token.is_end_tag().name == "template":
            self.in_head_mode()
        elif self.token.is_start_tag().name == "head" or \
        self.token.is_end_tag().name not in ("<null>", "body",
        "html", "br"):
            # Parse Error
            pass
        else:
            node = Node("body")
            self.insert_node(node)
            self.mode = "IN_BODY"
            self.reprocess = True

    def in_body_mode(self):
        pass

    def text_mode(self):
        if self.token.is_char().data != "<null>":
            self.insert_char(self.token.data)
        elif self.token.is_eof():
            # Parse Error
            self.open_nodes.pop()
            self.mode = self.return_mode
            self.reprocess = True
        else:
            self.open_nodes.pop()
            self.mode = self.return_mode
