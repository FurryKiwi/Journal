# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

import binascii
import time
import json
import os
import base64
import ast
from Scripts.settings import *
from CustomTkWidgets.custom_combobox import CustomComboWithClassName
from CustomTkWidgets.custom_color_picker import ColorPicker


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
    # Used for the help section class
    with open(filepath, 'r') as file:
        return file.readlines()


def read_colors_list(filepath: str):
    try:
        with open(filepath, 'r+') as file:
            data = file.read()
            return eval(data)
    except SyntaxError:
        dump_colors_list(filepath)
        return COLORS


def dump_colors_list(filepath: str):
    with open(filepath, 'w+') as file:
        file.write(str(COLORS))


def read_config(filepath: str):
    with open(filepath, 'r') as file:
        return json.load(file)


def dump_json(filepath: str, data: dict | str) -> None:
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)
        file.truncate()


def read_json(filename, data: dict) -> dict | str:
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
        return data.copy()


def create_pop_up(title: str, root: tk.Tk, entry_limit: int) -> (tk.Toplevel, tk.Entry):
    """Creates a top level window for renaming definitions/categories and adding new categories."""
    top_window = tk.Toplevel(root)
    set_window(top_window, 200, 100, title)

    ttk.Label(top_window, text=f"{title}: ", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack()

    entry = ttk.Entry(top_window, validate="key", style="R.TEntry",
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


def set_window(root, w, h, title, resize: bool = False, offset: tuple[int, int] = None) -> None:
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
    root.focus_force()


def create_labels_grid(frame: tk.Frame | ttk.Frame, text: list, font: tuple[str, int], style: str, pad_y: int,
                       pad_x: int):
    try:
        if not text:
            raise TypeError
        for index, i in enumerate(text):
            ttk.Label(frame, text=f"{i}:", font=font, style=style).grid(column=0, row=index, pady=pad_y, padx=pad_x)
    except TypeError:
        print("Can't have an empty list or dict type.")


def create_combo_grid(frame: tk.Frame | ttk.Frame, keys: list, type_class: str, values: list, font: tuple[str, int],
                      style: str, state: str, pad_y: int, pad_x: int, offset: int = 0) -> tuple[list, list]:
    try:
        if not keys:
            raise TypeError
        combo_list = []
        labels = []
        for index, key in enumerate(keys):
            new = CustomComboWithClassName(frame, key, type_class, values=values, font=font, style=style,
                                           state=state)
            new.grid(column=1, row=index, pady=pad_y, padx=pad_x + offset)
            lab = ColorPicker(frame, key, type_class, text=" ", width=4, height=2, background="black", borderwidth=1,
                              relief='solid')
            lab.grid(column=2, row=index, padx=4, pady=4)
            labels.append(lab)
            combo_list.append(new)
        return combo_list, labels
    except TypeError:
        print("Can't have an empty list, or dict type.")


def create_dynamic_combo(frame: tk.Frame | ttk.Frame, data: dict, font: tuple[str, int], style: str, state: str,
                         pad_y: int, pad_x: int, offset: int = 0):
    """Creates and packs combo boxes to the grid, and returns a dict with key being the label the combo boxes
     is attached to, value being the combo widget object and the last index the last combo box was added to."""
    try:
        if data == {}:
            raise TypeError
        combo_list = {}
        index = 0
        for key, value in data.items():
            new = ttk.Combobox(frame, values=value, font=font, style=style, state=state, class_="TCombobox")
            new.grid(column=1, row=index, pady=pad_y, padx=pad_x + offset)
            combo_list.update({key: new})
            index += 1

        return combo_list, index
    except TypeError:
        print("Can't have an empty dictionary or none-type dict.")


def stay_on_top(win):
    win.lift()
    win.focus_set()


def convert_image_to_base64(image_location: str):
    import base64
    with open(image_location, "rb") as image2string:
        converted_string = base64.b64encode(image2string.read())
    return converted_string


def decode_string(data: str, passes: int = 1, json_object: bool = False) -> tuple[str, bool] | tuple[dict, bool]:
    data_eval = eval(data)
    decoded_string = None
    try:
        for i in range(passes):
            if decoded_string is None:
                decoded = base64.urlsafe_b64decode(data_eval)
                decoded_string = decoded
            else:
                decoded_string = base64.urlsafe_b64decode(decoded_string)
    except binascii.Error:
        return {}, False
    if json_object:
        try:
            decoded_string = decoded_string.decode()
            return ast.literal_eval(str(decoded_string)), True
        except SyntaxError:
            return {}, False
        except ValueError:
            return {}, False
    return str(decoded_string.decode()), True


def encode_string(data: str | int | dict, passes: int = 1) -> str:
    encoded_string = None
    for i in range(passes):
        if encoded_string is None:
            encoded = base64.urlsafe_b64encode(str(data).encode())
            encoded_string = encoded
        else:
            encoded_string = base64.urlsafe_b64encode(encoded_string)
    return str(encoded_string)


# Testing Performance -------------

#
if __name__ == '__main__':
    # print(decode_string(test, 16, True))
    from CustomTkWidgets.custom_scrollable_frames import VerticalScrolledFrame
    import cProfile
    import pstats
    # import itertools
    #
    root = tk.Tk()
    width, height = 800, 500
    set_window(root, width, height, "Test Functions", offset=(0, 100))
    #
    frame = ttk.Frame(root)
    frame.pack(side='top', expand=True, fill='both')

    vs_frame = VerticalScrolledFrame(frame)
    vs_frame.pack(side='top', fill='both', expand=True, pady=10, anchor='center')

    font = ("Arial", 12)
    pady = 15
    padx = 7
    styles = ['Accent.TButton', 'R.Treeview', 'TNotebook.Tab', 'R.TCombobox', 'H.TLabel', 'R.TLabel', 'S.TLabel',
              'SF.TLabel', 'R.TEntry', 'Help_Text', 'Listbox', 'Menu', 'Pin_Color']
    foreground_labels = ['Button FG', 'Export/Import FG', 'Tabs FG', 'Selector Boxes FG', 'Header Labels FG',
                         'Regular Labels FG', 'Settings Headers FG', 'Settings Frames FG', 'Entry FG',
                         'Document Text FG', 'Listbox FG', 'Menu FG', 'Pin Text FG']

    # colors_dir_path = os.path.join(os.getcwd(), "color_options.txt")

    button_values = ['custom', 'red', 'blue', 'green', 'orange', 'white', 'grey', 'black', 'purple', 'brown', 'yellow',
                     'violet']
    #
    # start = time.perf_counter()
    # create_labels_grid(vs_frame.interior, foreground_labels, font, "R.TLabel", pady,
    #                    padx)
    # end = time.perf_counter()
    # print("Time for create_labels_grid: ", end - start)  # 0.009138800029177219
    #
    start = time.perf_counter()
    # with cProfile.Profile() as pr:
    combos = create_combo_grid(vs_frame.interior, styles, "foreground", button_values,
                               font=DEFAULT_FONT, style="R.TCombobox", state="readonly",
                               pad_y=pady, pad_x=padx)
    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()
    # stats.dump_stats(filename="../profile.prof")
    # # combos = create_dynamic_combo(vs_frame.interior, test_dict,
    # #                               font=DEFAULT_FONT, style="R.TCombobox", state="readonly",
    # #                               pad_y=pady, pad_x=padx)
    # combos = create_combo_grid(vs_frame.interior, styles, "foreground", button_values,
    #                            font=DEFAULT_FONT, style="R.TCombobox", state="readonly",
    #                            pad_y=pady, pad_x=padx)
    end = time.perf_counter()
    # # print("Time for create_combo_grid_dict: ", end - start)  # 0.011388599989004433
    print("Time for create_combo_grid: ", end - start)  # 0.011911500012502074
    # # print("Time for create_dynamic_combo: ", end-start)  # 0.011579999991226941
    #
    root.mainloop()
