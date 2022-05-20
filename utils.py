try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

import time
import json
import os
from settings import *


def set_folder_directory(cwd: str, directory: str, filename: str) -> str:
    if os.path.isdir(directory):
        return cwd + "\\" + directory + "\\" + filename
    else:
        os.mkdir(directory)
        return cwd + "\\" + directory + "\\" + filename


def dump_json(filepath: str, data: dict) -> None:
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)
        file.truncate()


def read_json(filename, database: bool) -> dict:
    """Read file data from the json file. Other-wise creates a new file."""
    try:
        with open(filename, 'r') as file:
            if os.path.getsize(filename) == 2 or os.path.getsize(filename) == 0:
                return create_json(filename, database)
            return json.load(file)
    except FileNotFoundError:
        return create_json(filename, database)


def create_json(filename, database: bool) -> dict:
    """Creates the json file if it doesn't exist."""
    if database:
        new_data = {"current": "", "signed_in": "", "users": []}
    else:
        new_data = {"users": []}
    with open(filename, 'w') as file:
        json.dump(new_data, file, indent=4)
        file.truncate()
        return new_data


def create_pop_up(title: str, root: tk.Tk) -> (tk.Toplevel, tk.Entry):
    """Creates a top level window for renaming definitions/categories and adding new categories."""
    top_window = tk.Toplevel(root)
    set_window(top_window, 200, 100, title)

    ttk.Label(top_window, text=f"{title}: ", width=50, font=DEFAULT_FONT).pack(side='top')

    entry = tk.Entry(top_window, validate="key", background=ENTRY_COLOR,
                     validatecommand=(root.register(validate_entry), "%P"), font=DEFAULT_FONT, width=21)
    entry.pack(side='top', padx=4, pady=4)

    entry.focus_set()

    return top_window, entry


def validate_entry(entry):
    # valid percent substitutions (from the Tk entry man page)
    # note: you only have to register the ones you need; this
    # example registers them all for illustrative purposes
    #
    # %d = Type of action (1=insert, 0=delete, -1 for others)
    # %i = index of char string to be inserted/deleted, or -1
    # %P = value of the entry if the edit is allowed
    # %s = value of entry prior to editing
    # %S = the text string being inserted or deleted, if any
    # %v = the type of validation that is currently set
    # %V = the type of validation that triggered the callback
    #      (key, focusin, focusout, forced)
    # %W = the tk name of the widget
    if len(entry) <= ENTRY_LIMIT:
        return True
    else:
        return False


def get_time():
    return time.ctime()


def get_current_time(entry):
    entry.delete(0, len(entry.get()))
    entry.insert(0, time.strftime("%B %d, %Y"))


def set_window(root, w, h, title) -> None:
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.title(title)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.resizable(0, 0)
    root.focus_set()
