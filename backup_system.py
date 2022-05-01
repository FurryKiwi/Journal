try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

import os
import json
import utils
from settings import *


class BackUpView:
    def __init__(self, root, layout, data_handler):
        self.root = root
        # self.root.attributes('-alpha', 0.7)

        self.main_layout = layout
        self.data_handler = data_handler

        top_level = tk.Toplevel(self.root)
        utils.set_window(top_level, 300, 270, "Back Up/Restore")

        label_frame = ttk.LabelFrame(top_level, text="Back Up and Restore Settings:", padding=15)
        label_frame.pack(pady=4)

        ttk.Label(label_frame, text=f"Create a Back Up:", font=DEFAULT_FONT).pack(side='top', anchor='nw')

        ttk.Button(label_frame, text="Manual Back Up", width=14, style="Accent.TButton",
                   command=lambda: self.data_handler.backup_data()).pack(side='top', anchor='ne', pady=8, padx=15)

        ttk.Label(label_frame, text=f"Restore Last Back Up:", font=DEFAULT_FONT).pack(side='top', anchor='nw')

        ttk.Button(label_frame, text="Restore", width=14, style="Accent.TButton",
                   command=lambda: self.restore_user(top_level)).pack(side='top', anchor='ne', pady=8, padx=15)

        ttk.Label(label_frame, text=f"Auto Back Up:(Secs)", font=DEFAULT_FONT).pack(side='top', anchor='nw')

        time_choice = ttk.Combobox(label_frame, values=["30", "60", "120"], width=3,
                                   font=DEFAULT_FONT, state="readonly")
        time_choice.pack(side='left', anchor='nw', pady=8, padx=15)
        time_choice.current(0)

        ttk.Button(label_frame, text="Cancel", width=7, style="Accent.TButton",
                   command=lambda: self.data_handler.cancel_backup()).pack(side='right', anchor='ne', pady=8,
                                                                           padx=15)

        ttk.Button(label_frame, text="Auto", width=7, style="Accent.TButton",
                   command=lambda: self.data_handler.start_auto_backup(time_choice.get())).pack(side='right',
                                                                                                anchor='ne',
                                                                                                pady=8,
                                                                                                padx=15)

    def restore_user(self, window: tk.Toplevel) -> None:
        """Calls the restore function of the current users data and notifies user."""
        if tk.messagebox.askyesno("Restore", "Are you sure you want to restore?"):
            check = self.data_handler.restore_backup()
            if check:
                self.main_layout.update_categories()
                self.main_layout.set_category_list()
                self.main_layout.update_list()
            window.focus_set()


class BackUpSystem:

    _filename = "backup.json"
    _current_directory = os.getcwd()
    _directory = "Back Ups"
    _save_path = ""

    def __init__(self, root, data_handler):
        self.root = root
        self.data_handler = data_handler

        self.backup_data = None
        self.active = False
        self.after_ids = []
        self._save_path = utils.set_folder_directory(self._current_directory, self._directory, self._filename)

    def cancel_auto(self) -> None:
        """Cancels the 'after' call and generates an event."""
        try:
            self.root.after_cancel(self.after_ids.pop())
            self.root.event_generate("<<AutoBackupStopped>>")
            self.after_ids = []
            self.active = False
        except IndexError:
            self.root.event_generate("<<AutoBackupNotStarted>>")

    def start_auto_backup(self, user: str, time_frame: int) -> None:
        data = self.data_handler.get_data()
        # If not data, cancels auto backup, and generates event for notification to grab
        if data == {}:
            self.root.event_generate("<<AutoBackupNotStartedNoData>>")
        else:
            self.root.event_generate("<<AutoBackupStarted>>")
            self.active = True
            self.auto_backup(user, time_frame)

    def auto_backup(self, user: str, time_frame: int) -> None:
        """Starts an 'after' call to automatically back up the current user."""
        # Every time-run, grabs the current data from the database
        data = self.data_handler.get_data()
        # If not data, cancels auto backup
        if data == {}:
            self.cancel_auto()

        if self.active:
            i_d = self.root.after(time_frame, lambda: self.auto_backup(user, time_frame))
            # id to keep track of which function call the auto back-up is on
            self.after_ids.append(i_d)
            # Tries to back up the user with the current data
            self.backup_user(user, data)

    def _check_user_for_backup(self, user: str) -> bool:
        """Checks if a backup exists for the current user."""
        for data in self.backup_data['users']:
            for users in data.keys():
                if user == users:
                    return True
        return False

    def backup_user(self, user: str, data: dict) -> None:
        """Back's up the current user with the data associated with user."""
        self.backup_data = utils.read_json(self._save_path, False)
        # If no data is being passed, then returns false
        if data == {}:
            self.root.event_generate("<<BackupFailed>>")
        else:
            # Checks if user has a backup already
            check_user = self._check_user_for_backup(user)
            # If user not in backup, creates a new back up for user
            if not check_user:
                self._create_backup(user, data)
                self.root.event_generate("<<BackupSuccess>>")
            else:
                self._update_backup(user, data)
                self.root.event_generate("<<BackupSuccess>>")

    def _create_backup(self, user: str, data: dict) -> None:
        # If user doesn't have existing save data
        new_data = {user: data}
        with open(self._save_path, 'r+') as file:
            file_data = json.load(file)
            file_data['users'].append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)
            file.truncate()

    def _update_backup(self, user: str, data: dict) -> None:
        # If users does have a backup, then it updates the current backup with the data given
        for d in self.backup_data['users']:
            for u in d.keys():
                if u == user:
                    d[u] = data
        utils.dump_json(self._save_path, self.backup_data)

    def restore_user(self, user: str):
        """Restores the current user's saved backup if there is one. Returns Data/False"""
        self.backup_data = utils.read_json(self._save_path, False)
        if len(self.backup_data['users']) > 0:
            for data in self.backup_data['users']:
                for u in data.keys():
                    if user == u:
                        self.root.event_generate("<<RestoreSuccess>>")
                        return data[u]
        else:
            self.root.event_generate("<<RestoreFailed>>")
            return False
