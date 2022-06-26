# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

import json
import os
import time
import utils
from backup_system import BackUpSystem, BackUpView


def get_timestamp() -> str:
    """Returns the current date."""
    return time.strftime('%Y-%m-%d', time.localtime())


class DataHandler:

    _filename = "database.json"
    _current_directory = os.getcwd()
    _directory = "Data"
    _save_path = ""
    _time_frames = {"30": 30000,
                    "60": 60000,
                    "120": 120000}

    def __init__(self):
        self.backup_sys = None

        self.data = {}
        self.raw_data = {}
        self.current_user = None
        self.signed_in = None
        self.entry_limit = None
        self.tab_limit = None
        self.tab_font = None
        self.default_font = None

        self._save_path = utils.set_folder_directory(self._current_directory, self._directory, self._filename)

        self._setup_database()

    # Json data functions
    def clear_data(self) -> None:
        """Clears the current user's data."""
        self.data = {}

    def _setup_database(self) -> None:
        """Grabs the saved data from the json file and set's attributes from it."""
        self.raw_data = utils.read_json(self._save_path, True)
        if self.raw_data['current']:
            self.current_user = self.raw_data['current']
        else:
            self.current_user = ''
        if self.raw_data['signed_in']:
            self.signed_in = self.raw_data['signed_in']
        else:
            self.signed_in = ''
        self.entry_limit = self.raw_data['entry_limit']
        self.tab_limit = self.raw_data['tab_limit']
        self.default_font = self.raw_data['default_font']

    def _setup_user_data(self, user: str) -> None:
        """Sets the self_data for the current user from the database."""
        self.current_user = user
        for d in self.raw_data['users']:
            for k, v in d.items():
                if k == self.current_user:
                    self.data = d['data']

    def update_json(self) -> None:
        """Updates the data in the raw_data for the current user."""
        for d in self.raw_data['users']:
            for user in d.keys():
                if user == self.current_user:
                    d["data"] = self.data
        self.raw_data['current'] = self.current_user
        self.raw_data['signed_in'] = self.signed_in
        self.raw_data['entry_limit'] = self.entry_limit
        self.raw_data['tab_limit'] = self.tab_limit
        self.raw_data['default_font'] = self.default_font
        utils.dump_json(self._save_path, self.raw_data)

    # Back up Functions
    def create_backup_system(self, root, alert_system) -> None:
        """Creates the backup system for the current user."""
        self.backup_sys = BackUpSystem(root, self, alert_system)

    def create_backup_view(self, root, main_layout):
        """Creates the backup view page."""
        BackUpView(root, main_layout, self)

    def backup_data(self) -> None:
        """Calls the backup user method from the BackupSystem with the current user and data."""
        self.backup_sys.backup_user(self.current_user, self.data)

    def restore_backup(self) -> bool:
        """Gets the backed up data from the BackupSystem for the current user.
        Sets the grabbed data and returns boolean."""
        temp_data = self.backup_sys.restore_user(self.current_user)
        if temp_data != {}:
            self.data = temp_data
            return True
        else:
            return False

    def cancel_backup(self) -> None:
        """Calls the cancel backup function."""
        self.backup_sys.cancel_auto()

    def start_auto_backup(self, time_frame: str) -> None:
        """Calls the auto backup function."""
        milliseconds = self._time_frames[time_frame]
        self.backup_sys.start_auto_backup(self.current_user, milliseconds)

    def get_data(self) -> dict:
        return self.data

    # Login Functions
    def create_new_user(self, new_user: str, new_pw: str) -> bool:
        """Checks if new user already exists, otherwise adds user and pw to the database.
        Returns True if created successfully, otherwise False"""
        if new_user == '':
            return False
        new_user = self.strip_whitespace(new_user)
        user, pw = self.get_credentials(new_user)

        if new_user not in user:
            new_data = {"data": {}, new_user: new_pw}
            with open(self._save_path, 'r+') as file:
                file_data = json.load(file)
                file_data['current'] = self.current_user
                file_data['users'].append(new_data)
                file.seek(0)
                json.dump(file_data, file, indent=4)
                file.truncate()
            self.raw_data = utils.read_json(self._save_path, True)
            return True
        else:
            return False

    def log_out_user(self) -> None:
        """Resets the current data used from the previous user and sets back up the database."""
        self.cancel_backup()
        self.backup_sys = None
        self.data = {}
        self.raw_data = None
        self._setup_database()

    def validate_login(self, user: str, pw: str, auto: int) -> bool:
        """Checks if user and pw == database data, returns True, otherwise False."""
        if user == '':
            return False
        u, p = self.get_credentials(user)
        if user == u and pw == p:
            self._setup_user_data(user)
            self.signed_in = auto
            self.raw_data['signed_in'] = self.signed_in
            return True
        else:
            return False

    def reset_password(self, user: str, new_user: str, new_pw: str) -> bool:
        if new_user == '':
            return False
        for data in self.raw_data['users']:
            if user in data.keys():
                data[new_user] = data.pop(user)
                data[new_user] = new_pw
                self.raw_data['signed_in'] = 0
                self.raw_data['current'] = new_user
                utils.dump_json(self._save_path, self.raw_data)
                self.raw_data = utils.read_json(self._save_path, True)
                return True
        else:
            return False

    def delete_user(self, user: str) -> bool:
        if user == '':
            return False
        try:
            for index, data in enumerate(self.raw_data['users']):
                if user in data.keys():
                    del self.raw_data['users'][index]
                    self.raw_data['current'] = ""
                    utils.dump_json(self._save_path, self.raw_data)
                    self.raw_data = utils.read_json(self._save_path, True)
                    return True
        except KeyError:
            return False

    def get_users(self) -> list:
        """Returns all the created users in the database to fill combobox."""
        if not self.raw_data['users']:
            return ["SignUp"]
        else:
            temp_list = []
            for data in self.raw_data['users']:
                for user in data.keys():
                    if user != "data":
                        temp_list.append(user)
            return temp_list

    def get_credentials(self, user: str) -> tuple:
        """Returns the selected user and pw from the database for validation."""
        for data in self.raw_data['users']:
            for users, v in data.items():
                if user == users:
                    return users, v
        return "", ""

    # Getting/Setting of data functions
    def add_category(self, entry: str, category: str) -> bool:
        """Adds/Renames a category in the data for the current user."""
        if entry == '':
            return False
        if entry.isspace():
            return False
        # Check if adding a category to an existing category
        if entry in self.data.keys():
            return False
        entry = self.strip_whitespace(entry)
        try:
            if category in self.data.keys():
                # If renaming a category
                index = list(self.data.keys()).index(category)
                items = list(self.data.items())
                items.insert(index, (entry, self.data[category]))
                self.data = dict(items)
                self.data.pop(category)
                return True
            else:
                # Adding a new category
                self.data.update({entry: {}})
                return True
        except KeyError:
            return False

    @staticmethod
    def strip_whitespace(entry: str) -> str:
        entry = entry.rstrip()
        entry = entry.lstrip()
        return entry

    def add_definition(self, entry: str, category: str, definition: str) -> bool:
        """Adds/Renames a definition in the data for the current user."""
        if entry == '':
            return False
        if entry.isspace():
            return False
        # Check if adding a definition that exists
        if entry in self.data[category]:
            return False
        entry = self.strip_whitespace(entry)
        try:
            if definition in self.data[category]:
                # If renaming an existing definition
                index = list(self.data[category].keys()).index(definition)
                items = list(self.data[category].items())
                items.insert(index, (entry, self.data[category][definition]))
                self.data[category] = dict(items)
                self.data[category].pop(definition)
                return True
            else:
                # Add new definition
                self.data[category].update({entry: ["", get_timestamp(), self.get_default_font()]})
                return True
        except KeyError:
            return False

    def get_default_font(self):
        return self.default_font

    def paste_definition(self, category: str, definition: str, text: str, time_stamp: str, font: tuple) -> bool:
        if definition == '':
            return False
        # Check if adding a definition that exists
        if definition in self.data[category]:
            return False
        else:
            self.data[category].update({definition: [text, time_stamp, font]})
            return True

    def add_text(self, category: str, definition: str, text: str) -> None:
        self.data[category][definition][0] = text

    def set_tab_font(self, category, definition, font: tuple) -> None:
        self.data[category][definition][2] = font

    def update_listbox(self, new_order: list, category: str) -> None:
        """Creates a new dictionary with the dataset with the new order of elements.
        Used for when the indexes in the listbox changes."""
        new_list = list()
        index = 0
        for text in new_order:
            new_list.insert(index, (text, self.data[category][text]))
            index += 1
        self.data[category] = dict(new_list)

    def delete_category(self, category: str) -> bool:
        try:
            del self.data[category]
            return True
        except KeyError:
            return False

    def delete_definition(self, category: str, definition: list) -> bool:
        try:
            for i in definition:
                del self.data[category][i]
            return True
        except KeyError:
            return False

    def get_categories_by_list(self) -> list:
        try:
            if self.data != {}:
                return list(self.data.keys())
            else:
                return ["Create a Category"]
        except AttributeError or TypeError:
            return ["Create a Category"]

    def get_definitions_by_list(self, category: str) -> list:
        try:
            return list(self.data[category].keys())
        except KeyError:
            return []

    def get_text_by_definition(self, category: str, definition: str) -> str:
        return self.data[category][definition][0]

    def get_timestamp_by_definition(self, category: str, definition: str) -> str:
        return self.data[category][definition][1]

    def get_tab_font(self, category, definition) -> None:
        return self.data[category][definition][2]

    def set_font(self, font, size):
        self.default_font = (font, size)
