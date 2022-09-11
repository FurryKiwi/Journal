# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

import os
import Scripts.utils as utils


class BackUpSystem:
    _filename = "backup.json"
    _current_directory = os.getcwd()
    _directory = "Back Ups"
    _passes = 2
    __slots__ = "root", "data_handler", "alert_system", "backup_data", "active", "after_id", "_save_path"

    def __init__(self, root, data_handler, alert_system):
        self.root = root
        self.data_handler = data_handler
        self.alert_system = alert_system

        self.backup_data = None
        self.active = False
        self.after_id = ""
        self._save_path = os.path.join(self._current_directory, self._directory, self._filename)
        utils.check_folder_and_create(os.path.join(self._current_directory, self._directory))

    def cancel_auto(self) -> None:
        """Cancels the 'after' call and generates an event."""
        if self.active:
            self.root.after_cancel(self.after_id)
            self.alert_system.show_alert(("Auto backup has stopped.", "red"))
            self.after_id = ""
            self.active = False
        else:
            self.alert_system.show_alert(("Auto backup has not been started.", "red"))

    def start_auto_backup(self, user: str, time_frame: int) -> None:
        data = self.data_handler.get_data()
        # If not data, cancels auto backup
        if data == {}:
            self.alert_system.show_alert(("Auto backup could not be set with no data.", "red"))
        else:
            self.alert_system.show_alert(("Auto backup has started.", "white"))
            self.active = True
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
            self.backup_user(user, data)

    @staticmethod
    def _check_user_for_backup(user: str, raw_data: dict) -> bool:
        """Checks if a backup exists for the current user."""
        for data in raw_data['users']:
            if user in data.keys():
                return True
        return False

    def backup_user(self, user: str, data: dict) -> None:
        """Back's up the current user with the data associated with user."""
        read_data = utils.read_json(self._save_path, data={"users": []})
        self.backup_data, _ = utils.decode_string(read_data, self._passes, json_object=True)

        # If no data is being passed, then returns false
        if data == {}:
            self.alert_system.show_alert(("No data to backup.", "red"))
        else:
            # Checks if user has a backup already
            check_user = self._check_user_for_backup(user, self.backup_data)
            # If user not in backup, creates a new back up for user
            if not check_user:
                self._create_backup(user, data)
            else:
                self._update_backup(user, data)
            self.alert_system.show_alert(("Backup complete.", "white"))

    def _create_backup(self, user: str, data: dict) -> None:
        """Creates a new backup for the current user."""
        new_data = {user: data}
        self.backup_data['users'].append(new_data)

        encoded_data = utils.encode_string(self.backup_data, self._passes)
        utils.dump_json(self._save_path, encoded_data)

    def _update_backup(self, user: str, data: dict) -> None:
        """Updates the backed up data for the current user."""
        for d in self.backup_data['users']:
            for u in d.keys():
                if u == user:
                    d[u] = data
        encoded_data = utils.encode_string(self.backup_data, self._passes)
        utils.dump_json(self._save_path, encoded_data)

    def restore_user(self, user: str) -> dict | str:
        """Restores the current user's saved backup if there is one. Returns Data."""
        read_data = utils.read_json(self._save_path, data={"users": []})
        raw_data, _ = utils.decode_string(read_data, self._passes, json_object=True)

        check = self._check_user_for_backup(user, raw_data)
        if check:
            for data in raw_data['users']:
                for u in data.keys():
                    if user == u:
                        self.alert_system.show_alert(("Restored user's data.", "white"))
                        return data[u]
        else:
            self.alert_system.show_alert(("No data to restore for user.", "red"))
            return {}
