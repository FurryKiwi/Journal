# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>
import random

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog
    from tkinter.colorchooser import askcolor


class ColorPicker(tk.Label):
    """A basic color picker that utilizes the colorchooser dialog built in tkinter. The chosen color sets the labels
    background to said color for visual representation to user.

    Args: root (Frame/window),
        class_name: identifier for each widget to set styling of widgets ie: "TFrame, "TButton", "Entry"
        type_class: identifier for each widget style argument ie: "foreground", "background", "selectbackground", etc

    Returns the hex code for the chosen color with a get method.

    """
    __slots__ = "root", "class_name", "type_class", "color"

    def __init__(self, root, class_name, type_class, **kwargs):
        tk.Label.__init__(self, root, **kwargs)
        self.root = root
        self.class_name = class_name
        self.type_class = type_class
        self.color = None

    def choose_color(self):
        color_code = askcolor(title="Choose color", parent=self.root)
        _, hex = color_code
        self["background"] = hex
        self.color = hex

    def get(self):
        return self.color


def change_color(event):
    event.widget.choose_color()
    set_style(event, button, event.widget.get())


def set_style(event, widget, color):
    widget[event.widget.type_class] = color


if __name__ == '__main__':
    root = tk.Tk()
    colors = ['red', 'blue', 'green', 'orange', 'white', 'grey', 'black', 'purple', 'brown', 'yellow', 'violet']
    button = tk.Button(root, text="Some Text", width=10)
    button.pack()
    new = ColorPicker(root, "TButton", "foreground", text=" ", width=4, height=2,
                      background=random.choice(colors), borderwidth=1, relief='solid')
    new.pack(side='top', pady=5)

    new.bind("<Button-1>", lambda event: change_color(event))

    root.geometry("300x300+800+300")
    root.mainloop()
