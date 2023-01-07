# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

import os
import Scripts.utils as utils


class StyleManager:
    all_styles = ['Accent.TButton', 'R.Treeview', 'TNotebook.Tab', 'R.TCombobox', 'H.TLabel', 'R.TLabel', 'S.TLabel',
                  'SF.TLabel', 'R.TEntry', 'Help_Text', 'Listbox', 'Menu', 'Pin_Color', 'TCheckbutton']

    _style_options = ['Accent.TButton', 'R.Treeview', 'TNotebook.Tab', 'R.TCombobox', 'H.TLabel', 'R.TLabel',
                      'S.TLabel', 'SF.TLabel', 'R.TEntry', 'TCheckbutton']

    _default_style = {
        "Accent.TButton": {"foreground": "white"},
        "R.Treeview": {"foreground": "white"},
        "TNotebook.Tab": {"foreground": "white"},
        "R.TCombobox": {"foreground": "white"},
        "H.TLabel": {"foreground": "white"},
        "R.TLabel": {"foreground": "white"},
        "S.TLabel": {"foreground": "white"},
        "SF.TLabel": {"foreground": "white"},
        "R.TEntry": {"foreground": "white"},
        "Help_Text": {"foreground": "white"},
        "Listbox": {"foreground": "white"},
        "Menu": {"foreground": "white"},
        "Pin_Color": {"foreground": "yellow"},
        "TCheckbutton": {"font": "8", "foreground": "white"}
    }
    __slots__ = "root", "journal", "user", "theme", "style", "_path_to_directory", "_path_to_config", "data"

    def __init__(self, journal, root, user, theme):
        self.root = root
        self.journal = journal
        self.user = user
        self.theme = theme

        self.style = ttk.Style(self.root)
        self.style.theme_use(self.theme)

        self._path_to_directory = os.path.join(os.getcwd(), "Data", "Users", self.user)
        self._path_to_config = os.path.join(self._path_to_directory, "style_config.json")
        utils.check_folder_and_create(self._path_to_directory)

        self.data = utils.read_json(self._path_to_config, self._default_style)

        self.root.bind("<<MainWindowCreated>>", lambda event=None: self.apply_style())
        self.root.bind("<<HelpSectionCreated>>", lambda event=None: self.apply_to_help_section())
        self.root.bind("<<ImportExportCreated>>", lambda event=None: self.apply_to_import_export())

    def apply_to_help_section(self):
        # Only apply to the help section text widget
        key = "Help_Text"
        widget = self.journal.find_widgets("Text")
        self.apply_to_top_window(key, widget, type_widget="ttk.Frame")

    def apply_to_import_export(self):
        # Apply to all list boxes
        key = "Listbox"
        widget = self.journal.find_widgets("Listbox")
        self.apply_to_top_window(key, widget, type_widget="ttk.Frame")

    def apply_to_top_window(self, key, widget, type_widget):
        for w in widget:
            if isinstance(w.master, eval(type_widget)):
                for arg, option in self.data[key].items():
                    w[arg] = option

    def apply_style(self):
        """Sets the style."""
        for key in self.data.keys():
            if key in self._style_options:
                for arg, option in self.data[key].items():
                    self.style.configure(key, **{arg: option})
            else:
                if key == "Listbox":
                    for arg, option in self.data[key].items():
                        self.journal.main_layout.list_box[arg] = option
                        if option == "foreground":
                            self.journal.main_layout.list_box["selectforeground"] = option
                elif key == "Menu":
                    widgets = self.journal.find_widgets("Menu")
                    for w in widgets:
                        for arg, option in self.data[key].items():
                            w[arg] = option
                elif key == "Pin_Color":
                    for arg in self.data[key].keys():
                        self.journal.main_layout.pin_color = self.data[key][arg]
                        self.journal.main_layout.update_list()

    def set_style(self, widgets):
        """Sets the style for widgets with that style(key)."""
        widget_iter = iter(widgets)
        try:
            event = widget_iter.__next__()
        except StopIteration:
            return
        data = self.data.copy()
        for _ in data:
            key = event.widget.class_name
            argument = event.widget.type_class
            option = event.widget.get()
            for arg, value in data[key].items():
                if arg == argument:
                    data[key][arg] = option
            try:
                event = widget_iter.__next__()
            except StopIteration:
                pass
        self.dump_style(data)
        self.update_style()

    def get_style(self, key, option):
        """Returns the style of a widget style."""
        return self.data[key][option]

    def dump_style(self, data=None):
        """Dumps the json data of the styles into a file."""
        if data:
            utils.dump_json(self._path_to_config, data)
        else:
            utils.dump_json(self._path_to_config, self.data)

    def update_style(self):
        self.data = utils.read_json(self._path_to_config, self._default_style)
        self.apply_style()

    def reset_to_defaults(self):
        """Resets all styling back to their defaults."""
        self.dump_style(self._default_style)
        self.update_style()
