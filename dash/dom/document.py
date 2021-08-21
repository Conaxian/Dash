from dom.node import Node

class Doctype:
    """
    Represents a document type.
    """
    def __init__(self, name: str, pub_id: str="", sys_id: str="") -> None:
        self.name = name
        self.pub_id = pub_id
        self.sys_id = sys_id

class Document:
    """
    Represents an HTML document.
    """
    def __init__(self, root: Node) -> None:
        self.doctype = Doctype("")
        self.root = root
        self.html = root
        title = ""
        for child in root.head.title.walk():
            if child.is_text():
                title += child.data
        self.title = title
