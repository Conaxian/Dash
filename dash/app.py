import tkinter as tk
from webloader import load as load_page
from renderer import Renderer

DEFAULT_WIN_TITLE = "<no title>"
DEFAULT_BG_COLOR = "#ffffff"
renderer = Renderer()

class App:
    """
    Represents a GUI application.
    """
    def __init__(self) -> None:
        self.win = tk.Tk()
        self.fullscreen = False
        width = self.win.winfo_screenwidth() // 4 * 3
        height = self.win.winfo_screenheight() // 4 * 3
        self.win.geometry(f"{width}x{height}")
        self.win["background"] = DEFAULT_BG_COLOR
        self.win.bind("<Escape>", lambda e: exit())
        self.win.bind("<F11>", self.toggle_fullscreen)
        self.document = None

    def toggle_fullscreen(self, event):
        print(event.__class__)
        self.fullscreen = not self.fullscreen
        self.win.attributes("-fullscreen", self.fullscreen)

    def load_page(self, url: str) -> None:
        self.document = load_page(url)

    def render(self) -> None:
        components = renderer.render(self.document)
        for component in components:
            component.draw(self.win)
        self.win.title(self.document.title or DEFAULT_WIN_TITLE)

    def run(self) -> None:
        """
        Runs the app and blocks the execution.
        """
        self.win.mainloop()
