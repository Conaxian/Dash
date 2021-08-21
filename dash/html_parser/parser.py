from html_parser.tokenizer import Tokenizer
from html_parser.tree_constructor import TreeConstructor
from dom.document import Document

# https://html.spec.whatwg.org/multipage/parsing.html#parsing

class Parser:
    """
    Represents a single parsable HTML text.
    """
    def __init__(self, html: str) -> None:
        self.html = html

    def parse(self) -> Document:
        """
        Parses the HTML into a document object.
        """
        tokenizer = Tokenizer(self.html)
        tree_constructor = TreeConstructor()
        tree_constructor.reset()
        for token in tokenizer.tokenize():
            tree_constructor.handle(token)
        root = tree_constructor.root.unpack()
        return Document(root)
