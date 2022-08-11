# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog


class CustomToDoList(ttk.Frame):
    """Custom Check List that will add check-buttons to every element in a given list.
        Args: root: tk.window,
              todo_list: list,
              title: string,
              width: int
    """

    DEFAULT_FONT = ("Arial", 12)
    ENTRY_COLOR = "#848689"

    def __init__(self, root, title, todo_list: list = None, **kwargs):
        try:
            self.width = kwargs['width']
        except KeyError:
            self.width = 25
        try:
            self.height = kwargs['height']
        except KeyError:
            self.height = 25

        ttk.Frame.__init__(self, root, **kwargs)
        self.root = root
        self.vars = []
        self.check_buttons = []

        ttk.Label(self, text=title, font=self.DEFAULT_FONT).pack(side='top', padx=4, pady=4)

        if todo_list:
            self._initial_creation(todo_list)

    def _initial_creation(self, values: list) -> None:
        for choice in values:
            choice = choice.strip()
            already_added = self.get_all_items()
            if choice not in already_added:
                var = tk.StringVar(value=choice)
                self.vars.append(var)
                cb = ttk.Checkbutton(self, variable=var, text=choice,
                                     onvalue=choice, offvalue="",
                                     width=self.width, style="TCheckbutton", takefocus=False
                                     )
                cb.pack(side="top", fill="x", anchor="w")
                cb.bind("<ButtonPress-3>", lambda event: self.create_popup(event))
                self.check_buttons.append(cb)
        self.deselect_all()

    def create_popup(self, event) -> None:
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Select All", command=lambda: self.select_all())
        menu.add_command(label="Deselect All", command=lambda: self.deselect_all())
        menu.add_command(label="Add Element", command=lambda: self.create_window())
        menu.add_command(label="Remove Element", command=lambda: self.remove_element(event))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def create_window(self) -> None:
        top_window, entry = self.create_pop_up("Add Element", self.root, 100)

        ttk.Button(top_window, text="Add Element", width=21, style="Accent.TButton",
                   command=lambda e=None: self.add_element(entry.get(), top_window)).pack(side='top', padx=4, pady=4)

        entry.bind("<Return>", lambda e=None: self.add_element(entry.get(), top_window))

    def create_pop_up(self, title: str, root: tk.Tk, entry_limit: int) -> (tk.Toplevel, tk.Entry):
        """Creates a top level window for renaming definitions/categories and adding new categories."""
        top_window = tk.Toplevel(root)
        self.set_window(top_window, 200, 100, title)

        ttk.Label(top_window, text=f"{title}: ", font=self.DEFAULT_FONT).pack()

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
    def set_window(root, w, h, title, resize: bool = False, icon: str = None) -> None:
        import sys
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        root.title(title)
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        if sys.platform == "linux":  # To set the icon image, which nothing shows in linux
            pass
        else:
            if icon:
                root.iconphoto(True, tk.PhotoImage(file=icon))
        if resize:
            root.resizable(1, 1)
        else:
            root.resizable(0, 0)
        root.focus_set()

    def add_element(self, entry: str, top_window: tk.Toplevel) -> None:
        add_multiple = []
        if entry == '':
            return
        entries = entry.split(',')
        for word in entries:
            word = word.strip()
            if word.isspace() is False:
                if len(word) != 0:
                    add_multiple.append(word)

        for value in add_multiple:
            already_added = self.get_all_items()
            if value not in already_added:
                var = tk.StringVar(value=value)
                self.vars.append(var)
                cb = ttk.Checkbutton(self, variable=var, text=value,
                                     onvalue=value, offvalue="",
                                     width=self.width, style="TCheckbutton", takefocus=False
                                     )
                cb.pack(side="top", fill="x", anchor="w")
                cb.bind("<ButtonPress-3>", lambda event: self.create_popup(event))
                self.check_buttons.append(cb)
                cb.invoke()
        if top_window:
            top_window.destroy()

    def remove_element(self, event) -> None:
        check_button = event.widget
        string_var = event.widget.cget('onvalue')
        to_be_removed = None
        for index, value in enumerate(self.check_buttons):
            if value == check_button:
                to_be_removed = index
                value.pack_forget()
        del self.check_buttons[to_be_removed]
        for index, value in enumerate(self.vars):
            if value == string_var:
                to_be_removed = index
        del self.vars[to_be_removed]

    def get_all_items(self) -> list:
        return [cbb.cget('onvalue') for cbb in self.check_buttons]

    def get_checked_items(self) -> list:
        return [var.get() for var in self.vars if var.get()]

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
