import tkinter as tk
from document import Document

DEFAULT_FONT = "Times New Roman"
DEFAULT_SIZE = 16

DEFAULTS = {
    "h1": {
        "font": "Arial",
        "size": 20
    },
    "p": {
        "font": "Arial",
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
        justify: str=""
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
            font=(self.font, self.size)
        )
        text.pack()

class Renderer:
    """
    Renders a HTML document.
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
