from parsers import HtmlParser

parser = HtmlParser()

class Document:
    """
    Represents a HTML document.
    """
    def __init__(self, html: str) -> None:
        tokens = parser.tokenize(html)
        self.root = parser.parse(tokens)
        self.html = self.root
        self.title = self.root.head.title.text
