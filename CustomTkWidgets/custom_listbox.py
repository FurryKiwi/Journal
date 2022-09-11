try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk


class DefaultListbox(tk.Listbox):
    __slots__ = "root", "selection", "shifting", "ctrl_clicked", "index_lock"

    def __init__(self, root, **kw):
        tk.Listbox.__init__(self, root, **kw)
        self.root = root
        self.bind('<Button-1>', self.set_current)
        self.bind('<Control-1>', self.toggle_selection)
        self.bind('<B1-Motion>', self.shift_selection)
        self.selection = False
        self.shifting = False
        self.ctrl_clicked = False
        self.index_lock = False
        self.unlock_shifting()

    def set_current(self, event):
        self.ctrl_clicked = False
        i = self.nearest(event.y)
        self.selection = self.selection_includes(i)

    def toggle_selection(self, event):
        self.ctrl_clicked = True

    def move_item(self, source, target):
        if not self.ctrl_clicked:
            item = self.get(source)
            self.delete(source)
            self.insert(target, item)

    def unlock_shifting(self):
        self.shifting = False

    def lock_shifting(self):
        self.shifting = True

    def unlock_selection(self):
        self.index_lock = False

    def lock_selection(self):
        self.index_lock = True

    def shift_selection(self, event):
        if self.index_lock:
            return "break"
        else:
            if self.ctrl_clicked:
                return "break"
            selection = self.curselection()
            if not self.selection or len(selection) == 0:
                return "break"

            if self.shifting:
                return "break"

            selection_range = range(min(selection), max(selection))
            current_index = self.nearest(event.y)

            line_height = 5
            bottom_y = self.winfo_height()
            if event.y >= bottom_y - line_height:
                self.lock_shifting()
                self.see(self.nearest(bottom_y - line_height) + 1)
                self.root.after(500, self.unlock_shifting)
            if event.y <= line_height:
                self.lock_shifting()
                self.see(self.nearest(line_height) - 1)
                self.root.after(500, self.unlock_shifting)

            if current_index < min(selection):
                self.lock_shifting()
                not_in_index = 0
                for i in selection_range[::-1]:
                    if not self.selection_includes(i):
                        self.move_item(i, max(selection) - not_in_index)
                        not_in_index += 1
                current_index = min(selection) - 1
                self.move_item(current_index, current_index + len(selection))
            elif current_index > max(selection):
                self.lock_shifting()
                not_in_index = 0
                for i in selection_range:
                    if not self.selection_includes(i):
                        self.move_item(i, min(selection) + not_in_index)
                        not_in_index += 1
                current_index = max(selection) + 1
                self.move_item(current_index, current_index - len(selection))
            self.unlock_shifting()
            return "break"


# Testing Purposes ------------


if __name__ == '__main__':
    from Scripts.utils import *

    r = tk.Tk()
    set_window(r, 400, 300, "Test", True)
    data = ["This", "Is", "Some", "Shit", "ToDo", "With", "Some", "More", "Fuck this up",
            "This", "Is", "Some", "Shit", "ToDo", "With", "Some", "More", "Fuck this up",
            "This", "Is", "Some", "Shit", "ToDo", "With", "Some", "More", "Fuck this up"]
    test = DefaultListbox(r, selectmode=tk.EXTENDED)
    test.pack()
    for i in data:
        test.insert(tk.END, i)
    r.mainloop()
