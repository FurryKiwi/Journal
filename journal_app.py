# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog

# BUILT IN PYTHON 3.10 VERSION
import os
import sys
import Scripts.utils as utils
from Scripts.custom_classes import Layout, BackGround, SearchEngine, ExportView, ImportView
from Scripts.settings import *
from Scripts.data_model import DataHandler, LoginHandler
from Scripts.style_manager import StyleManager
from Scripts.login_page import LoginPage
from Scripts.alert_system import AlertSystem
from Scripts.settings_page import SettingsPage


class Journal:
    _path_to_py_file = sys.argv
    _path_to_py_exe = sys.executable
    __slots__ = "data_handler", "theme_path", "theme", "login_handler", "root", "title", "search_engine", \
                "alert_system", "main_layout", "login_page", "canvas", "menubar", "settings_page", "style", \
                "style_manager", "pack_settings", "export_page", "import_page"

    def __init__(self, title: str, root):
        self.data_handler = DataHandler()
        self.theme_path = self.data_handler.theme["theme_path"]
        self.theme = self.data_handler.theme['theme']
        self.login_handler = LoginHandler(self.data_handler)

        self.root = root
        self.root.tk.call("source", self.theme_path)
        self.root.tk.call("set_theme", "dark")
        self.root.iconbitmap(default=ICON_IMG_ICO)
        self.root.iconify()
        self.root.deiconify()

        self.title = title
        self.search_engine = None
        self.alert_system = None
        self.main_layout = None
        self.login_page = None
        self.canvas = None
        self.menubar = None
        self.settings_page = None
        self.export_page = None
        self.import_page = None

        self.style = None
        self.style_manager = None

        self.pack_settings = []

        self.create_login_page()

    def create_login_page(self):
        self.login_page = LoginPage(self.root, self, self.login_handler)

    def create_file_menu(self, root: tk.Tk) -> None:
        self.menubar = tk.Menu(root)
        menubar = self.menubar
        root.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        searchmenu = tk.Menu(menubar, tearoff=0)
        settingsmenu = tk.Menu(menubar, tearoff=0)
        export_import_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(menubar, tearoff=0)
        screen_menu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Search", menu=searchmenu)
        menubar.add_cascade(label="Settings", menu=settingsmenu)

        filemenu.add_command(label="Add Category", command=lambda: self.main_layout.add_category_view())
        filemenu.add_command(label="Clear Database", command=self._on_clearing)

        filemenu.add_cascade(label="Import/Export", menu=export_import_menu)
        export_import_menu.add_command(label="Import Data", command=self.create_import_page)
        export_import_menu.add_command(label="Export Data", command=self.create_export_page)

        filemenu.add_separator()
        filemenu.add_command(label="Log Out", command=self._log_out)

        searchmenu.add_command(label="Word Search", command=lambda: self.search_engine.create_view())

        settingsmenu.add_command(label="Settings", command=self.create_settings_page)

        settingsmenu.add_cascade(label="Screen Settings", menu=screen_menu)
        screen_menu.add_command(label="Clear Screen", command=lambda: self.unpack_widgets())
        screen_menu.add_command(label="Repack Screen", command=lambda: self.repack_widgets())

        settingsmenu.add_cascade(label="Change Theme", menu=theme_menu)
        theme_menu.add_command(label="Azure Theme", command=lambda: self.azure_theme())
        theme_menu.add_command(label="Sun Valley Theme", command=lambda: self.sun_valley_theme())

    def create_export_page(self):
        if self.export_page is None:
            self.export_page = ExportView(self.root, self.data_handler)
        else:
            try:
                self.export_page.focus_set()
            except tk.TclError:
                self.export_page = ExportView(self.root, self.data_handler)

    def create_import_page(self):
        if self.import_page is None:
            try:
                filepath = tk.filedialog.askopenfilename(filetypes=[("Json Files", ".json")])
                if filepath != '':
                    self.import_page = ImportView(self.root, self.data_handler, filepath, self.main_layout)
            except FileNotFoundError:
                tk.messagebox.showinfo("No File", "Please select a file to open.", parent=self.root)
        else:
            try:
                self.import_page.focus_set()
            except tk.TclError:
                try:
                    filepath = tk.filedialog.askopenfilename(filetypes=[("Json Files", ".json")])
                    if filepath != '':
                        self.import_page = ImportView(self.root, self.data_handler, filepath, self.main_layout)
                except FileNotFoundError:
                    tk.messagebox.showinfo("No File", "Please select a file to open.", parent=self.root)

    def create_settings_page(self):
        if self.settings_page is None:
            self.settings_page = SettingsPage(self.root, self.data_handler, self.canvas,
                                              self.style_manager, self.main_layout)
        else:
            try:
                self.settings_page.focus_set()
            except tk.TclError:
                self.settings_page = SettingsPage(self.root, self.data_handler, self.canvas,
                                                  self.style_manager, self.main_layout)

    def unpack_widgets(self):
        widgets = self.canvas.winfo_children()
        for i in widgets:
            try:
                if i.winfo_class() == "TFrame":
                    self.pack_settings.append(i.pack_info())
                i.pack_forget()
            except tk.TclError:
                return

    def repack_widgets(self):
        widgets = self.canvas.winfo_children()
        try:
            index = 0
            for i in widgets:
                if i.winfo_class() == "TFrame":
                    i.pack(**self.pack_settings[index])
                    index += 1
            self.main_layout.notebook.check_for_unpack()
        except IndexError:
            return

    def azure_theme(self):
        if tk.messagebox.askyesno("Azure Theme", "Are you sure you want to change themes?"):
            self.data_handler.theme["theme"] = AZURE_THEME
            self.data_handler.theme["theme_path"] = AZURE_THEME_PATH
            self._on_restart()
            os.execv(self._path_to_py_exe, ['python'] + self._path_to_py_file)
        else:
            return

    def sun_valley_theme(self):
        if tk.messagebox.askyesno("Sun Valley Theme", "Are you sure you want to change themes?"):
            self.data_handler.theme["theme"] = SUN_VALLEY_THEME
            self.data_handler.theme["theme_path"] = SUN_VALLEY_THEME_PATH
            self._on_restart()
            os.execv(self._path_to_py_exe, ['python'] + self._path_to_py_file)
        else:
            return

    def _log_out(self):
        if tk.messagebox.askyesno("Log Out", "Do you want to log out?", parent=self.root):
            self.canvas.save_image_paths()
            self.main_layout.notebook.close_tabs(log_out=True)
            self.data_handler.set_last_category(self.main_layout.category_box.get())
            self.data_handler.update_json()
            self.data_handler.cancel_backup()
            self.alert_system.cancel_after()
            self.style_manager.dump_style()
            self.canvas.pack_forget()
            menus = self.find_widgets("Menu")
            for i in menus:
                i.delete(0, len(menus))
            if self.settings_page is not None:
                self.settings_page.destroy()
            if self.export_page is not None:
                self.export_page.destroy()
            if self.import_page is not None:
                self.import_page.destroy()
            self.create_login_page()

    def _on_closing(self) -> None:
        """Handles saving and quiting."""
        if tk.messagebox.askyesno("Quit", "Do you want to quit?", parent=self.root):
            self.canvas.save_image_paths()
            self.main_layout.notebook.close_tabs(log_out=True)
            self.data_handler.set_last_category(self.main_layout.category_box.get())
            self.data_handler.update_json()
            self.style_manager.dump_style()
            self.root.destroy()

    def _on_restart(self) -> None:
        self.canvas.save_image_paths()
        self.main_layout.notebook.close_tabs(log_out=True)
        self.data_handler.set_last_category(self.main_layout.category_box.get())
        self.data_handler.update_json()
        self.style_manager.dump_style()

    def _on_clearing(self) -> None:
        """Clears the database for the selected user."""
        if tk.messagebox.askyesno("Clear Data", "Do you want to clear data? It's Permanent!", parent=self.root):
            self.alert_system.show_alert(("Data was cleared.", "white"))
            self.main_layout.notebook.close_tabs(clearing=True)
            self.data_handler.clear_data()
            self.main_layout.update_categories()
            self.main_layout.category_box.current(0)
            self.main_layout.update_list()

    def find_widgets(self, widget):
        """Returns all instances of a specific widget class."""
        toplevel = self.root.winfo_toplevel()  # Get top-level window containing self.
        # Use a list comprehension to filter result.
        selection = [child for child in self.get_all_children(toplevel)
                     if child.winfo_class() == widget]
        return selection

    def get_all_children(self, widget):
        """ Return a list of all the children, if any, of a given widget.  """
        result = []  # Initialize.
        return self._all_children(widget.winfo_children(), result)

    def _all_children(self, children, result):
        """ Recursively append all children of a list of widgets to result. """
        for child in children:
            result.append(child)
            subchildren = child.winfo_children()
            if subchildren:
                self._all_children(subchildren, result)

        return result

    def run(self) -> None:
        # Set window
        utils.set_window(self.root, SCREEN_WIDTH, SCREEN_HEIGHT, self.title, resize=True)
        self.root.minsize(width=800, height=550)
        self.root.bind("<<AutoBackupRun>>", lambda event=None: self.main_layout.notebook.save_text())
        self.root.bind("<Control-f>", lambda event=None: self.search_engine.create_view())

        # Create the style manager class
        self.style_manager = StyleManager(self, self.root, self.data_handler.current_user, self.theme)

        # Create the alert system
        self.alert_system = AlertSystem(self.root)

        # Setup backup system
        self.data_handler.create_backup_system(self.root, self.alert_system)

        # Creates a background canvas for everything to be drawn to on top
        self.canvas = BackGround(self.root, heigh=SCREEN_HEIGHT, width=SCREEN_WIDTH, highlightthickness=0, bd=0)

        # Create the file menu
        self.create_file_menu(self.root)

        # Creates the Layout class
        self.main_layout = Layout(self.root, self.canvas, self.data_handler, self.alert_system)
        # Sets styling for the main part of the layout
        self.root.event_generate("<<MainWindowCreated>>")

        # Create the search engine class
        self.search_engine = SearchEngine(self.main_layout, self.data_handler)

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)


if __name__ == '__main__':
    r = tk.Tk()
    Journal("Journal", r)
    r.mainloop()
