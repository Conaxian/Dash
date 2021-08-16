from html_parser.node import Node

class Document:
    """
    Represents an HTML document.
    """
    def __init__(self, root: Node) -> None:
        self.root = root
        self.html = root
        title = ""
        for child in root.head.title.walk():
            if child.is_text():
                title += child.data
        self.title = title
