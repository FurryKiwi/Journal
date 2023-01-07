# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

import time
import os
import Scripts.utils as utils
from CustomTkWidgets.custom_treeview import TreeView
from Scripts.settings import *


class BackUpSystem:
    _current_directory = os.getcwd()
    _directory = "Back Ups"
    _main_directory = os.path.join(_current_directory, _directory)
    _passes = 2
    __slots__ = "root", "data_handler", "alert_system", "backup_data", "active", "after_id", "save_path", "flag", \
                "data_passes", "tree_view", "top_window", "data_passes"

    def __init__(self, root, data_handler, alert_system):
        self.root = root
        self.data_handler = data_handler
        self.alert_system = alert_system

        self.backup_data = None
        self.active = False
        self.after_id = ""
        self.save_path = ""
        self.flag = False
        self.data_passes = None

        self.tree_view = None
        self.top_window = None
        self.data_passes = None
        utils.check_folder_and_create(self._main_directory)

    def cancel_auto(self) -> None:
        """Cancels the 'after' call and generates an event."""
        if self.active:
            self.root.after_cancel(self.after_id)
            if self.alert_system:
                self.alert_system.show_alert(("Auto backup has stopped.", "red"))
            self.after_id = ""
            self.active = False
            self.flag = False
        else:
            if self.alert_system:
                self.alert_system.show_alert(("Auto backup has not been started.", "red"))

    def start_auto_backup(self, user: str, time_frame: int, data_passes) -> None:
        data = self.data_handler.get_data()
        # If no data, cancels auto backup
        if data == {}:
            self.alert_system.show_alert(("Auto backup could not be set with no data.", "red"))
        else:
            self.alert_system.show_alert(("Auto backup has started.", "white"))
            self.active = True
            user_directory = os.path.join(self._main_directory, user)
            utils.check_folder_and_create(user_directory)
            self.save_path = os.path.join(user_directory, (utils.get_current_time() + f"-auto-{user}.json"))
            self.data_passes = data_passes
            self.auto_backup(user, time_frame)

    def auto_backup(self, user: str, time_frame: int) -> None:
        """Starts an 'after' call to automatically back up the current user."""
        # Have to generate an event so the program knows to save the current input from the user.
        self.root.event_generate("<<AutoBackupRun>>")
        # Every time-run, grabs the current data from the database
        data = self.data_handler.get_data()
        # If not data, cancels auto backup
        if data == {}:
            self.cancel_auto()

        if self.active:
            # id to keep track of which function call the auto back-up is on (string)
            self.after_id = self.root.after(time_frame, lambda: self.auto_backup(user, time_frame))
            # Tries to back up the user with the current data
            self.backup_user(user, data, self.data_passes, auto=True)

    def backup_user(self, user: str, data: dict, data_passes, auto: bool = False) -> None:
        """Back's up the current user with the data associated with user."""
        # If no data is being passed, then returns false
        if data == {}:
            self.alert_system.show_alert(("No data to backup.", "red"))
            return
        if not auto:
            user_directory = os.path.join(self._main_directory, user)
            utils.check_folder_and_create(user_directory)
            self.save_path = os.path.join(user_directory, (utils.get_current_time() + f"-manual-{user}.json"))

        # If auto backup has started, but it's the first time, create a new backup
        if auto and not self.flag:
            self._create_backup(data, data_passes)
            self.flag = True
        # After the first the backup is created for auto backup, overwrite the existing one
        elif auto and self.flag:
            self._update_backup(data, data_passes)
        # If calling the manual backup, then create a new backup everytime
        else:
            self._create_backup(data, data_passes)

        if self.alert_system:
            self.alert_system.show_alert(("Backup complete.", "white"))

    def _create_backup(self, data: dict, data_passes) -> None:
        """Creates a new backup for the current user."""
        encoded_data = utils.encode_string(data, data_passes)
        utils.dump_json(self.save_path, encoded_data)

    def _update_backup(self, data: dict, data_passes) -> None:
        """Updates the backed up data for the current user."""
        encoded_data = utils.encode_string(data, data_passes)
        utils.dump_json(self.save_path, encoded_data)

    def restore_user(self, data_passes, top_level):
        """Restores the current user's saved backup if there is one. Returns Data."""
        if self.active:
            self.cancel_auto()
        self.data_passes = data_passes
        path = os.path.join(os.getcwd(), "Back Ups", self.data_handler.current_user)
        filepaths = os.listdir(path)
        self.create_restore_view(filepaths, top_level)

    def create_restore_page(self, filepaths, top_level):
        # Top Frame
        top_frame = ttk.Frame(self.top_window, relief='ridge', borderwidth=2)
        top_frame.pack(side='top', fill='x', anchor='nw', padx=4, pady=4)

        bottom_frame = ttk.Frame(self.top_window, relief='ridge', borderwidth=2)
        bottom_frame.pack(side='top', expand=True, fill='both', anchor='nw', pady=4, padx=4)

        # Left Frame
        left_main_frame = tk.Frame(bottom_frame)
        left_main_frame.pack(side='left', anchor='w', expand=True, fill='both', pady=4, padx=4)
        # Right Frame
        right_main_frame = tk.Frame(bottom_frame)
        right_main_frame.pack(side='right', anchor='e', expand=True, fill='both', padx=4, pady=4)

        ttk.Label(right_main_frame, text="Functions:", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(side='top',
                                                                                                      pady=4,
                                                                                                      padx=4)

        ttk.Label(top_frame, text="Saves Available", font=DEFAULT_FONT_BOLD, style='H.TLabel').pack(pady=5)

        self.tree_view = TreeView(left_main_frame)
        self.tree_view.pack(side='top', anchor='nw', expand=True, fill='both')
        self.tree_view.add_elements("Files", filepaths)
        self.tree_view.see(self.tree_view.children_of_parents[0])

        ttk.Button(right_main_frame, style="Accent.TButton", text="Load", width=18,
                   command=lambda: self.load_restored_data(self.tree_view.item_selected, top_level)).pack(side='top',
                                                                                                          pady=4,
                                                                                                          padx=4)
        ttk.Button(right_main_frame, style="Accent.TButton", text="Cancel", width=18,
                   command=lambda: self.cancel_loading()).pack(side='top', pady=4, padx=4)

    def create_restore_view(self, data_passes, top_level):
        if self.active:
            self.cancel_auto()
        self.data_passes = data_passes
        path = os.path.join(os.getcwd(), "Back Ups", self.data_handler.current_user)
        filepaths = os.listdir(path)
        # Reversing the filepaths
        start = len(filepaths) - 1
        filepaths = [filepaths[i] for i in range(start, -1, -1)]
        if self.top_window is None:
            self.top_window = tk.Toplevel(self.root)
            utils.set_window(self.top_window, 700, 500, "Restore User", parent=self.root, resize=True,
                             offset=(-280, -150))
            self.create_restore_page(filepaths, top_level)
            self.top_window.focus_set()
        else:
            try:
                self.top_window.focus_set()
            except tk.TclError:
                self.top_window = tk.Toplevel(self.root)
                utils.set_window(self.top_window, 700, 500, "Restore User", parent=self.root, resize=True,
                                 offset=(-280, -150))
                self.create_restore_page(filepaths, top_level)
                self.top_window.focus_set()

    def cancel_loading(self):
        self.top_window.destroy()

    def load_restored_data(self, filepath: str, top_level):
        if filepath is None:
            return
        filepath = os.path.join(os.getcwd(), "Back Ups", self.data_handler.current_user, filepath)
        read_data = utils.read_json(filepath, data={})
        raw_data, check = utils.decode_string(read_data, self.data_passes, json_object=True)

        if not check:
            tk.messagebox.showinfo("Error", "Can't restore that data.", parent=top_level)
            return None
        else:
            self.top_window.destroy()
            top_level.focus_set()
            tk.messagebox.showinfo("Restored Data", "Restored user's data.", parent=top_level)
            self.data_handler.restore_data(raw_data)
            self.root.event_generate("<<RestoredData>>")
