import tkinter as tk
from html_parser import Document

DEFAULT_FONT = "Times New Roman"
DEFAULT_SIZE = 16
DEFAULT_BG_COLOR = "#ffffff"

DEFAULTS = {
    "h1": {
        "font": "Times New Roman",
        "size": 20,
        "emphasis": "bold",
        "justify": tk.CENTER,
        "anchor": tk.CENTER,
    },
    "p": {
        "font": "Times New Roman",
        "size": 16,
        "justify": tk.LEFT,
        "anchor": tk.W
    }
}

class Component:
    """
    Represents a visible HTML element.
    """
    def draw(self, win: tk.Tk) -> None:
        """
        Draws the element.
        """

class Text(Component):
    """
    Represents a text element.
    """
    def __init__(self,
        text: str,
        font: str=DEFAULT_FONT,
        size: int=DEFAULT_SIZE,
        emphasis: str="",
        side: str=tk.TOP,
        anchor: str=tk.W,
        justify: str=tk.LEFT,
        background: str=DEFAULT_BG_COLOR
    ) -> None:
        self.text = text
        self.font = font
        self.size = size
        self.emphasis = emphasis
        self.side = side
        self.anchor = anchor
        self.justify = justify
        self.background = background

    def draw(self, win: tk.Tk) -> None:
        """
        Draws the element.
        """
        text = tk.Label(win,
            text=self.text,
            font=(self.font, self.size, self.emphasis),
            justify=self.justify,
            background=self.background
        )
        text.pack(side=self.side, anchor=self.anchor)

class Renderer:
    """
    Renders an HTML document.
    """
    def __init__(self) -> None:
        pass

    def render(self, document: Document) -> list[Component]:
        components = []
        for elem in document.root.walk():
            if elem.name == "h1":
                text = ""
                for child in elem.walk():
                    if child.is_text():
                        text += child.data
                text = Text(text=text, **DEFAULTS["h1"])
                components.append(text)
            elif elem.name == "p":
                text = ""
                for child in elem.walk():
                    if child.is_text():
                        text += child.data
                text = Text(text=text, **DEFAULTS["p"])
                components.append(text)
        return components
