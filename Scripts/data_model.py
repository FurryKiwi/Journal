# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

import json
import os
import shutil
import time
import random
import Scripts.utils as utils
from Scripts.settings import *
from Scripts.backup_system import BackUpSystem

USER_DATA = {"entry_limit": 20,
             "tdl_limit": 80,
             "tab_limit": 4,
             "last_category": "",
             "default_font": ["Arial", 12],
             "pinned": {}
             }


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
    _config_passes = 2
    _pw_passes = 6
    _config_data = {"current": utils.encode_string("", _config_passes),
                    "signed_in": utils.encode_string(0, _config_passes)
                    }

    __slots__ = "data_handler", "last_signed_in", "signed_in_btn", "entry_limit", "_save_path_config", \
                "_save_path_config_folder", "_users_folder_path"

    def __init__(self, data_handler):
        self.data_handler = data_handler

        self.last_signed_in = None
        self.signed_in_btn = None
        self.entry_limit = 20

        # CWD/Data/Config/filename
        self._save_path_config = os.path.join(self._current_directory, self._main_dir, self._config_dir,
                                              self._filename_config)
        self._save_path_config_folder = os.path.join(self._current_directory, self._main_dir, self._config_dir)
        utils.check_folder_and_create(self._save_path_config_folder)
        # CWD/Data/Users
        self._users_folder_path = os.path.join(self._current_directory, self._main_dir, self._main_user_dir)
        utils.check_folder_and_create(self._users_folder_path)

        self._setup_data(utils.read_json(self._save_path_config, self._config_data))

    def get_key(self, key: str) -> str:
        return utils.encode_string(key, self._pw_passes)

    def get_users(self) -> list[str]:
        directory = self._users_folder_path
        dirlist = [item for item in os.listdir(directory) if os.path.isdir(os.path.join(directory, item))]
        if dirlist:
            return dirlist
        else:
            return ["SignUp"]

    def _setup_data(self, data):
        try:
            data, _ = utils.decode_string(data, self._config_passes, True)
            self.last_signed_in, _ = utils.decode_string(data['current'], self._config_passes)
            self.signed_in_btn, _ = utils.decode_string(data['signed_in'], self._config_passes)
            self.signed_in_btn = int(self.signed_in_btn)
        except TypeError:
            self.last_signed_in = ""
            self.signed_in_btn = 0

    @staticmethod
    def _gen_random_passes() -> int:
        return random.randint(2, 20)

    def create_new_user(self, new_user: str, new_pw: str, birth: str = None) -> bool:
        """Checks if new user already exists, otherwise adds user and pw to the database.
        Returns True if created successfully, otherwise False"""
        if new_user == '':
            return False

        new_user = new_user.strip()

        if not utils.check_folder_exists(os.path.join(self._users_folder_path, new_user)):
            new_pw = self.get_key(new_pw)
            # CWD/Data/Users/Username-folder/config_pref.json
            save_path_config = os.path.join(self._users_folder_path, new_user, self._user_config)
            utils.check_folder_and_create(os.path.join(self._users_folder_path, new_user))
            # CWD/Data/Users/Username-folder/unknown.json
            secret = os.path.join(self._users_folder_path, new_user, self._secret_config)

            data_passes = self._gen_random_passes()
            data = utils.encode_string({new_user: new_pw, "Data": data_passes}, self._pw_passes)

            utils.dump_json(secret, data)
            utils.dump_json(save_path_config, USER_DATA)
            return True
        else:
            return False

    def validate_login(self, user: str, pw: str, auto: int) -> tuple[bool, str]:
        """Checks if user and pw == database data, returns True, otherwise False."""
        if user == '' or user == "SignUp":
            return False, ""
        u, p = self.get_credentials_data(user)
        pw = self.get_key(pw)
        if user == u and pw == p:
            data_passes = self.get_credentials_data(user, key="Data")
            check, message = self.data_handler.setup_database(user, auto, data_passes)
            self.last_signed_in = user
            self.signed_in_btn = auto
            last_signed_in = utils.encode_string(user, self._config_passes)
            signed_in_btn = utils.encode_string(auto, self._config_passes)
            data = {"current": last_signed_in, "signed_in": signed_in_btn}
            encoded = utils.encode_string(data, self._config_passes)
            utils.dump_json(self._save_path_config, encoded)
            if message != "":
                return True, message
            else:
                return True, ""
        else:
            return False, ""

    def bypass(self, user, auto) -> tuple[bool, str]:
        last_signed_in = utils.encode_string(user, self._config_passes)
        signed_in_btn = utils.encode_string(auto, self._config_passes)
        data = {"current": last_signed_in, "signed_in": signed_in_btn}
        encoded = utils.encode_string(data, self._config_passes)
        utils.dump_json(self._save_path_config, encoded)
        data_passes = self.get_credentials_data(user, key="Data")
        check, message = self.data_handler.setup_database(user, auto, data_passes)
        if message != "":
            return True, message
        return True, ""

    def reset_password(self, user: str, pw: str, new_user: str, new_pw: str) -> bool:
        if len(new_user) < 1:
            return False
        users = self.get_users()
        if new_user in users and new_user != user:
            return False
        if user == "SignUp":
            return False
        u, p = self.get_credentials_data(user)
        pw = self.get_key(pw)
        if p != pw:
            return False
        # CWD/Data/Users/Username/unknown.json
        save_path = os.path.join(self._users_folder_path, u, self._secret_config)
        # CWD/Data/Users/Username
        folder_path = os.path.join(self._users_folder_path, u)
        # CWD/Data/Users/NewUsername
        new_folder_path = os.path.join(self._users_folder_path, new_user)
        new_pw = self.get_key(new_pw)
        with open(save_path, 'r+') as file:
            data = json.load(file)

        data, _ = utils.decode_string(data, self._pw_passes, True)
        data[new_user] = data.pop(user)
        data[new_user] = new_pw
        data = utils.encode_string(data, self._pw_passes)

        utils.dump_json(save_path, data)
        # Now to rename the folder
        if u != new_user:
            os.rename(folder_path, new_folder_path)
        return True

    def delete_user(self, user: str, pw: str) -> bool:
        if user == '':
            return False
        u, p = self.get_credentials_data(user)
        pw = self.get_key(pw)
        if p != pw:
            return False
        try:
            users = self.get_users()
            for u in users:
                if u == user:
                    try:
                        path = os.path.join(self._users_folder_path, user)
                        shutil.rmtree(path)
                        data = utils.encode_string(self._config_data, self._config_passes)
                        utils.dump_json(self._save_path_config, data)
                        return True
                    except OSError:
                        return False
        except KeyError:
            return False

    def get_credentials_data(self, user: str, key: str = None) -> tuple | int:
        """Returns the selected user and pw from the database for validation."""
        # CWD/Data/Users/Username/unknown.json
        save_path = os.path.join(self._users_folder_path, user, self._secret_config)

        with open(save_path, 'r') as file:
            data = json.load(file)
        data, _ = utils.decode_string(data, self._pw_passes, True)
        if key is not None:
            temp = [(d, v) for d, v in data.items() if d == key]
            _, passes = temp[0]
            return passes
        else:
            temp = [(u, p) for u, p in data.items() if u == user]
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
    _theme_config = "theme.json"
    _path_to_config_directory = os.path.join(_current_directory, _directory, "Config")
    _path_to_theme_config = os.path.join(_current_directory, _directory, "Config", _theme_config)
    time_frames = {"30": 30000,
                   "60": 60000,
                   "120": 120000}
    _default_theme_data = {"theme_path": AZURE_THEME_PATH,
                           "theme": AZURE_THEME}
    __slots__ = "backup_sys", "data", "config_data", "current_user", "signed_in", "entry_limit", "tab_limit", \
                "last_category", "default_font", "pinned", "theme", "_data_passes", "_data_save_path", \
                "_config_save_path", "tdl_limit"

    def __init__(self):
        self.backup_sys = None

        self.data = {}
        self.config_data = {}

        self.current_user = None
        self.signed_in = None
        self.entry_limit = None
        self.tdl_limit = None
        self.tab_limit = None
        self.last_category = None
        self.default_font = None
        self.pinned = None
        self.theme = None
        self._data_passes = None

        self._data_save_path = None
        self._config_save_path = None

        self._setup_theme()

    # Json data functions
    def clear_data(self) -> None:
        """Clears the current user's data."""
        self.data = {}

    def _setup_theme(self):
        utils.check_folder_and_create(self._path_to_config_directory)
        self.theme = utils.read_json(self._path_to_theme_config, self._default_theme_data)

    def setup_database(self, user: str, signed_in: str, data_passes: int) -> tuple[bool, str]:
        """Grabs the saved data from the json file and set's attributes from it."""
        # CWD/Data/Users/Username/config_pref.json
        self._config_save_path = os.path.join(self._users_folder_path, user, self._users_config)
        config_data = utils.read_json(self._config_save_path, USER_DATA)

        self.current_user = user
        self.signed_in = signed_in
        self.entry_limit = config_data['entry_limit']
        self.tdl_limit = config_data['tdl_limit']
        self.tab_limit = config_data['tab_limit']
        self.last_category = config_data['last_category']
        self.default_font = config_data['default_font']
        self.pinned = config_data['pinned']

        # CWD/Data/Users/Username/database.json
        self._data_save_path = os.path.join(self._users_folder_path, user, self._filename)
        self._data_passes = data_passes

        data = utils.read_json(self._data_save_path, data={})
        # First time creating
        if data == {}:
            self.data = {}
            return True, ""
        self.data, check = utils.decode_string(data, self._data_passes, json_object=True)
        if not check:
            self.data = {}
            return True, "Database has been corrupted."
        else:
            return True, ""

    def update_json(self) -> None:
        """Updates the data in the raw_data for the current user."""
        self.config_data['entry_limit'] = self.entry_limit
        self.config_data['tdl_limit'] = self.tdl_limit
        self.config_data['tab_limit'] = self.tab_limit
        self.config_data['last_category'] = self.last_category
        self.config_data['default_font'] = self.default_font
        self.config_data['pinned'] = self.pinned
        utils.dump_json(self._config_save_path, self.config_data)

        utils.dump_json(self._path_to_theme_config, self.theme)

        data = utils.encode_string(self.data, self._data_passes)
        utils.dump_json(self._data_save_path, data)

    def reset_default_config(self):
        config_data = USER_DATA
        self.entry_limit = config_data['entry_limit']
        self.tdl_limit = config_data['tdl_limit']
        self.tab_limit = config_data['tab_limit']
        self.last_category = config_data['last_category']
        self.default_font = config_data['default_font']
        utils.dump_json(self._config_save_path, USER_DATA)

    # Import/Export Functions
    def import_data(self, data: dict, orig_data: dict, backup: bool):
        """Imports only the selected data the user wants to import."""
        try:
            if backup:
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
                                                      self.get_tab_font(category, i),
                                                      self.get_tab_type(category, i)]})
                else:
                    export_data.update({category: {
                        i: [self.get_text_by_definition(category, i), self.get_timestamp_by_definition(category, i),
                            self.get_tab_font(category, i), self.get_tab_type(category, i)]}})
        export_folder = os.path.join(self._export_folder_path, self.current_user)
        utils.check_folder_and_create(export_folder)
        file_name = "database_exported_" + self.current_user.lower() + "_" + utils.get_current_time() + ".json"
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

    def backup_data(self) -> None:
        """Calls the backup user method from the BackupSystem with the current user and data."""
        self.backup_sys.backup_user(self.current_user, self.data, self._data_passes)

    def restore_backup(self, top_level):
        """Gets the backed up data from the BackupSystem for the current user.
        Sets the grabbed data and returns boolean."""
        self.backup_sys.create_restore_view(self._data_passes, top_level)

    def restore_data(self, data):
        self.data = data

    def cancel_backup(self) -> None:
        """Calls the cancel backup function."""
        self.backup_sys.cancel_auto()

    def start_auto_backup(self, time_frame: str) -> None:
        """Calls the auto backup function."""
        milliseconds = self.time_frames[time_frame]
        self.backup_sys.start_auto_backup(self.current_user, milliseconds, self._data_passes)

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
        entry = entry.strip()
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

    def add_definition(self, entry: str, category: str, definition: str, tab_type: str = TEXT) -> bool:
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
        entry = entry.strip()
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
                items = list(self.data[category].items())
                # Text, timestamp, font, tab_type
                items.insert(0, (entry, ["", get_timestamp(), self.get_default_font(), tab_type]))
                self.data[category] = dict(items)
                return True
        except KeyError:
            return False

    def pin_definition(self, category, definition):
        items = list(self.data[category].items())
        items.insert(0, (definition, self.data[category][definition]))
        self.data[category] = dict(items)
        if category in self.pinned.keys():
            self.pinned[category] = definition
        else:
            self.pinned.update({category: definition})

    def remove_pin(self, category):
        del self.pinned[category]

    def get_default_font(self):
        return self.default_font

    def paste_definition(self, category: str, definition_list: list) -> bool:
        hits = 0
        for dic in definition_list:
            for definition, values in dic.items():
                if definition == '' or definition is None:
                    hits += 1
                if definition not in self.data[category]:
                    text = values[0]
                    time_stamp = values[1]
                    font = values[2]
                    tab_type = values[3]
                    self.data[category].update({definition: [text, time_stamp, font, tab_type]})
                else:
                    hits += 1
        if hits == len(definition_list):
            return False
        else:
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
        except AttributeError:
            return ["Create a Category"]
        except TypeError:
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

    def get_tab_type(self, category, definition):
        try:
            return self.data[category][definition][3]
        except IndexError:
            return TEXT

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
