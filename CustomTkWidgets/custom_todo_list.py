# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

from CustomTkWidgets.custom_scrollable_frames import VerticalScrolledFrame


class CustomToDoList(ttk.Frame):
    """Custom Check List that will add check-buttons to every element in a given list."""

    DEFAULT_FONT = ("Arial", 12)
    ENTRY_COLOR = "#848689"

    def __init__(self, frame, root, todo_list: list = None, entry_limit: int = 80, **kwargs):
        ttk.Frame.__init__(self, frame, **kwargs)
        self.entry_limit = entry_limit
        self.root = root
        self.string_vars = []
        self.check_buttons = []
        self.frame = VerticalScrolledFrame(self)
        self.frame.pack(side='top', fill=tk.BOTH, expand=tk.TRUE)
        self.frame.interior.bind("<ButtonPress-3>", lambda event: self.create_popup(event))
        self.frame.canvas.bind("<ButtonPress-3>", lambda event: self.create_popup(event))

        if todo_list:
            self._initial_creation(todo_list)

    def _initial_creation(self, values: list) -> None:
        for choice in values:
            choice = choice.strip()
            already_added = self.get_all_items()
            if choice not in already_added:
                var = tk.StringVar(value=choice)
                self.string_vars.append(var)
                cb = ttk.Checkbutton(self.frame.interior, variable=var, text=choice,
                                     onvalue=choice, offvalue="", style="TCheckbutton", takefocus=False)
                cb.pack(side="top", fill="x", expand=True)
                cb.bind("<ButtonPress-3>", lambda event: self.create_popup(event))
                self.check_buttons.append(cb)
        self.deselect_all()

    def create_popup(self, event) -> None:
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Select All", command=lambda: self.select_all())
        menu.add_command(label="Deselect All", command=lambda: self.deselect_all())
        menu.add_command(label="Add Element", command=lambda: self.create_win())
        menu.add_command(label="Remove Element", command=lambda: self.remove_element(event))
        menu.add_command(label="Remove All Selected", command=lambda e=None: self.remove_all_selected())
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def create_win(self) -> None:
        top_window, entry = self.create_pop_up("Add Elements", self.root, self.entry_limit)
        top_window.grab_set()
        ttk.Button(top_window, text="Add Elements", width=21, style="Accent.TButton",
                   command=lambda e=None: self.add_element(entry.get(), top_window)).pack(side='top', padx=4, pady=4)

        entry.bind("<Return>", lambda e=None: self.add_element(entry.get(), top_window))

    def create_pop_up(self, title: str, root: tk.Tk, entry_limit: int) -> (tk.Toplevel, tk.Entry):
        """Creates a top level window for renaming definitions/categories and adding new categories."""
        top_window = tk.Toplevel(root)
        self.set_window(top_window, 220, 120, title, parent=root, offset=(240, 90))

        ttk.Label(top_window, text=f"{title}: ", font=self.DEFAULT_FONT).pack()
        ttk.Label(top_window, text=f"To add multiple, use a comma", font=("Arial", 10), foreground="Yellow").pack()

        entry = tk.Entry(top_window, validate="key", background=self.ENTRY_COLOR,
                         validatecommand=(root.register(lambda event: self.validate_entry(event, entry_limit)), "%P"),
                         font=self.DEFAULT_FONT, width=21)
        entry.pack(side='top', padx=4, pady=4)

        entry.focus_set()

        return top_window, entry

    @staticmethod
    def validate_entry(entry, limit):
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        if len(entry) <= limit:
            return True
        else:
            return False

    @staticmethod
    def set_window(root, w, h, title, parent=None, resize: bool = False, offset: tuple[int, int] = None) -> None:
        if parent:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            x = (w / 2) + parent_x  # 280
            y = (h / 2) + parent_y  # 200
        else:
            ws = root.winfo_screenwidth()
            hs = root.winfo_screenheight()
            x = (ws / 2) - (w / 2)
            y = (hs / 2) - (h / 2)
        root.title(title)
        if offset:
            root.geometry('%dx%d+%d+%d' % (w, h, x + offset[0], y + offset[1]))
        else:
            root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        if resize:
            root.resizable(1, 1)
        else:
            root.resizable(0, 0)

    def add_element(self, entry: str, top_window: tk.Toplevel) -> None:
        if entry == '':
            return
        add_multiple = self.split_entries(entry)

        for value in add_multiple:
            already_added = self.get_all_items()
            if value not in already_added:
                var = tk.StringVar(value=value)
                self.string_vars.append(var)
                cb = ttk.Checkbutton(self.frame.interior, variable=var, text=value,
                                     onvalue=value, offvalue="", style="TCheckbutton", takefocus=False)
                cb.pack(side="top", fill="x")
                cb.bind("<ButtonPress-3>", lambda event: self.create_popup(event))
                self.check_buttons.append(cb)
                cb.invoke()
        if top_window:
            top_window.destroy()

    @staticmethod
    def split_entries(entry: str) -> list[str]:
        add_multiple = []
        entries = entry.split(',')
        for word in entries:
            word = word.strip()
            if word.isspace() is False:
                if len(word) != 0:
                    add_multiple.append(word)
        return add_multiple

    def remove_element(self, event) -> None:
        check_button = event.widget
        try:
            string_var = event.widget.cget('onvalue')
        except tk.TclError:
            return
        to_be_removed = None
        for index, value in enumerate(self.check_buttons):
            if value == check_button:
                to_be_removed = index
                value.pack_forget()
        del self.check_buttons[to_be_removed]
        for index, value in enumerate(self.string_vars):
            if value == string_var:
                to_be_removed = index
        del self.string_vars[to_be_removed]

    def remove_all_selected(self):
        to_be_removed = []
        to_be_deleted = []
        for i, v in enumerate(self.string_vars):
            if v.get():
                to_be_removed.append(i)
                for index, btn in enumerate(self.check_buttons):
                    val = btn.cget('onvalue')
                    if val == v.get():
                        to_be_deleted.append(index)
                        btn.pack_forget()
        for i in reversed(to_be_deleted):
            del self.check_buttons[i]
        for i in reversed(to_be_removed):
            del self.string_vars[i]

    def select_elements(self, elements):
        for cbb in self.check_buttons:
            for i in elements:
                if cbb.cget('onvalue') == i:
                    cbb.invoke()

    def get_all_items(self) -> list:
        return [cbb.cget('onvalue') for cbb in self.check_buttons]

    def get_checked_items(self) -> list:
        return [var.get() for var in self.string_vars if var.get()]

    def select_all(self) -> None:
        variables = self.get_checked_items()
        for cbb in self.check_buttons:
            if cbb.cget('onvalue') not in variables:
                cbb.invoke()

    def deselect_all(self) -> None:
        variables = self.get_checked_items()
        for cbb in self.check_buttons:
            if cbb.cget('onvalue') in variables:
                cbb.invoke()


# Testing Purposes ------------------
def print_checked(widget):
    print(widget.get_checked_items())
    vars = widget.get_checked_items()
    x = ""
    for i in vars:
        x += f"{i}:"
    print(x, type(x))


if __name__ == '__main__':
    from Scripts.utils import *
    root = tk.Tk()
    tcl_path = "C:/Users/nmich/Documents/GitHub/Journal/Core/themes/Azure/azure.tcl"
    root.tk.call("source", tcl_path)
    root.tk.call("set_theme", "dark")
    set_window(root, 300, 300, "To Do List", resize=True)

    data = ["This", "Is", "Some", "test", "Infomation", "and", "some", "more"]

    ttk.Button(root, text="Print Checked", style="Accent.TButton", command=lambda: print_checked(test)).pack()
    frame = tk.Frame(root)
    test = CustomToDoList(frame, root, data)
    test.pack()
    frame.pack()

    root.mainloop()
