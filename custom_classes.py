try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

import utils
from settings import *


class BackGround(tk.Canvas):

    def __init__(self, root, *args, **kwargs):
        tk.Canvas.__init__(self, root, *args, **kwargs)
        self.root = root
        self.background_img = tk.PhotoImage(file=BACKGROUND_IMG)
        self.create_image(400, 300, image=self.background_img)
        self.pack(expand=True, fill="both")


class TabArea(tk.Frame):

    def __init__(self, notebook, data_handler, category, definition, alert_system, *args, **kwargs):
        tk.Frame.__init__(self, notebook, *args, **kwargs)
        self.data_handler = data_handler
        self.notebook = notebook
        self.alert_system = alert_system

        text_frame = tk.Frame(self, borderwidth=1, relief="sunken")
        bottom_frame = tk.Frame(self)

        # Create the text area for text frame
        self.text_area = tk.Text(text_frame, font=DEFAULT_FONT, padx=2, spacing3=2, wrap=tk.WORD, undo=True)
        self.text_area.insert(tk.END, self.data_handler.get_text_by_definition(category, definition))

        # Create the scrollbar for the text
        scroll_bar = ttk.Scrollbar(text_frame, orient='vertical', command=self.text_area.yview)
        self.text_area.config(yscrollcommand=scroll_bar.set)

        # Bottom Frame layout
        label = ttk.Label(bottom_frame,
                          text=f"Created: {self.data_handler.get_timestamp_by_definition(category, definition)}")
        self.save_btn = ttk.Button(bottom_frame, text="Save", style="Accent.TButton",
                                   command=lambda: self.save_text(category, definition,
                                                                  self.text_area.get(1.0, "end-1c")))

        scroll_bar.pack(in_=text_frame, side='right', fill='y', expand=False)
        self.text_area.pack(in_=text_frame, side='left', fill='both', expand=True, padx=4)

        label.pack(side="left", pady=4, padx=4)
        self.save_btn.pack(side="left", pady=6, padx=120)

        bottom_frame.pack(side="bottom", fill='x')
        text_frame.pack(side='top', fill='x')

        self.text_area.bind("<End>",
                            lambda event=None: self.notebook.close_tabs(tab_id=self.notebook.get_tab_ids([definition])))

    def save_text(self, category: str, definition: str, text: str) -> None:
        """Save the entered text to the database."""
        self.data_handler.add_text(category, definition, text)
        self.data_handler.update_json()
        self.alert_system.show_alert(("Entry has been saved.", "white"))


class CustomListBox(tk.Listbox):

    def __init__(self, root, data_handler, category, **kw):
        kw['selectmode'] = tk.EXTENDED
        tk.Listbox.__init__(self, root, kw)
        self.root = root
        self.data_handler = data_handler
        self.category = category
        self.bind('<Button-1>', self.set_current)
        self.bind('<Control-1>', self.toggle_selection)
        self.bind('<B1-Motion>', self.shift_selection)
        self.selection = False
        self.shifting = False
        self.ctrl_clicked = False
        self.unlock_shifting()

    def save_new_order(self):
        new_list_order = list(self.get(0, tk.END))
        self.data_handler.update_listbox(new_list_order, self.category)

    def set_current(self, event):
        self.ctrl_clicked = False
        i = self.nearest(event.y)
        self.selection = self.selection_includes(i)

    def toggle_selection(self, event):
        self.ctrl_clicked = True

    def move_item(self, source, target):
        if not self.ctrl_clicked:
            item = self.get(source)
            self.delete(source)
            self.insert(target, item)

    def unlock_shifting(self):
        self.shifting = False

    def lock_shifting(self):
        self.shifting = True

    def shift_selection(self, event):
        if self.ctrl_clicked:
            return "break"

        selection = self.curselection()
        if not self.selection or len(selection) == 0:
            return "break"

        if self.shifting:
            return "break"

        selection_range = range(min(selection), max(selection))
        current_index = self.nearest(event.y)

        line_height = 15
        bottom_y = self.winfo_height()
        if event.y >= bottom_y - line_height:
            self.lock_shifting()
            self.see(self.nearest(bottom_y - line_height) + 1)
            self.root.after(500, self.unlock_shifting)
        if event.y <= line_height:
            self.lock_shifting()
            self.see(self.nearest(line_height) - 1)
            self.root.after(500, self.unlock_shifting)

        if current_index < min(selection):
            self.lock_shifting()
            not_in_index = 0
            for i in selection_range[::-1]:
                if not self.selection_includes(i):
                    self.move_item(i, max(selection) - not_in_index)
                    not_in_index += 1
            current_index = min(selection) - 1
            self.move_item(current_index, current_index + len(selection))
            self.save_new_order()
        elif current_index > max(selection):
            self.lock_shifting()
            not_in_index = 0
            for i in selection_range:
                if not self.selection_includes(i):
                    self.move_item(i, min(selection) + not_in_index)
                    not_in_index += 1
            current_index = max(selection) + 1
            self.move_item(current_index, current_index - len(selection))
            self.save_new_order()
        self.unlock_shifting()
        return "break"


class Layout(tk.Frame):

    def __init__(self, root, data_handler, alert_system, **kwargs):
        tk.Frame.__init__(self, root, **kwargs)
        self.root = root
        self.data_handler = data_handler
        self.alert_system = alert_system
        self.alert_system.main_layout = self

        parent_frame = ttk.Frame(self.root, relief="ridge", borderwidth=2)
        parent_frame.pack(anchor='nw', fill='x', pady=4, padx=4)

        self.category_frame = ttk.Frame(parent_frame, height=5)
        self.category_frame.pack(side='left', anchor='w')

        self.tool_frame = ttk.Frame(parent_frame, height=5)
        self.tool_frame.pack(side='right', anchor='e')

        tk.Label(self.category_frame, text="Select Category:", font=DEFAULT_FONT).grid(row=0, column=0)

        # Create the drop-down category
        self.category_box = ttk.Combobox(self.category_frame, values=self.data_handler.get_categories_by_list(),
                                         font=DEFAULT_FONT, state="readonly")
        self.category_box.grid(row=1, column=0, padx=4, pady=4)
        self.category_box.current(0)

        tk.Label(self.category_frame, text="Alerts:", font=DEFAULT_FONT).grid(row=0, column=1, rowspan=2)

        tk.Label(self.tool_frame, text=f"User: {self.data_handler.current_user}", font=DEFAULT_FONT).pack(side='left',
                                                                                                          anchor='e',
                                                                                                          padx=4)

        # listbox frame
        listbox_frame = ttk.Frame(self.root, width=50,
                                  height=SCREEN_HEIGHT, relief="ridge", borderwidth=2)
        listbox_frame.pack(fill='both', side='left', padx=8, pady=8)

        tk.Label(listbox_frame, text="Add Definitions:", font=DEFAULT_FONT).pack()

        # Create the entry and button to add definitions
        self.def_entry = tk.Entry(listbox_frame, validate="key",
                                  validatecommand=(self.root.register(utils.validate_entry), "%P"), font=DEFAULT_FONT,
                                  width=21, background=ENTRY_COLOR)
        self.def_entry.pack(pady=4)

        self.add_definition_btn = ttk.Button(listbox_frame, style="Accent.TButton", text="Add Definition", width=24,
                                             command=lambda: self.add_definition(
                                                 self.def_entry.get(),
                                                 self.category_box.get()))
        self.add_definition_btn.pack(side='top', padx=4, pady=4)

        # Create the listbox to display all the definitions
        self.list_box = CustomListBox(listbox_frame, width=20, height=100, font=DEFAULT_FONT,
                                      activestyle=tk.DOTBOX, data_handler=self.data_handler,
                                      category=self.category_box.current(0))
        self.list_box.pack(side='top', fill='both', expand=True, pady=4, padx=4)
        self.list_box.configure(highlightcolor=BLACK)

        # Create the definition scrollbar
        def_scroll_bar = ttk.Scrollbar(self.list_box)
        def_scroll_bar.pack(side='right', fill='y')
        def_scroll_bar.config(command=self.list_box.yview)

        self.list_box.config(yscrollcommand=def_scroll_bar.set)

        self.notebook = CustomNotebook(self.root, data_handler=self.data_handler, alert_system=self.alert_system,
                                       width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

    # Class Functions
    def delete_category(self) -> None:
        """Deletion of categories."""
        if tk.messagebox.askyesno("Are you sure?", "Deleting is permanent!"):
            category = self.category_box.get()
            definitions = self.data_handler.get_definitions_by_list(category)

            check = self.data_handler.delete_category(category)
            if check:
                close_list = self.notebook.get_tab_ids(definitions)
                self.notebook.close_tabs(close_list=close_list)
                self.update_categories()
                self.set_category_list()
                del close_list
            else:
                self.alert_system.show_alert(("Category doesn't exist.", "red"))

    def set_category_list(self, category=None) -> None:
        """Set the category list to specified category or to the first one in the list."""
        if category:
            temp_list = self.category_box['values']
            for index, i_d in enumerate(temp_list):
                if i_d == category:
                    self.category_box.current(index)
        else:
            self.category_box.current(0)
        self.update_list()

    def add_category(self, entry: str, window: tk.Toplevel, category=None) -> None:
        """Save the category list to database."""
        check = self.data_handler.add_category(entry, category)
        if check:
            window.destroy()
            self.update_categories()
            self.set_category_list(entry)
        else:
            self.alert_system.show_alert(("Could not save category.", "red"))

    def add_definition(self, entry: str, category: str, definition=None, window=None) -> None:
        """Adds the definition entry to the database, calls the update list method,
           and closes the toplevel window if opened. Also checks if renaming a definition."""
        # Checks if definition is getting renamed
        if definition is not None:
            active_tabs = self.notebook.get_active_tabs()
            for text, i_d in active_tabs.items():
                # Closes the tab that's being renamed
                if definition == text:
                    self.notebook.close_tabs(tab_id=i_d)

        check = self.data_handler.add_definition(entry, category, definition)
        if check:
            self.update_list()
        else:
            self.alert_system.show_alert(("Could not save definition.", "red"))
        self.def_entry.delete(0, len(entry))
        self.def_entry.focus_set()
        if window:
            window.destroy()

    def delete_definition(self, instance: tk.Listbox, index: list) -> None:
        """Deletion of definitions from the given category list."""
        if tk.messagebox.askyesno("Are you sure?", "Deleting is permanent!"):
            category = self.category_box.get()

            # Appends selected definitions to a list
            temp_list = []
            for i in index:
                definition = instance.get(i)
                temp_list.append(definition)

            check = self.data_handler.delete_definition(category, temp_list)
            if check:
                close_list = self.notebook.get_tab_ids(temp_list)
                self.notebook.close_tabs(close_list=close_list)
                self.update_list()
                del temp_list
                del close_list
            else:
                self.alert_system.show_alert(("Definition doesn't exist.", "red"))

    def create_view(self, instance: tk.Listbox = None, index: list = None, state: str = None):
        """Creates the pop-up window for renaming, adding of categories and renaming definitions."""
        category = self.category_box.get()
        if state == "rdefinition":
            definition = instance.get(index)
            top_window, entry = utils.create_pop_up("Rename Definition", self.root)

            ttk.Button(top_window, text="Save Definition", width=21, style="Accent.TButton",
                       command=lambda e=None: self.add_definition(entry.get(), category, definition,
                                                                  window=top_window)).pack(side='top', padx=4, pady=4)

            entry.bind("<Return>",
                       lambda e=None: self.add_definition(entry.get(), category, definition, window=top_window))
            entry.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))

        elif state == "rcategory":
            top_window, entry = utils.create_pop_up("Rename Category", self.root)

            ttk.Button(top_window, text="Save Category", width=21, style="Accent.TButton",
                       command=lambda: self.add_category(entry.get(), top_window,
                                                         category)).pack(side='top', padx=4, pady=4)

            entry.bind("<Return>", lambda e=None: self.add_category(entry.get(), top_window, category))

        elif state == "acategory":
            top_window, entry = utils.create_pop_up("Add Category", self.root)

            ttk.Button(top_window, text="Save Category", width=21, style="Accent.TButton",
                       command=lambda: self.add_category(entry.get(),
                                                         top_window)).pack(side='top', padx=4, pady=4)
            entry.bind("<Return>", lambda e=None: self.add_category(entry.get(), top_window))

    def event_biding(self) -> None:
        """Handles the binding of events to specific widgets."""
        self.category_box.bind("<<ComboboxSelected>>", lambda event=None: self.update_list())

        self.list_box.bind("<Double-1>", lambda event=None: self.notebook.add_tab(
            self.category_box.get(), self.get_list_box_item()))

        self.list_box.bind("<Return>", lambda event=None: self.notebook.add_tab(
            self.category_box.get(), self.get_list_box_item()))

        self.def_entry.bind("<Return>", lambda event=None: self.add_definition_btn.invoke())
        self.def_entry.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))
        self.list_box.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))
        self.category_box.bind("<ButtonPress-3>", lambda event=None: self.pop_up_menu(event))

    def pop_up_menu(self, event: (tk.Listbox, ttk.Combobox, tk.Entry)) -> None:
        """Create a popup menu by right-clicking with options."""
        instance = event.widget
        # Listbox drop down menu
        if isinstance(instance, tk.Listbox):
            index = instance.curselection()
            if index:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Delete", command=lambda: self.delete_definition(instance, index))
                if len(index) == 1:
                    menu.add_command(label="Rename",
                                     command=lambda: self.create_view(instance, index, state='rdefinition'))
                try:
                    menu.tk_popup(event.x_root, event.y_root)
                finally:
                    menu.grab_release()
        # Category drop down menu
        if isinstance(instance, ttk.Combobox):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Delete", command=self.delete_category)
            menu.add_command(label="Rename", command=lambda: self.create_view(state="rcategory"))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
        # Definition entry drop down menu
        if isinstance(instance, tk.Entry):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Add Date", command=lambda: utils.get_current_time(instance))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def get_list_box_item(self) -> str:
        """Returns the selected list box item."""
        index = self.list_box.curselection()
        if len(index) > 1:
            for i in index:
                return self.list_box.get(i)
        else:
            definition = self.list_box.get(index)
            return definition

    def update_list(self) -> None:
        """Updates the definition list from selected category."""
        category = self.category_box.get()
        if self.list_box.size() != 0:
            self.list_box.delete(0, self.list_box.size())
        temp_list = self.data_handler.get_definitions_by_list(category)
        self.list_box.category = category
        if temp_list is not None:
            for definition in temp_list:
                self.list_box.insert(tk.END, definition)
        self.category_box.selection_clear()

    def update_categories(self) -> None:
        """Updates the category selection box with given values from the database."""
        self.category_box.config(values=self.data_handler.get_categories_by_list())


class CustomNotebook(ttk.Notebook):

    def __init__(self, root, alert_system, data_handler, *args, **kwargs):

        kwargs["style"] = "TNotebook"
        ttk.Notebook.__init__(self, root, *args, **kwargs)
        self.root = root
        self.data_handler = data_handler
        self.alert_system = alert_system

        self.style = ttk.Style()
        self.__initialize_custom_style()

        self._active = None
        self.packed = False
        self.frames = {}

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
        self.bind("<<NotebookTabClosed>>", lambda e=None: self.check_for_unpack())

    def add_tab(self, category: str, definition: str) -> None:
        """Calls the create_tab method to create elements and adds them to the notebook."""
        if not self.packed:
            self.pack_notebook()
        active_tabs = self.get_active_tabs()

        if len(active_tabs) < TAB_LIMIT:
            # Creates a tab if the tab is not opened on the notebook
            if definition not in active_tabs:
                frame = self.create_tab(category, definition)
                self.frames.update({definition: frame})
                self.add(frame, text=definition)
                self.select(frame)
            # Other-wise sets the focused on the specified definition user is trying to open again
            else:
                self.set_tab(definition, active_tabs)
        else:
            # If tab limit is executed, focus will be set to specified tab.
            if definition in active_tabs:
                self.set_tab(definition, active_tabs)
            else:
                self.alert_system.show_alert(("Tab limit has been met.", "red"))

    def create_tab(self, category: str, definition: str) -> tk.Frame:
        """Creates the elements for the tab from the add tab method."""
        return TabArea(self, self.data_handler, category, definition, self.alert_system)

    def close_tabs(self, close_list: list = None, tab_id: int = None, log_out: bool = False,
                   clearing: bool = False) -> None:
        """Closes tabs via keyboard shortcut, exit button, renaming definitions, deleting definitions,
        deleting categories. Calls the save_text prior to logging out."""
        if log_out:
            close_list = self.get_tab_ids()
            self.save_text()
        if clearing:
            close_list = self.get_tab_ids()

        if tab_id is not None:
            definition = self.tab(tab_id, 'text')
            close_list = [tab_id]
            self.save_text(definition)
        elif close_list is not None:
            self.delete_frames(close_list)

        for i in sorted(close_list, reverse=True):
            self.forget(i)

        self.event_generate("<<NotebookTabClosed>>")
        if self.packed:
            self.focus_set()
        else:
            self.root.focus_set()

    def delete_frames(self, frames: list) -> None:
        """Deletes frames from the frame's dict."""
        for tab_id in frames:
            del self.frames[self.tab(tab_id, 'text')]

    def set_tab(self, definition: str, active_tabs: dict) -> None:
        """Sets the opened tab to the specified definition."""
        for text, i_d in active_tabs.items():
            if text == definition:
                self.select(i_d)

    def get_tab_ids(self, temp_list: list = None) -> list:
        """Returns the id's of the opened tabs in the notebook, or the id's of a given definition list."""
        active_tabs = self.get_active_tabs()

        if active_tabs == {}:
            return []

        close_list = []
        # If given a list of definitions, will return only the id's of those given
        if temp_list:
            for i in temp_list:
                for text, i_d in active_tabs.items():
                    if i == text:
                        close_list.append(i_d)
        else:
            # Returns all opened tabs
            for text, i_d in active_tabs.items():
                close_list.append(i_d)
        return close_list

    def pack_notebook(self) -> None:
        """Creates the CustomNotebook Class and packs to the screen."""
        self.pack(expand=True, fill="both", padx=8, pady=8)
        self.packed = True

    def save_text(self, definition: str = None) -> None:
        """Invokes the save text function for closing tabs."""
        # If definition is specified it's called from renaming the tab.
        if definition:
            delete_frame = None
            for text, frame in self.frames.items():
                if definition == text:
                    frame.save_btn.invoke()
                    delete_frame = text
            del self.frames[delete_frame]
        else:
            # Used for closing all the tabs to save all data
            for frame in self.frames.values():
                frame.save_btn.invoke()

    def check_for_unpack(self) -> None:
        """Checks if any tabs are opened and unpacks the notebook."""
        active_tabs = self.get_active_tabs()
        if len(active_tabs) == 0:
            self.pack_forget()
            self.packed = False
            self.frames = {}

    def get_active_tabs(self) -> dict:
        """Returns a dict of the opened tabs in the notebook with definition and i_d of tab."""
        if self.packed:
            temp_list = {}
            for i in range(len(self.tabs())):
                temp_list.update({self.tab(i)['text']: i})
            return temp_list
        else:
            return {}

    def on_close_press(self, event) -> str:
        """Called when the button is pressed over the close button"""
        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
            return "break"

    def on_close_release(self, event) -> None:
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            # need to change the state back of the button
            self.state(["!pressed"])
            return

        index = self.index("@%d,%d" % (event.x, event.y))

        if self._active == index:
            self.close_tabs(tab_id=index)

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self) -> None:
        """Initializes the style for the notebook along with creating elements."""
        self.images = (
            tk.PhotoImage("img_close", file=CLOSE_BTN),
            tk.PhotoImage("img_closeactive", file=CLOSE_BTN_ACTIVE),
            tk.PhotoImage("img_closepressed", file=CLOSE_BTN_PRESSED)
        )

        self.style.element_create("close", "image", "img_close",
                                  ("active", "pressed", "!disabled", "img_closepressed"),
                                  ("active", "!disabled", "img_closeactive"), border=10, sticky='e')
        self.style.layout("TNotebook", [("TNotebook.client", {"sticky": "nswe"})])
        self.style.layout("TNotebook.Tab", [
            ("TNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("TNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("TNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("TNotebook.label", {"side": "left", "sticky": 'w'}),
                                    ("TNotebook.close", {"side": "right", "sticky": 'e'}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
        self.style.theme_settings("azure-dark", {
            "TNotebook": {"configure": {"font": TAB_FONT, "padding": [0, 0], "focuscolor": "."}},
            "TNotebook.Tab": {
                "configure": {"padding": [2, 4], "font": TAB_FONT, "focuscolor": "."},
                "map": {"background": [("selected", BUTTON_BG)],
                        "expand": [("selected", [0, 0, 0, 0])]}}
        })
