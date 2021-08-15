import tkinter as tk
from html_parser import Document

DEFAULT_FONT = "Times New Roman"
DEFAULT_SIZE = 16

DEFAULTS = {
    "h1": {
        "font": "Times New Roman",
        "size": 20
    },
    "p": {
        "font": "Times New Roman",
        "size": 16,
        "justify": tk.LEFT
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
        justify: str=tk.LEFT
    ) -> None:
        self.text = text
        self.font = font
        self.size = size
        self.justify = justify

    def draw(self, win: tk.Tk) -> None:
        """
        Draws the element.
        """
        text = tk.Label(win,
            text=self.text,
            font=(self.font, self.size),
            justify=self.justify
        )
        text.pack()

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
                text = Text(text=elem.text, **DEFAULTS["h1"])
                components.append(text)
            elif elem.name == "p":
                text = Text(text=elem.text, **DEFAULTS["p"])
                components.append(text)
        return components
