from html_parser.node import Node

class Document:
    """
    Represents an HTML document.
    """
    def __init__(self, root: Node) -> None:
        self.root = root
        self.html = root
        self.title = root.head.title
