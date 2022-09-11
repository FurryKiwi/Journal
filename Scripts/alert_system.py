# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

from Scripts.settings import *


class AlertSystem:
    __slots__ = "root", "layout", "queue", "shown", "after_id"

    def __init__(self, root):
        self.root = root
        self.layout = None
        self.queue = []
        self.shown = False
        self.after_id = ''

    def show_alert(self, message: tuple = None) -> None:
        if message is not None:
            self.queue.append(message)
        if not self.shown:
            try:
                message, color = self.queue.pop()
                label = ttk.Label(self.layout.category_frame, text=message, style="R.TLabel", foreground=color,
                                  font=DEFAULT_FONT)
                label.grid(row=1, column=4, columnspan=2)
                self.shown = True
                self.after_id = self.root.after(1000, lambda: self.clear_canvas(label))
            except IndexError:
                return

    def clear_canvas(self, label):
        label.grid_forget()
        del label
        self.shown = False
        self.show_alert()

    def cancel_after(self):
        self.root.after_cancel(self.after_id)
