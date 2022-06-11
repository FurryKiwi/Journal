# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

# BUILT IN PYTHON 3.10 VERSION

import utils
from custom_classes import Layout, BackGround, HelpSection, SettingSection, SearchEngine
from settings import *
from data_model import DataHandler
from login_page import LoginPage
from alert_system import AlertSystem


class Journal:
    _tcl_path = TCL_PATH

    def __init__(self, title: str):
        self.root = None
        self.title = title

        self.data_handler = DataHandler()
        self.search_engine = None
        self.alert_system = None
        self.main_layout = None
        self.login_page = None
        self.canvas = None

        self.create_login_page()

    def create_login_page(self):
        self.login_page = LoginPage(self, self.data_handler)
        self.login_page.run()

    def create_help_view(self):
        help_section = HelpSection(self.root)
        help_section.create_top_window_view()

    def create_settings_view(self):
        settings_section = SettingSection(self.root, self.data_handler)
        settings_section.create_top_window_view()

    def create_file_menu(self, root: tk.Tk) -> None:
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        searchmenu = tk.Menu(menubar, tearoff=0)
        helpmenu = tk.Menu(menubar, tearoff=0)
        settingsmenu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Search", menu=searchmenu)
        menubar.add_cascade(label="Help", menu=helpmenu)
        menubar.add_cascade(label="Settings", menu=settingsmenu)

        filemenu.add_command(label="Add Category", command=lambda: self.main_layout.create_view(state="acategory"))
        filemenu.add_command(label="Clear Database", command=self._on_clearing)
        filemenu.add_command(label="Back Up/Restore",
                             command=lambda: self.data_handler.create_backup_view(self.root, self.main_layout))
        filemenu.add_separator()
        filemenu.add_command(label="Log Out", command=self._log_out)

        searchmenu.add_command(label="Word Search", command=lambda: self.search_engine.create_view())

        helpmenu.add_command(label="Documentation", command=lambda: self.create_help_view())

        settingsmenu.add_command(label="Settings", command=lambda: self.create_settings_view())

    def event_biding(self) -> None:
        self.root.bind("<<AutoBackupRun>>", lambda event=None: self.main_layout.notebook.save_text())
        self.root.bind("<Control-f>", lambda event=None: self.search_engine.create_view())

    def _log_out(self):
        if tk.messagebox.askyesno("Log Out", "Do you want to log out?"):
            self.main_layout.notebook.close_tabs(log_out=True)
            self.data_handler.update_json()
            self.data_handler.log_out_user()
            self.alert_system.cancel_after()
            self.root.destroy()
            self.create_login_page()

    def _on_closing(self) -> None:
        """Handles saving and quiting."""
        if tk.messagebox.askyesno("Quit", "Do you want to quit?"):
            self.main_layout.notebook.close_tabs(log_out=True)
            self.data_handler.update_json()
            self.root.destroy()

    def _on_clearing(self) -> None:
        """Clears the database for the selected user."""
        if tk.messagebox.askyesno("Clear Data", "Do you want to clear data? It's Permanent!"):
            self.alert_system.show_alert(("Data was cleared.", "white"))
            self.main_layout.notebook.close_tabs(clearing=True)
            self.data_handler.clear_data()
            self.main_layout.update_categories()
            self.main_layout.category_box.current(0)
            self.main_layout.update_list()

    def run(self) -> None:
        del self.login_page
        self.root = tk.Tk()
        self.root.tk.call("source", self._tcl_path)
        self.root.tk.call("set_theme", "dark")

        # Create the alert system
        self.alert_system = AlertSystem(self.root)

        # Setup backup system
        self.data_handler.create_backup_system(self.root, self.alert_system)

        # Set window resizable
        utils.set_window(self.root, SCREEN_WIDTH, SCREEN_HEIGHT, self.title, resize=True)

        # Creates a background canvas for everything to be drawn to on top
        self.canvas = BackGround(self.root, heigh=SCREEN_HEIGHT, width=SCREEN_WIDTH, highlightthickness=0, bd=0)

        # Create the file menu
        self.create_file_menu(self.root)

        # Creates the Layout class
        self.main_layout = Layout(self.canvas, self.data_handler, self.alert_system)

        # Create the search engine class
        self.search_engine = SearchEngine(self.main_layout, self.data_handler)

        # Sets the category to the first one and populates the listbox
        self.main_layout.update_list()

        # Calls the main_layout event bidding
        self.main_layout.event_biding()

        # Force windows to set the focus to the main window of the application
        self.root.focus_force()

        # Event checking and mainloop()
        self.event_biding()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()


if __name__ == '__main__':
    Journal(TITLE)
