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
            for node in self.open_nodes:
                if node.name == "template":
                    return
            html_node = self.open_nodes[0]
            for key, value in self.token.attrs.values():
                html_node.attrs.setdefault(key, value)
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
        if (char := self.token.is_char().data) in SPACE_CR:
            self.insert_char(char)
        elif self.token.is_comment():
            pass
        elif self.token.is_doctype():
            # Parse Error
            pass
        elif self.token.is_start_tag().name == "html":
            # Parse Error
            for node in self.open_nodes:
                if node.name == "template":
                    return
            html_node = self.open_nodes[0]
            for key, value in self.token.attrs.values():
                html_node.attrs.setdefault(key, value)
        elif self.token.is_start_tag().name in \
        ("base", "basefont", "bgsound", "link", "meta"):
            node = Node("meta", self.token.attrs)
            self.insert_node(node)
            self.open_nodes.pop()
        elif self.token.is_start_tag().name == "title":
            node = Node("title", self.token.attrs)
            self.insert_node(node)
            self.token.new_state = "RCDATA"
            self.return_mode = "IN_HEAD"
            self.mode = "TEXT"

    def text_mode(self):
        if (char := self.token.is_char().data) != "<null>":
            self.insert_char(char)
        elif self.token.is_eof():
            # Parse Error
            self.open_nodes.pop()
            self.mode = self.return_mode
            self.reprocess = True
        else:
            self.open_nodes.pop()
            self.mode = self.return_mode
