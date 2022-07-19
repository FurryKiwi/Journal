# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

import sys
import time
import json
import os
from Scripts.settings import *


def check_folder_exists(filepath: str) -> bool:
    """Checks if a user folder already exists."""
    if os.path.isdir(filepath):
        return True
    return False


def check_folder_and_create(filepath: str) -> None:
    if os.path.isdir(filepath):
        return
    else:
        os.makedirs(filepath)


def read_txt(filepath: str):
    with open(filepath, 'r') as file:
        return file.readlines()


def read_config(filepath: str):
    with open(filepath, 'r') as file:
        return json.load(file)


def dump_json(filepath: str, data: dict) -> None:
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)
        file.truncate()


def read_json(filename, data: dict) -> dict:
    """Read file data from the json file. Other-wise creates a new file."""
    try:
        with open(filename, 'r') as file:
            if os.path.getsize(filename) == 2 or os.path.getsize(filename) == 0:
                return create_json(filename, data)
            return json.load(file)
    except FileNotFoundError:
        return create_json(filename, data)


def create_json(filename, data: dict) -> dict:
    """Creates the json file if it doesn't exist."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
        file.truncate()
        return data


def create_pop_up(title: str, root: tk.Tk, entry_limit: int) -> (tk.Toplevel, tk.Entry):
    """Creates a top level window for renaming definitions/categories and adding new categories."""
    top_window = tk.Toplevel(root)
    set_window(top_window, 200, 100, title)

    ttk.Label(top_window, text=f"{title}: ", font=DEFAULT_FONT).pack()

    entry = tk.Entry(top_window, validate="key", background=ENTRY_COLOR,
                     validatecommand=(root.register(lambda event: validate_entry(event, entry_limit)), "%P"),
                     font=DEFAULT_FONT, width=21)
    entry.pack(side='top', padx=4, pady=4)

    entry.focus_set()

    return top_window, entry


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


def format_date(date: str) -> str:
    date = str(date)  # Convert from datetime object to string
    month = MONTHS[date[5:7]]
    day = date[8:10]
    year = date[:4]
    return month + " " + day + ", " + year


def get_current_date() -> str:
    date = time.strftime("%m %d %Y")
    month = MONTHS[date[:2]]
    day = date[3:5]
    year = date[6:]
    cur_date = month + " " + day + ", " + year
    return cur_date


def set_window(root, w, h, title, resize: bool = False) -> None:
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.title(title)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    if sys.platform == "linux":  # To set the icon image, which nothing shows in linux
        pass
    else:
        root.iconphoto(True, tk.PhotoImage(file=ICON_IMG_PNG))
    if resize:
        root.resizable(1, 1)
    else:
        root.resizable(0, 0)
    root.focus_set()


def strip_whitespace(entry: str) -> str:
    entry = entry.rstrip()
    entry = entry.lstrip()
    return entry


def stay_on_top(win):
    win.lift()
    win.focus_set()
