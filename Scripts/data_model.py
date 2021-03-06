# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

import json
import os
import shutil
import time
import Scripts.utils as utils
from Scripts.backup_system import BackUpSystem, BackUpView


def get_timestamp() -> str:
    """Returns the current date."""
    return time.strftime('%Y-%m-%d', time.localtime())


class LoginHandler:
    """This handles the creating of user's folder directories, and the main config file for the program. Along with
    all the functions handling of the signing in and out of the program."""
    _filename_config = "config.json"
    _user_config = "config_pref.json"
    _secret_config = "unknown.json"
    _current_directory = os.getcwd()
    _main_dir = "Data"
    _config_dir = "Config"
    _main_user_dir = "Users"
    _config_data = {"current": "", "signed_in": 0}
    _user_data = {"entry_limit": 20,
                  "tab_limit": 4,
                  "last_category": "",
                  "default_font": ["Arial", 12]}

    def __init__(self, data_handler):
        self.data_handler = data_handler

        self.last_signed_in = None
        self.signed_in_btn = None
        self.entry_limit = 20  # This will be a constant for validating username and password limit

        # CWD/Data/Config/filename
        self._save_path_config = os.path.join(self._current_directory, self._main_dir, self._config_dir,
                                              self._filename_config)
        self._save_path_config_folder = os.path.join(self._current_directory, self._main_dir, self._config_dir)
        utils.check_folder_and_create(self._save_path_config_folder)
        # CWD/Data/Users
        self._users_folder_path = os.path.join(self._current_directory, self._main_dir, self._main_user_dir)
        utils.check_folder_and_create(self._users_folder_path)

        self._setup_data(utils.read_json(self._save_path_config, self._config_data))

    def get_users(self) -> list[str]:
        directory = self._users_folder_path
        dirlist = [item for item in os.listdir(directory) if os.path.isdir(os.path.join(directory, item))]
        if dirlist:
            return dirlist
        else:
            return ["SignUp"]

    def _setup_data(self, data: dict):
        self.last_signed_in = data['current']
        self.signed_in_btn = data['signed_in']

    def create_new_user(self, new_user: str, new_pw: str) -> bool:
        """Checks if new user already exists, otherwise adds user and pw to the database.
        Returns True if created successfully, otherwise False"""
        if new_user == '':
            return False

        new_user = utils.strip_whitespace(new_user)

        if not utils.check_folder_exists(os.path.join(self._users_folder_path, new_user)):
            # CWD/Data/Users/Username-folder/config_pref.json
            save_path_config = os.path.join(self._users_folder_path, new_user, self._user_config)
            utils.check_folder_and_create(os.path.join(self._users_folder_path, new_user))
            # CWD/Data/Users/Username-folder/unknown.json
            secret = os.path.join(self._users_folder_path, new_user, self._secret_config)

            utils.dump_json(secret, {new_user: new_pw})
            utils.dump_json(save_path_config, self._user_data)
            return True
        else:
            return False

    def validate_login(self, user: str, pw: str, auto: int) -> bool:
        """Checks if user and pw == database data, returns True, otherwise False."""
        if user == '' or user == "SignUp":
            return False
        u, p = self.get_credentials(user)
        if user == u and pw == p:
            self.signed_in_btn = auto
            self.last_signed_in = user
            data = {"current": self.last_signed_in, "signed_in": self.signed_in_btn}
            utils.dump_json(self._save_path_config, data)
            self.data_handler.setup_database(self.last_signed_in, self.signed_in_btn)
            return True
        else:
            return False

    def reset_password(self, user: str, new_user: str, new_pw: str) -> bool:
        if new_user == '':
            return False
        users = self.get_users()
        if new_user in users and new_user != user:
            return False
        if user == "SignUp":
            return False
        user, pw = self.get_credentials(user)
        # CWD/Data/Users/Username/unknown.json
        save_path = os.path.join(self._users_folder_path, user, self._secret_config)
        # CWD/Data/Users/Username
        folder_path = os.path.join(self._users_folder_path, user)
        # CWD/Data/Users/NewUsername
        new_folder_path = os.path.join(self._users_folder_path, new_user)
        with open(save_path, 'r+') as file:
            data = json.load(file)
            data[new_user] = data.pop(user)
            data[new_user] = new_pw
        utils.dump_json(save_path, data)
        # Now to rename the folder
        os.rename(folder_path, new_folder_path)
        # Save the main config file
        self.last_signed_in = ""
        self.signed_in_btn = 0
        utils.dump_json(self._save_path_config, self._config_data)
        return True

    def delete_user(self, user: str) -> bool:
        if user == '':
            return False
        try:
            users = self.get_users()
            for u in users:
                if u == user:
                    try:
                        path = os.path.join(self._users_folder_path, user)
                        shutil.rmtree(path)
                        self.signed_in_btn = 0
                        self.last_signed_in = ""
                        utils.dump_json(self._save_path_config, self._config_data)
                        return True
                    except OSError:
                        return False
        except KeyError:
            return False

    def get_credentials(self, user: str) -> tuple:
        """Returns the selected user and pw from the database for validation."""
        # CWD/Data/Users/Username/unknown.json
        save_path = os.path.join(self._users_folder_path, user, self._secret_config)

        with open(save_path, 'r') as file:
            data = json.load(file)
        temp = [(u, p) for u, p in data.items()]
        user, pw = temp[0]
        return user, pw


class DataHandler:
    _filename = "database.json"
    _current_directory = os.getcwd()
    _export_directory = "Export"
    _export_folder_path = os.path.join(_current_directory, _export_directory)
    _directory = "Data"
    _users_directory = "Users"
    _users_folder_path = os.path.join(_current_directory, _directory, _users_directory)
    _users_config = "config_pref.json"
    _save_path = ""
    _time_frames = {"30": 30000,
                    "60": 60000,
                    "120": 120000}

    def __init__(self):
        self.backup_sys = None

        self.data = {}
        self.config_data = {}

        self.current_user = None
        self.signed_in = None
        self.entry_limit = None
        self.tab_limit = None
        self.last_category = None
        self.default_font = None

        self._data_save_path = None
        self._config_save_path = None

    # Json data functions
    def clear_data(self) -> None:
        """Clears the current user's data."""
        self.data = {}

    def setup_database(self, user: str, signed_in: int) -> None:
        """Grabs the saved data from the json file and set's attributes from it."""
        # CWD/Data/Users/Username/config_pref.json
        self._config_save_path = os.path.join(self._users_folder_path, user, self._users_config)
        # CWD/Data/Users/Username/database.json
        self._data_save_path = os.path.join(self._users_folder_path, user, self._filename)

        config_data = utils.read_config(self._config_save_path)

        self.current_user = user
        self.signed_in = signed_in
        self.entry_limit = config_data['entry_limit']
        self.tab_limit = config_data['tab_limit']
        self.last_category = config_data['last_category']
        self.default_font = config_data['default_font']

        self.data = utils.read_json(self._data_save_path, data={})

    def update_json(self) -> None:
        """Updates the data in the raw_data for the current user."""
        self.config_data['entry_limit'] = self.entry_limit
        self.config_data['tab_limit'] = self.tab_limit
        self.config_data['last_category'] = self.last_category
        self.config_data['default_font'] = self.default_font
        utils.dump_json(self._config_save_path, self.config_data)
        utils.dump_json(self._data_save_path, self.data)

    # Import/Export Functions
    def import_data(self, data: dict, orig_data: dict):
        """Imports only the selected data the user wants to import."""
        try:
            self.backup_data()
            new_data = self.data.copy()
            for key, values in data.items():
                for cat, definitions in orig_data.items():
                    for definition, details in definitions.items():
                        if definition in values:
                            if key in new_data:
                                new_data[key].update({definition: details})
                            else:
                                new_data.update({key: {definition: details}})
            self.data = new_data
            return True
        except KeyError:
            return False

    def export_data(self, data: dict):
        """Exports only the selected data the user wants to export."""
        export_data = {}
        for category, definition_list in data.items():
            for i in definition_list:
                if category in export_data:
                    export_data[category].update({i: [self.get_text_by_definition(category, i),
                                                      self.get_timestamp_by_definition(category, i),
                                                      self.get_tab_font(category, i)]})
                else:
                    export_data.update({category: {
                        i: [self.get_text_by_definition(category, i), self.get_timestamp_by_definition(category, i),
                            self.get_tab_font(category, i)]}})
        export_folder = os.path.join(self._export_folder_path, self.current_user)
        utils.check_folder_and_create(export_folder)
        file_name = "database_exported_" + self.current_user.lower() + ".json"
        export_filepath = os.path.join(export_folder, file_name)
        try:
            utils.dump_json(export_filepath, export_data)
            return True
        except FileNotFoundError:
            return False

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
        entry = utils.strip_whitespace(entry)
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

    def add_definition(self, entry: str, category: str, definition: str) -> bool:
        """Adds/Renames a definition in the data for the current user."""
        if entry == '':
            return False
        if entry.isspace():
            return False
        if category == "Create a Category":
            return False
        # Check if adding a definition that exists
        if entry in self.data[category]:
            return False
        entry = utils.strip_whitespace(entry)
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
        if definition == '' or definition is None:
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

    def set_font(self, font, size) -> None:
        self.default_font = (font, size)

    def set_last_category(self, category: str) -> None:
        self.last_category = category

    def get_last_category(self) -> str | None:
        if self.last_category == '':
            return None
        else:
            return self.last_category

    def get_categories_definitions_formatted(self):
        """Used for populating the export view function."""
        data = {}
        for c in self.data.keys():
            data.update({c: list(self.data[c].keys())})
        return data
