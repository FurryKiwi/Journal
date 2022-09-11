# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>=

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog


class DefaultNotebook(ttk.Notebook):
    TAB_FONT = ("Arial", 12, 'bold')
    BUTTON_BG = "#007fff"  # Change this to whatever color you need for when no theme is specified
    __slots__ = "root", "theme", "style", "_active", "packed"

    def __init__(self, root, theme: bool = False, *args, **kwargs):
        kwargs['style'] = "TNotebook"
        ttk.Notebook.__init__(self, root, *args, **kwargs)
        self.root = root
        # If no theme is specified, it will create its own custom elements
        # to close the notebook tabs
        if theme:
            self.theme = theme
            self.style = ttk.Style(self.root)
            self.style.theme_create("TNotebook")
            self.style.theme_use("TNotebook")
            self.__initialize_custom_style()

        self._active = None
        self.packed = False

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def validate_tab_length(self, frame):
        """Checks the length of characters in a tab and shortens it if need be."""
        length = len(self.tab(frame)['text'])
        if 14 <= length <= 18:
            original = self.tab(frame)['text']
            sliced = original[:-8]
            self.tab(frame, text=(sliced + "..."))
        elif 19 <= length <= 23:
            original = self.tab(frame)['text']
            sliced = original[:-12]
            self.tab(frame, text=(sliced + "..."))
        elif 24 <= length <= 28:
            original = self.tab(frame)['text']
            sliced = original[:-16]
            self.tab(frame, text=(sliced + "..."))
        elif 29 <= length <= 33:
            original = self.tab(frame)['text']
            sliced = original[:-22]
            self.tab(frame, text=(sliced + "..."))
        elif 34 <= length <= 35:
            original = self.tab(frame)['text']
            sliced = original[:-23]
            self.tab(frame, text=(sliced + "..."))

    def on_close_press(self, event) -> None:
        """Called when the button is pressed over the close button"""
        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
            return

    def on_close_release(self, event) -> None:
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        if "close" not in element:
            # User moved the mouse off of the close button
            # Need to change the state back of the button
            self.state(["!pressed"])
            return

        index = self.index("@%d,%d" % (event.x, event.y))

        if self._active == index:
            self.forget(index)

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self) -> None:
        """Initializes the style for the notebook along with creating elements."""
        self.images = (
            tk.PhotoImage("img_close",
                          data='''iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAAXNSR0IArs4c6QAAAC5JREFUGJVjYCAFnD9z
                          5j/RctgU4zQAWQKfLXAF2BQx4dWFzzSS3IdTjKTgIQQAplgvl/OK83kAAAAASUVORK5CYII=
                          '''),
            tk.PhotoImage("img_closeactive",
                          data='''iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAAXNSR0IArs4c6QAAAFJJREFUGJWVkEsOgEAI
                          Q1+8/0HYkpTz4WbQMQ4T7Yq05VMA0t2TBkPLqzCzl3lw96AiZvOKewiSUlK7BYAyVMOsHV2IFvPqiNjftw3z5z2fHn4C
                          eBlslik72i8AAAAASUVORK5CYII=
                          '''),
            tk.PhotoImage("img_closepressed",
                          data='''iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAAXNSR0IArs4c6QAAAD1JREFUGJVjYICA/wy4
                          wX8GBgYGRjRFjNgUIUtgU4wihmwCLusZ8VqF7hQmHKZgN5YUq4nyDFHBQ8hauBwAP+4PBPOBamIAAAAASUVORK5CYII=
                          ''')
        )

        self.style.element_create("close", "image", "img_close",
                                  ("active", "pressed", "!disabled", "img_closepressed"),
                                  ("active", "!disabled", "img_closeactive"), border=10, sticky='e')
        self.style.layout("TNotebook", [("TNotebook.client", {"sticky": "nswe"})])
        self.style.layout("TNotebook.Tab", [
            ("TNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("TNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("TNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("TNotebook.label", {"side": "left", "sticky": 'w'}),
                                    ("TNotebook.close", {"side": "right", "sticky": 'e'}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
        if self.theme:
            self.style.theme_settings("TNotebook", {
                "TNotebook.Tab": {
                    "configure": {"padding": [2, 4], "font": self.TAB_FONT, "focuscolor": "."},
                    "map": {"background": [("selected", self.BUTTON_BG)],
                            "expand": [("selected", [0, 2, 0, 0])]}}
            })


# Testing purposes ----------------------------
if __name__ == '__main__':
    import Scripts.utils as utils

    root = tk.Tk()
    utils.set_window(root, 400, 400, "Test Notebook")
    frame = tk.Frame(root)
    frame.pack(expand=True, fill='both', pady=4)

    notebook = DefaultNotebook(frame, theme=True)
    notebook.pack(side='top', expand=True, fill='both')

    frame1 = tk.Frame(notebook)
    tk.Label(frame1, text="Blah Blah Blah").pack()
    tk.Label(frame1, text="Blah Blah").pack()
    tk.Label(frame1, text="Blah").pack()
    frame1.pack()
    notebook.add(frame1, text="Frame 1")

    frame2 = tk.Frame(notebook)
    tk.Label(frame2, text="Yes yes yes").pack()
    tk.Label(frame2, text="yes yes").pack()
    tk.Label(frame2, text="no no").pack()
    frame2.pack()
    notebook.add(frame2, text="Frame 2")

    root.mainloop()
