from html_parser.tokenizer import Tokenizer
from html_parser.tree_constructor import TreeConstructor
from html_parser.document import Document

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
        print(root)
        return Document(root)
