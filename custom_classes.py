try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    import tkinter.font as tkfont
    from tkcalendar import Calendar

import utils
from settings import *
from PIL import ImageTk, Image
import random


class SettingSection:
    _title = "Settings"
    _entry_limit = [str(x) for x in range(1, 36)]
    _tab_limit = [str(x) for x in range(1, 5)]

    def __init__(self, root, data_handler):
        self.root = root
        self.data_handler = data_handler
        self.window = None
        self.limit_entry = None
        self.tab_entry = None

    def create_top_window_view(self):
        self.window = tk.Toplevel(self.root)
        utils.set_window(self.window, 300, 300, self._title)
        tk.Label(self.window, text="Settings Section", font=DEFAULT_FONT_UNDERLINE_BOLD).pack(side='top')

        tk.Label(self.window, text="Entry Limit:", font=DEFAULT_FONT).pack(side='left', anchor='nw', pady=4, padx=4)
        self.limit_entry = ttk.Combobox(self.window, values=self._entry_limit, width=3,
                                        font=DEFAULT_FONT, state="readonly")
        self.limit_entry.pack(side='left', anchor='nw', padx=4, pady=4)
        self.limit_entry.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())

        self.set_combobox(limit_entry=True)

        tk.Label(self.window, text="Tab Limit:", font=DEFAULT_FONT).pack(side='left', anchor='nw', pady=4, padx=4)
        self.tab_entry = ttk.Combobox(self.window, values=self._tab_limit, width=3,
                                      font=DEFAULT_FONT, state="readonly")
        self.tab_entry.pack(side='left', anchor='nw', padx=4, pady=4)
        self.tab_entry.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())

        self.set_combobox(tab_entry=True)

    def update_database(self):
        self.data_handler.entry_limit = int(self.limit_entry.get())
        self.limit_entry.selection_clear()
        self.data_handler.tab_limit = int(self.tab_entry.get())
        self.tab_entry.selection_clear()

    def set_combobox(self, limit_entry: bool = False, tab_entry: bool = False) -> None:
        if limit_entry:
            selection = str(self.data_handler.entry_limit)
            temp_list = self.limit_entry['values']
            for index, i_d in enumerate(temp_list):
                if i_d == selection:
                    self.limit_entry.current(index)
        if tab_entry:
            selection = str(self.data_handler.tab_limit)
            temp_list = self.tab_entry['values']
            for index, i_d in enumerate(temp_list):
                if i_d == selection:
                    self.tab_entry.current(index)


class HelpSection:
    _title = "Help Section"
    _options = ["Keyboard Shortcuts", "Functions"]
    _keyboard_shortcuts = "Control-F: Opens the search bar.\n" \
                          "\nKey-End: Closes the opened tab in the notebook.\n" \
                          "\nAlt-F4: Closes the program.\n" \
                          "\nCtrl-C: Copies the text in the text area.\n" \
                          "\nCtrl-V: Pastes the text in the text area.\n" \
                          "\nKey-Tab: Tabs through the widgets as well in the text.\n" \
                          "\nKey-Arrows: To go through the widgets, definitions and such.\n" \
                          "\nKey-Enter: Mimics the use of save buttons instead of clicking.\n" \
                          "\nCtrl-Tab: Will get the cursor to reset back to the main-window " \
                          "after closing a notebook tab.\n" \
                          "\nShift-ScrollWheel: Will move horizontally in the list of entries.\n"

    _functions = "Right-Click: Used for a variety of menus for copying, pasting, renaming, deleting, etc.\n" \
                 "\nBack-up/Auto Back-up: Feature that can be setup to automatically or manually back up your data," \
                 "so you will never lose any data.\n" \
                 "\nDragging and dropping definitions: So user can keep the order of things the way they" \
                 "want them to be.\n" \
                 "\nMultiple Categories: Users can create as many categories as they need in order " \
                 "to organize their data.\n" \
                 "\nSearch Feature: Can be used to search through the users definition list. At this time, it's only" \
                 "able to search through definitions and not the text entries in those definitions.\n" \
                 "\nEntry length: The character length of an entry is set to 20 for rendering purposes. " \
                 "Users may change it for longer definition entries but not recommended.\n" \
                 "\nCopy/Paste Definitions: Ability to copy a single definition from one category to another." \
                 "Used by the right-click function.\n"

    def __init__(self, root):
        self.root = root
        self.window = None
        self.text = None
        self.combo_box = None

    def create_top_window_view(self):
        self.window = tk.Toplevel(self.root)
        utils.set_window(self.window, 300, 300, self._title)
        tk.Label(self.window, text="Welcome to the Help Section", font=DEFAULT_FONT_UNDERLINE_BOLD).pack(side='top')
        self.combo_box = ttk.Combobox(self.window, values=self._options, state="readonly", font=DEFAULT_FONT)
        self.combo_box.pack(pady=4, padx=4)
        self.combo_box.current(0)
        self.combo_box.bind("<<ComboboxSelected>>", lambda event=None: self.update_text())

        text_frame = tk.Frame(self.window, borderwidth=1, relief="sunken")

        self.text = tk.Text(text_frame, font=DEFAULT_FONT, wrap=tk.WORD)

        # Create the scrollbar for the text
        scroll_bar = ttk.Scrollbar(text_frame, orient='vertical', command=self.text.yview)
        self.text.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(in_=text_frame, side='right', fill='y', expand=False)
        self.text.pack(in_=text_frame, side='left', fill='both', expand=True, padx=4)

        text_frame.pack()

        self.window.focus_set()
        self.update_text()

    def update_text(self) -> None:
        if self.combo_box.get() == "Keyboard Shortcuts":
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", "end-1c")
            self.text.insert(tk.END, self._keyboard_shortcuts)
            self.text.config(state=tk.DISABLED)
        elif self.combo_box.get() == "Functions":
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", "end-1c")
            self.text.insert(tk.END, self._functions)
            self.text.config(state=tk.DISABLED)
        self.combo_box.selection_clear()


class BackGround(tk.Canvas):

    _bg_image = None
    _filenames = ["Images/bg-0.jpeg",
                  "Images/bg-1.jpeg",
                  "Images/bg-2.jpeg",
                  "Images/bg-3.jpeg"]

    def __init__(self, root, *args, **kwargs):
        tk.Canvas.__init__(self, root, *args, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self._bg_image = random.choice(self._filenames)
        self.background_img = ImageTk.PhotoImage(file=self._bg_image)
        self.image = None
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.pack(expand=True, fill="both")
        self.drawn = self.create_image(0, 0, image=self.background_img, anchor='nw')

    def on_resize(self, event):
        new_size = Image.open(self._bg_image).resize((event.width, event.height), Image.ANTIALIAS)

        bg = ImageTk.PhotoImage(new_size)
        self.image = bg  # Need this so python doesn't get rid of it before it's drawn to the screen

        self.itemconfig(self.drawn, image=bg)


class TextArea(tk.Text):

    def __init__(self, text_frame, data_handler, category, definition, *args, **kwargs):
        tk.Text.__init__(self, text_frame, *args, **kwargs)
        self.data_handler = data_handler

        self.insert(tk.END, self.data_handler.get_text_by_definition(category, definition))

        # Create the scrollbar for the text
        scroll_bar = ttk.Scrollbar(text_frame, orient='vertical', command=self.yview)
        self.config(yscrollcommand=scroll_bar.set)

        scroll_bar.pack(in_=text_frame, side='right', fill='y', expand=False)
        self.pack(in_=text_frame, side='left', fill='both', expand=True, padx=4)


class TabArea(tk.Frame):
    _supported_fonts = []
    _font_sizes = [str(x) for x in range(10, 20, 2)]

    def __init__(self, notebook, data_handler, category, definition, alert_system, *args, **kwargs):
        tk.Frame.__init__(self, notebook, *args, **kwargs)
        self.data_handler = data_handler
        self.notebook = notebook
        self.alert_system = alert_system

        for i in tkfont.families():
            self._supported_fonts.append(i)

        top_frame = tk.Frame(self)
        text_frame = tk.Frame(self, borderwidth=1, relief="sunken")
        bottom_frame = tk.Frame(self)

        # Top frame widgets
        self.font_choices = ttk.Combobox(top_frame, values=self._supported_fonts,
                                         font=DEFAULT_FONT, state="readonly")
        self.font_choices.pack(side='left', padx=4, pady=4)
        self.font_choices.current(6)
        self.font_choices.bind("<<ComboboxSelected>>",
                               lambda event=None: self.change_font(self.font_choices.get(),
                                                                   self.font_size_choices.get(), category,
                                                                   definition))

        self.font_size_choices = ttk.Combobox(top_frame, values=self._font_sizes, width=3,
                                              font=DEFAULT_FONT, state="readonly")
        self.font_size_choices.pack(side='left', padx=4, pady=4)
        self.font_size_choices.current(0)
        self.font_size_choices.bind("<<ComboboxSelected>>",
                                    lambda event=None: self.change_font(self.font_choices.get(),
                                                                        self.font_size_choices.get(), category,
                                                                        definition))

        # Create the text area
        self.text_area = TextArea(text_frame, self.data_handler, category, definition,
                                  font=self.get_current_font(category, definition), padx=2, spacing3=2, wrap=tk.WORD,
                                  undo=True)

        # Bottom Frame layout
        time_stamp = ttk.Label(bottom_frame,
                               text=f"Created: {self.data_handler.get_timestamp_by_definition(category, definition)}")
        self.save_btn = ttk.Button(bottom_frame, text="Save", style="Accent.TButton",
                                   command=lambda: self.save_text(category, definition,
                                                                  self.text_area.get(1.0, "end-1c")))

        time_stamp.pack(side="left", pady=8, padx=8)
        self.save_btn.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        top_frame.pack(side='top', fill='x')
        bottom_frame.pack(side="bottom", fill='x')
        text_frame.pack(side='top', fill='both', expand=True)

        self.text_area.bind("<End>",
                            lambda event=None: self.notebook.close_tabs(self.notebook.get_tab_frames([definition]),
                                                                        save=True))

        self.set_combobox(category, definition)

    def save_text(self, category: str, definition: str, text: str) -> None:
        self.data_handler.add_text(category, definition, text)
        self.data_handler.update_json()
        self.alert_system.show_alert(("Entry has been saved.", "white"))

    def get_current_font(self, category, definition):
        return self.data_handler.get_tab_font(category, definition)

    def change_font(self, font: str, size: str, category, definition):
        new_font = font, int(size)
        self.text_area.config(font=new_font)
        self.font_size_choices.selection_clear()
        self.font_choices.selection_clear()
        self.data_handler.set_tab_font(category, definition, new_font)

    def set_combobox(self, category, definition):
        fonts = self.font_choices['values']
        sizes = self.font_size_choices['values']
        f, s = self.data_handler.get_tab_font(category, definition)
        for index, i_d in enumerate(fonts):
            if i_d == f:
                self.font_choices.current(index)
        for index, i_d in enumerate(sizes):
            if i_d == str(s):
                self.font_size_choices.current(index)


class CustomListBox(tk.Listbox):

    def __init__(self, root, data_handler=None, category=None, **kw):
        kw['selectmode'] = kw.pop('selectmode')
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
        self.index_lock = False
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

    def unlock_selection(self):
        self.index_lock = False

    def lock_selection(self):
        self.index_lock = True

    def shift_selection(self, event):
        if self.index_lock:
            return "break"
        else:
            if self.ctrl_clicked:
                return "break"
            selection = self.curselection()
            if not self.selection or len(selection) == 0:
                return "break"

            if self.shifting:
                return "break"

            selection_range = range(min(selection), max(selection))
            current_index = self.nearest(event.y)

            line_height = 5
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


class SearchEngine:

    def __init__(self, root, data_handler):
        self.root = root
        self.data_handler = data_handler
        self.packed = False
        self.search_frame = None
        self.search_entry = None

    def create_view(self):
        if not self.packed:
            self.search_frame = ttk.Frame(self.root.category_frame)
            self.search_frame.grid(row=0, column=2, columnspan=5)
            self.search_entry = tk.Entry(self.search_frame, width=21, font=DEFAULT_FONT, validate="key",
                                         background=ENTRY_COLOR, validatecommand=(self.root.register(lambda event:
                                                                                                     utils.validate_entry(
                                                                                                         event,
                                                                                                         self.data_handler.entry_limit)),
                                                                                  "%P"))
            self.search_entry.pack(side='left', padx=4)
            self.search_entry.bind("<Return>", lambda event=None: self.search_set_listbox(self.search_entry.get()))
            ttk.Button(self.search_frame, style="Accent.TButton", text="Search", width=6,
                       command=lambda: self.search_set_listbox(self.search_entry.get())).pack(side='left',
                                                                                              padx=4,
                                                                                              pady=4)
            ttk.Button(self.search_frame, style="Accent.TButton", text="Reset", width=6,
                       command=lambda: self.search_reset()).pack(side='left', padx=4, pady=4)
            ttk.Button(self.search_frame, style="Accent.TButton", text="X", width=1, command=self.unpack_search).pack(
                side='right', padx=4, pady=4)
            self.packed = True
        else:
            self.unpack_search()

    def unpack_search(self):
        if self.packed:
            self.search_frame.grid_forget()
            self.packed = False
            self.search_reset()

    @staticmethod
    def string_search(word: str, data: list) -> list:
        if word == '':
            return []

        word = word.lstrip()
        word = word.rstrip()

        word_case_fold = word.casefold()
        word_capital = word.capitalize()

        wo = filter(lambda a: word in a, data)
        w_case = filter(lambda a: word_case_fold in a, data)
        wc = filter(lambda a: word_capital in a, data)

        words = list(wo) + list(w_case) + list(wc)
        return list(set(words))

    def search_set_listbox(self, word: str) -> None:
        self.root.list_box.lock_selection()
        new_list = self.string_search(word, self.data_handler.get_definitions_by_list(self.root.category_box.get()))
        if len(new_list) > 0:
            self.root.update_list(new_list, search=True)

    def search_reset(self) -> None:
        word = self.search_entry.get()
        if len(word) > 0:
            self.search_entry.delete(0, len(word))
        self.root.update_list()
        self.root.list_box.unlock_selection()


class Layout(tk.Frame):

    def __init__(self, canvas, data_handler, alert_system, **kwargs):
        tk.Frame.__init__(self, canvas, **kwargs)
        self.root = canvas
        self.data_handler = data_handler
        self.alert_system = alert_system
        self.alert_system.main_layout = self
        self.copied_definition = None
        self.copied_text = None
        self.copied_font = None
        self.copied_time_stamp = None

        parent_frame = ttk.Frame(self.root, relief="ridge", borderwidth=2, width=25)
        parent_frame.pack(anchor='nw', fill='x', pady=8, padx=8)

        self.category_frame = ttk.Frame(parent_frame)
        self.category_frame.pack(side='left', anchor='w')

        tool_frame = ttk.Frame(parent_frame)
        tool_frame.pack(side='right', anchor='se')

        tk.Label(self.category_frame, text="Select Category:", font=DEFAULT_FONT).grid(row=0, column=0, pady=6)

        # Create the drop-down category
        self.category_box = ttk.Combobox(self.category_frame, values=self.data_handler.get_categories_by_list(),
                                         font=DEFAULT_FONT, state="readonly")
        self.category_box.grid(row=1, column=0, padx=4, pady=4)
        self.category_box.current(0)

        tk.Label(self.category_frame, text="Alerts:", font=DEFAULT_FONT).grid(row=1, column=1)

        tk.Label(tool_frame, text=f"User: {self.data_handler.current_user}", font=DEFAULT_FONT).pack(side='left',
                                                                                                     anchor='e',
                                                                                                     padx=4,
                                                                                                     pady=8)

        # listbox frame
        listbox_frame = ttk.Frame(self.root, width=50,
                                  height=SCREEN_HEIGHT, relief="ridge", borderwidth=2)
        listbox_frame.pack(fill='y', side='left', padx=8, pady=8)

        tk.Label(listbox_frame, text="Add Definitions:", font=DEFAULT_FONT).pack()

        # Create the entry and button to add definitions
        self.def_entry = tk.Entry(listbox_frame, validate="key",
                                  validatecommand=(self.root.register(
                                      lambda event: utils.validate_entry(event, self.data_handler.entry_limit)), "%P"),
                                  font=DEFAULT_FONT,
                                  width=21, background=ENTRY_COLOR)
        self.def_entry.pack(pady=4)

        self.add_definition_btn = ttk.Button(listbox_frame, style="Accent.TButton", text="Add Definition", width=24,
                                             command=lambda: self.add_definition(
                                                 self.def_entry.get(),
                                                 self.category_box.get()))
        self.add_definition_btn.pack(side='top', padx=4, pady=4)

        # Create the listbox to display all the definitions
        self.list_box = CustomListBox(listbox_frame, font=DEFAULT_FONT, selectmode=tk.EXTENDED,
                                      activestyle=tk.DOTBOX, data_handler=self.data_handler,
                                      category=self.category_box.current(0))
        self.list_box.pack(side='top', fill='both', expand=True, pady=4, padx=4)
        self.list_box.configure(highlightcolor=BLACK)

        # Create the definition scrollbar
        vert_scroll_bar = ttk.Scrollbar(self.list_box)
        vert_scroll_bar.pack(side='right', fill='y')
        vert_scroll_bar.config(command=self.list_box.yview)

        self.list_box.config(yscrollcommand=vert_scroll_bar.set)

        self.notebook_frame = ttk.Frame(self.root, relief="ridge")

        self.notebook = CustomNotebook(self.notebook_frame, data_handler=self.data_handler,
                                       alert_system=self.alert_system,
                                       width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

    # Class Functions
    def delete_category(self) -> None:
        """Deletion of categories."""
        if tk.messagebox.askyesno("Are you sure?", "Deleting is permanent!"):
            category = self.category_box.get()
            definitions = self.data_handler.get_definitions_by_list(category)

            check = self.data_handler.delete_category(category)
            if check:
                close_list = self.notebook.get_tab_frames(definitions)
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
        # Check if category is getting renamed to close all tabs
        if category is not None:
            close_list = self.notebook.get_tab_frames()
            self.notebook.close_tabs(close_list, save=True)

        check = self.data_handler.add_category(entry, category)
        if check:
            window.destroy()
            self.update_categories()
            self.set_category_list(entry)
        else:
            self.alert_system.show_alert(("Could not save category.", "red"))

    @staticmethod
    def stay_on_top(win):
        win.lift()
        win.focus_set()

    def add_definition(self, entry: str, category: str, definition=None, window=None) -> None:
        """Adds the definition entry to the database, calls the update list method,
           and closes the toplevel window if opened and checks if renaming a definition."""
        # Checks if definition is getting renamed
        if definition is not None:
            close_list = self.notebook.get_tab_frames([definition])
            self.notebook.close_tabs(close_list, save=True)

        check = self.data_handler.add_definition(entry, category, definition)
        if check:
            self.update_list()
            if window:
                window.destroy()
        else:
            self.alert_system.show_alert(("Could not save definition.", "red"))
            if window:
                window.after_idle(self.stay_on_top, window)

        self.def_entry.delete(0, len(entry))
        self.def_entry.focus_set()

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
                close_list = self.notebook.get_tab_frames(temp_list)
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
            top_window, entry = utils.create_pop_up("Rename Definition", self.root, self.data_handler.entry_limit)

            ttk.Button(top_window, text="Save Definition", width=21, style="Accent.TButton",
                       command=lambda e=None: self.add_definition(entry.get(), category, definition,
                                                                  window=top_window)).pack(side='top', padx=4, pady=4)

            entry.bind("<Return>",
                       lambda e=None: self.add_definition(entry.get(), category, definition, window=top_window))
            entry.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))

        elif state == "rcategory":
            top_window, entry = utils.create_pop_up("Rename Category", self.root, self.data_handler.entry_limit)

            ttk.Button(top_window, text="Save Category", width=21, style="Accent.TButton",
                       command=lambda: self.add_category(entry.get(), top_window,
                                                         category)).pack(side='top', padx=4, pady=4)

            entry.bind("<Return>", lambda e=None: self.add_category(entry.get(), top_window, category))

        elif state == "acategory":
            top_window, entry = utils.create_pop_up("Add Category", self.root, self.data_handler.entry_limit)

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

    def copy_definition(self, entry, index) -> None:
        """Copies the definition, text, font and timestamp from a given definition."""
        self.copied_definition = entry.get(index)
        self.copied_text = self.data_handler.get_text_by_definition(self.category_box.get(), self.copied_definition)
        self.copied_time_stamp = self.data_handler.get_timestamp_by_definition(self.category_box.get(),
                                                                               self.copied_definition)
        self.copied_font = self.data_handler.get_tab_font(self.category_box.get(), self.copied_definition)
        self.alert_system.show_alert(("Copied definition.", "white"))

    def paste_definition(self):
        """Pastes the saved definition."""
        check = self.data_handler.paste_definition(self.category_box.get(), self.copied_definition, self.copied_text,
                                                   self.copied_time_stamp, self.copied_font)
        if check:
            self.update_list()
        else:
            self.alert_system.show_alert(("Could not paste definition.", "red"))

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
                    menu.add_command(label="Copy",
                                     command=lambda: self.copy_definition(instance, index))
                    menu.add_command(label="Paste",
                                     command=lambda: self.paste_definition())
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
            menu.add_command(label="Add Date", command=lambda: self.create_calender(instance))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def create_calender(self, instance: tk.Entry) -> None:
        """Creates the calendar in a top window."""
        top_window = tk.Toplevel(self.root)
        utils.set_window(top_window, 250, 215, "Calender")

        month, day, year = utils.get_current_date()

        cal = Calendar(top_window, showweeknumbers=False, firstweekday='sunday', selectmode='day', year=year,
                       month=month, day=day)
        cal.pack(padx=4, pady=4)
        ttk.Button(top_window, text="Add Date", width=21, style="Accent.TButton",
                   command=lambda: self.add_date(instance, cal.selection_get(), top_window)).pack(pady=4, padx=4)

    @staticmethod
    def add_date(instance: tk.Entry, date: str, top_window: tk.Toplevel) -> None:
        """Sets the selected date from the calendar into the entry widget."""
        formatted_date = utils.format_date(date)
        instance.delete(0, len(instance.get()))
        instance.insert(0, formatted_date)
        top_window.destroy()

    def get_list_box_item(self) -> str:
        """Returns the selected list-box item if multiple are selected, will return the first one in the index."""
        index = self.list_box.curselection()
        if len(index) > 1:
            for i in index:
                return self.list_box.get(i)
        else:
            definition = self.list_box.get(index)
            return definition

    def update_list(self, word_list: list = None, search: bool = False) -> None:
        """Updates the definition list from selected category or from the searched item."""
        if search:
            self.list_box.delete(0, self.list_box.size())
            for definition in word_list:
                self.list_box.insert(0, definition)
        else:
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

    def validate_tab_length(self, frame):
        """Checks the length of characters in a tab and shortens it if need be."""
        length = len(self.tab(frame)['text'])
        if 14 <= length <= 18:
            original = self.tab(frame)['text']
            sliced = original[:-8]
            self.tab(frame, text=[sliced + ".."])
        elif 19 <= length <= 23:
            original = self.tab(frame)['text']
            sliced = original[:-14]
            self.tab(frame, text=[sliced + ".."])
        elif 24 <= length <= 28:
            original = self.tab(frame)['text']
            sliced = original[:-18]
            self.tab(frame, text=[sliced + ".."])
        elif 29 <= length <= 33:
            original = self.tab(frame)['text']
            sliced = original[:-22]
            self.tab(frame, text=[sliced + ".."])
        elif 34 <= length <= 35:
            original = self.tab(frame)['text']
            sliced = original[:-23]
            self.tab(frame, text=[sliced + ".."])

    def add_tab(self, category: str, definition: str) -> None:
        """Calls the create_tab method to create elements and adds them to the notebook."""
        if not self.packed:
            self.pack_notebook()

        if len(self.frames) < self.data_handler.tab_limit:
            # Creates a tab if the tab is not opened on the notebook
            if definition not in self.frames:
                frame = self.create_tab(category, definition)
                self.frames.update({definition: frame})
                self.add(frame, text=definition)
                self.select(frame)
                self.validate_tab_length(frame)
            # Other-wise sets the focused on the specified definition user is trying to open again
            else:
                self.set_tab(definition)
                self.alert_system.show_alert(("Can't open multiple tabs with the same name.", "red"))
        else:
            # If tab limit is executed, focus will be set to specified tab.
            if definition in self.frames:
                self.set_tab(definition)
            else:
                self.alert_system.show_alert(("Tab limit has been met.", "red"))

    def create_tab(self, category: str, definition: str) -> tk.Frame:
        """Creates the elements for the tab from the add tab method."""
        return TabArea(self, self.data_handler, category, definition, self.alert_system)

    def close_tabs(self, close_list: list = None, save: bool = False, log_out: bool = False,
                   clearing: bool = False) -> None:
        """Closes tabs via keyboard shortcut, exit button, renaming definitions, deleting definitions,
        deleting categories. Calls the save_text prior to logging out or if manually called, generates a
        NotebookTabClosed event."""
        if log_out:
            close_list = self.get_tab_frames()
            self.save_text()
        if clearing:
            close_list = self.get_tab_frames()
        if save:
            self.save_text(close_list)

        if close_list is not None:
            self.delete_frames(close_list)

        for i in close_list:
            self.forget(i)

        self.event_generate("<<NotebookTabClosed>>")
        if self.packed:
            self.focus_set()
        else:
            self.root.focus_set()

    def delete_frames(self, frames: list) -> None:
        """Deletes frames from the self-frames dict."""
        hit_list = []
        for frame in frames:
            for definition, f in self.frames.items():
                if frame == f:
                    hit_list.append(definition)
        for i in hit_list:
            del self.frames[i]

    def set_tab(self, definition: str) -> None:
        """Brings a currently opened tab into focus."""
        for text, frame in self.frames.items():
            if text == definition:
                self.select(frame)

    def get_tab_frames(self, temp_list: list = None) -> list:
        """Returns the frames of the opened tabs in the notebook."""
        if self.frames == {}:
            return []

        close_list = []
        # If given a list of definitions, will return only the frames of those given
        if temp_list:
            for i in temp_list:
                for text, frame in self.frames.items():
                    if i == text:
                        close_list.append(frame)
        else:
            # Returns all opened tabs
            for text, frame in self.frames.items():
                close_list.append(frame)
        return close_list

    def pack_notebook(self) -> None:
        """Packs the frame the notebook is on and the notebook itself."""
        self.root.pack(expand=True, fill='both', pady=8, padx=8)
        self.pack(pady=2, padx=2, expand=True, fill='both')
        self.packed = True

    def save_text(self, save_list: list = None) -> None:
        """Invokes the save text function for closing tabs."""
        if save_list:
            for frame in save_list:
                frame.save_btn.invoke()
        else:
            for frame in self.frames.values():
                frame.save_btn.invoke()

    def check_for_unpack(self) -> None:
        """Checks if any tabs are opened and unpacks the notebook."""
        if len(self.frames) == 0:
            self.root.pack_forget()
            self.pack_forget()
            self.packed = False
            self.frames = {}

    def on_close_press(self, event) -> None:
        """Called when the button is pressed over the close button"""
        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
            return

    def on_close_release(self, event) -> None:
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        if "close" not in element:
            # User moved the mouse off of the close button
            # Need to change the state back of the button
            self.state(["!pressed"])
            return

        index = self.index("@%d,%d" % (event.x, event.y))
        current_frame = self.select()  # Returns a string of the frame
        for text, frame in self.frames.items():
            if current_frame == str(frame):
                current_frame = frame

        if self._active == index:
            self.close_tabs([current_frame], save=True)

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
