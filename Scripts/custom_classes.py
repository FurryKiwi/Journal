# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog
    import tkinter.font as tkfont

import json
import threading
from PIL import ImageTk, Image
import random
from enchant import Dict, tokenize
from enchant.tokenize import en  # Need this for building with pyinstaller, otherwise it doesn't import the en.tokenizer
import os

from CustomTkWidgets.custom_calendar import Calendar
from CustomTkWidgets.custom_combobox import AutocompleteCombobox
from CustomTkWidgets.custom_listbox import DefaultListbox
from CustomTkWidgets.custom_treeview import TreeView
from CustomTkWidgets.custom_notebook import DefaultNotebook
from Scripts.settings import *
import Scripts.utils as utils


class BackGround(tk.Canvas):
    _bg_image = None
    _image_locations_path = os.path.join(os.getcwd(), "Core", "Docs", "image_paths.json")
    __slots__ = "root", "image_loc", "images_paths", "_image_path", "image_name", "background_img", "image", "drawn"

    def __init__(self, root, *args, **kwargs):
        tk.Canvas.__init__(self, root, *args, **kwargs)
        self.root = root
        self.bind("<Configure>", self.on_resize)
        self.image_loc = None
        self.images_paths = None
        self._image_path = None
        self.image_name = None
        self.background_img = None
        self.image = None
        self.drawn = None

        self.reload_image()

    def on_resize(self, event):
        resize_image = self.resize_image(self._image_path)
        self.image = ImageTk.PhotoImage(resize_image)

        self.itemconfig(self.drawn, image=self.image)

    def reload_image(self):
        self.image_loc = utils.read_json(self._image_locations_path, BACKGROUND_IMAGES)
        if self.image_loc is None:
            utils.dump_json(self._image_locations_path, BACKGROUND_IMAGES)
            self.image_loc = utils.read_json(self._image_locations_path, BACKGROUND_IMAGES)
        self.images_paths = [v for v in self.image_loc.values()]
        self._image_path = random.choice(self.images_paths)
        self.image_name = [k for k, v in self.image_loc.items() if self._image_path == v][0]
        resize_image = self.resize_image(self._image_path)
        self.image = ImageTk.PhotoImage(resize_image)
        self.pack(expand=True, fill="both")
        self.drawn = self.create_image(0, 0, image=self.image, anchor='nw')

    def change_background(self, image_path: str) -> None:
        # Reset the image path
        self._image_path = image_path
        # Reset the image name
        self.image_name = [k for k, v in self.image_loc.items() if self._image_path == v][0]
        # Resize to the screen
        resize_image = self.resize_image(image_path)
        # Convert to photo image
        self.image = ImageTk.PhotoImage(resize_image)
        # Set the canvas to the new image
        self.itemconfig(self.drawn, image=self.image)

    def resize_image(self, image_path: str) -> Image.Image:
        image = Image.open(image_path)
        return image.resize((self.winfo_width(), self.winfo_height()), Image.LANCZOS)

    def save_image_paths(self):
        """Used to dump any added images into the database to the json file before closing the program,
        or logging out."""
        utils.dump_json(self._image_locations_path, self.image_loc)


class TextArea(tk.Text):
    locale = 'en'
    __slots__ = "data_handler", "alert_system", "corpus", "tokenize", "_proxy", "selected_word", "suggested_words", \
                "after_id", "new_thread", "flag"

    def __init__(self, text_frame, data_handler, category, definition, alert_system, *args, **kwargs):
        tk.Text.__init__(self, text_frame, *args, **kwargs)
        self.data_handler = data_handler
        self.alert_system = alert_system
        self.corpus = Dict(self.locale)
        self.tokenize = tokenize.get_tokenizer(self.locale)
        self._proxy = self._w + "_proxy"
        self.tk.call("rename", self._w, self._proxy)
        self.tk.createcommand(self._w, self._proxy_cmd)
        self.tag_configure('hl', foreground='red')

        self.selected_word = ""
        self.suggested_words = {}
        self.after_id = None
        self.new_thread = None
        self.flag = False

        self.insert(tk.END, self.data_handler.get_text_by_definition(category, definition))

        # Create the scrollbar for the text
        scroll_bar = ttk.Scrollbar(text_frame, orient='vertical', command=self.yview)
        self.config(yscrollcommand=scroll_bar.set)

        scroll_bar.pack(in_=text_frame, side='right', fill='y', expand=False)

        self.bind('<<TextModified>>', self.on_modify)
        self.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))

    def pop_up_menu(self, event):
        try:
            self.selected_word = self.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return
        # Check if multiple words are selected via having a space in them.
        if " " in self.selected_word:
            return
        # Check if a period is selected with it and take it off for correction
        if "." in self.selected_word:
            self.flag = True
            self.selected_word = self.selected_word[:-1]
        # Check if the selected is None
        if self.selected_word != "None":
            menu = tk.Menu(self, tearoff=0)
            view = tk.Menu(self, tearoff=0)
            menu.add_cascade(label="Add-Dict", menu=view)

            def suggest_command(word):
                def new_command():
                    self.replace_word(word)

                return new_command

            def add_to_dict_command(word):
                def new_command():
                    self.add_to_dict(word)

                return new_command

            for key, value in self.suggested_words.items():
                for item in value:
                    if key == self.selected_word:
                        menu.add_command(label=item, command=suggest_command(item))

            view.add_command(label=self.selected_word, command=add_to_dict_command(self.selected_word))

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.selected_word = None
                menu.grab_release()

    def replace_word(self, word: str):
        try:
            if self.flag:
                self.replace(tk.SEL_FIRST, f"{tk.SEL_LAST}-1c", word)
            else:
                self.replace(tk.SEL_FIRST, tk.SEL_LAST, word)
            self.flag = False
        except tk.TclError:
            pass

    def add_to_dict(self, word: str):
        self.replace(tk.SEL_FIRST, tk.SEL_LAST, word)
        check = self.corpus.is_added(word)
        if not check:
            self.corpus.add(word)

    def _proxy_cmd(self, command, *args):
        """Intercept the Tk commands to the text widget and if any of the content
        modifying commands are called, post a TextModified event."""
        cmd = (self._proxy, command)
        if args:
            cmd = cmd + args
        try:
            result = self.tk.call(cmd)
            if command in ('insert', 'delete'):
                self.event_generate('<<TextModified>>')
            return result
        except tk.TclError as e:
            return

    def on_modify(self, event):
        """Rate limit the spell-checking with a 100ms delay. If another modification
        event comes in within this time, cancel the after call and re-schedule."""
        try:
            if self.after_id:
                self.after_cancel(self.after_id)
            self.after_id = self.after(700, lambda: self.make_thread(self.on_modified))
        except IndexError:
            pass

    def is_double_space(self, input_string):
        new_string = input_string.replace("  ", " ")
        self.replace("1.0 linestart", "1.0 lineend", new_string)

    def spell_check(self):
        data = self.get(f"1.0 linestart", "1.0 lineend")
        self.is_double_space(data)
        for word, pos in self.tokenize(data):
            check = self.corpus.check(word)
            if not check:
                start = f"1.{pos}"
                end = f"1.{pos + len(word)}"
                self.tag_add("hl", start, end)
                self.suggested_words.update({word: self.corpus.suggest(word)})

    def make_thread(self, func):
        self.new_thread = threading.Thread(target=func, daemon=True)
        self.new_thread.start()

    def on_modified(self):
        self.after_id = None

        data = self.get(f"1.0 linestart", "1.0 lineend")
        for word, pos in self.tokenize(data):
            check = self.corpus.check(word)
            if not check:
                start = f"1.{pos}"
                end = f"1.{pos + len(word)}"
                self.tag_add("hl", start, end)

                self.suggested_words.update({word: self.corpus.suggest(word)})


class TabArea(tk.Frame):
    _font_sizes = [str(x) for x in range(10, 20, 2)]
    _default_font_tab = "Arial"
    _default_size_tab = "12"
    __slots__ = "notebook", "data_handler", "alert_system", "checklist", "_supported_fonts", "text_frame", \
                "font_choices", "font_size_choices", "spell_check_btn", "text_area", "save_btn"

    def __init__(self, notebook, data_handler, category, definition, alert_system, **kwargs):
        tk.Frame.__init__(self, notebook, **kwargs)
        self.data_handler = data_handler
        self.notebook = notebook
        self.alert_system = alert_system
        self.checklist = None
        self._supported_fonts = [i for i in tkfont.families()]

        top_frame = tk.Frame(self)
        self.text_frame = tk.Frame(self, borderwidth=4)
        bottom_frame = tk.Frame(self)

        # Top frame widgets
        self.font_choices = AutocompleteCombobox(top_frame, self._supported_fonts,
                                                 font=DEFAULT_FONT, style="R.TCombobox")
        self.font_choices.pack(side='left', padx=4, pady=4)
        self.font_choices.bind("<<ComboboxSelected>>",
                               lambda event=None: self.change_font(self.font_choices.get(),
                                                                   self.font_size_choices.get(), category,
                                                                   definition))

        self.font_size_choices = ttk.Combobox(top_frame, values=self._font_sizes, width=4,
                                              font=DEFAULT_FONT, state="readonly", style="R.TCombobox")
        self.font_size_choices.pack(side='left', padx=4, pady=4)
        self.font_size_choices.bind("<<ComboboxSelected>>",
                                    lambda event=None: self.change_font(self.font_choices.get(),
                                                                        self.font_size_choices.get(), category,
                                                                        definition))

        self.spell_check_btn = ttk.Button(top_frame, text="Spell Check", style="Accent.TButton",
                                          command=self.spell_check)
        self.spell_check_btn.pack(side='left', pady=4, padx=4)

        # Create the text area
        self.text_area = TextArea(self.text_frame, self.data_handler, category, definition, self.alert_system,
                                  font=self.get_current_font(category, definition), padx=2, spacing3=2, wrap=tk.WORD,
                                  undo=True)
        self.text_area.pack(side='top', fill='both', expand=True)

        # Bottom Frame layout
        time_stamp = ttk.Label(bottom_frame, font=DEFAULT_FONT, style="R.TLabel",
                               text=f"Created: {self.data_handler.get_timestamp_by_definition(category, definition)}")
        self.save_btn = ttk.Button(bottom_frame, text="Save", style="Accent.TButton",
                                   command=lambda: self.save_text(category, definition,
                                                                  self.text_area.get(1.0, "end-1c")))

        time_stamp.pack(side="left", pady=8, padx=8)
        self.save_btn.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        top_frame.pack(side='top', fill='x')
        bottom_frame.pack(side="bottom", fill='x')
        self.text_frame.pack(side='top', fill='both', expand=True)

        self.text_area.bind("<End>", lambda event=None: self.notebook.close_tabs(
            self.notebook.get_tab_frames([definition]), save=True))

        self.set_combobox(category, definition)

    def spell_check(self):
        self.text_area.make_thread(self.text_area.spell_check)

    def save_text(self, category: str, definition: str, text: str) -> None:
        self.data_handler.add_text(category, definition, text)
        self.data_handler.update_json()
        self.alert_system.show_alert(("Entry has been saved.", "white"))

    def get_current_font(self, category, definition):
        return self.data_handler.get_tab_font(category, definition)

    def change_font(self, font: str, size: str, category: str, definition: str) -> None:
        """Changes font in the text area, and saves the font to the database."""
        new_font = font, int(size)
        self.text_area.config(font=new_font)
        self.font_size_choices.selection_clear()
        self.font_choices.selection_clear()
        self.data_handler.set_tab_font(category, definition, new_font)

    def set_combobox(self, category: str, definition: str) -> None:
        """Sets the font and size that was last used by that tab."""
        fonts = self.font_choices['values']
        sizes = self.font_size_choices['values']
        f, s = self.data_handler.get_tab_font(category, definition)
        _use_default_font = False
        _use_default_size = False
        if f not in fonts:
            _use_default_font = True
        if str(s) not in sizes:
            _use_default_size = True

        if _use_default_font:
            index = [index for index, i_d in enumerate(fonts) if i_d == self._default_font_tab]
            self.font_choices.current(index[0])
        else:
            index = [index for index, i_d in enumerate(fonts) if i_d == f]
            self.font_choices.current(index[0])

        if _use_default_size:
            index = [index for index, i_d in enumerate(sizes) if i_d == self._default_size_tab]
            self.font_size_choices.current(index[0])
        else:
            index = [index for index, i_d in enumerate(sizes) if i_d == str(s)]
            self.font_size_choices.current(index[0])


class SearchEngine:
    __slots__ = "main_layout", "data_handler", "packed", "search_frame", "search_entry"

    def __init__(self, main_layout, data_handler):
        self.main_layout = main_layout
        self.data_handler = data_handler
        self.packed = False
        self.search_frame = None
        self.search_entry = None

    def create_view(self):
        if not self.packed:
            self.search_frame = ttk.Frame(self.main_layout.category_frame)
            self.search_frame.place(relx=0.45)
            self.search_entry = ttk.Entry(self.search_frame, width=21, font=DEFAULT_FONT, validate="key",
                                          style="R.TEntry",
                                          validatecommand=(self.main_layout.register(
                                              lambda event: utils.validate_entry(
                                                  event, self.data_handler.entry_limit)), "%P"))

            self.search_entry.pack(side='left', padx=4)
            self.search_entry.bind("<Return>", lambda event=None: self.search_set_listbox(self.search_entry.get()))
            ttk.Button(self.search_frame, style="Accent.TButton", text="Search", width=8,
                       command=lambda: self.search_set_listbox(self.search_entry.get())).pack(side='left',
                                                                                              padx=2,
                                                                                              pady=4)
            ttk.Button(self.search_frame, style="Accent.TButton", text="Reset", width=6,
                       command=lambda: self.search_reset()).pack(side='left', padx=2, pady=4)
            ttk.Button(self.search_frame, style="Accent.TButton", text="X", width=2, command=self.unpack_search).pack(
                side='right', padx=2, pady=4)
            self.packed = True
        else:
            self.unpack_search()

    def unpack_search(self):
        if self.packed:
            self.search_frame.place_forget()
            self.packed = False
            self.search_reset()

    @staticmethod
    def string_search(word: str, data: list) -> list:
        """Searches a list of strings for the given word. Will search for all cases of the word in the given list.
        IE: Capitalize, lowercase, and original."""
        if word == '':
            return []

        word = word.strip()

        word_case_fold = word.casefold()
        word_capital = word.capitalize()

        wo = filter(lambda a: word in a, data)
        w_case = filter(lambda a: word_case_fold in a, data)
        wc = filter(lambda a: word_capital in a, data)

        words = list(wo) + list(w_case) + list(wc)
        return list(set(words))

    def search_set_listbox(self, word: str) -> None:
        self.main_layout.list_box.lock_selection()
        new_list = self.string_search(word,
                                      self.data_handler.get_definitions_by_list(self.main_layout.category_box.get()))
        if len(new_list) > 0:
            self.main_layout.update_list(new_list, search=True)

    def search_reset(self) -> None:
        word = self.search_entry.get()
        if len(word) > 0:
            self.search_entry.delete(0, len(word))
        self.main_layout.update_list()
        self.main_layout.list_box.unlock_selection()


class ImportView(tk.Toplevel):
    __slots__ = "root", "data_handler", "filepath", "main_layout", "formatted_data", "category_box", "list_box", \
                "tree_view"

    def __init__(self, root, data_handler, filepath, main_layout, **kwargs):

        try:
            self.data = utils.read_config(filepath)
            if isinstance(self.data, str):
                tk.messagebox.showinfo("Error Occurred", "There seems to be an issue reading in the json file.",
                                       parent=self)
                return
        except json.JSONDecodeError:
            tk.messagebox.showinfo("Error Occurred", "There seems to be an issue reading in the json file.",
                                   parent=self)
            return

        tk.Toplevel.__init__(self, root, **kwargs)

        self.root = root
        self.data_handler = data_handler
        self.main_layout = main_layout

        self.formatted_data = {}
        for c in self.data.keys():
            self.formatted_data.update({c: list(self.data[c].keys())})

        self.category_box = None
        self.list_box = None
        self.tree_view = None

        self.create_ui()
        self._setup_tree_view()
        self.update_list()
        self.root.event_generate("<<ImportExportCreated>>")
        utils.set_window(self, 700, 500, "Import", offset=(0, 100))

    def create_ui(self):
        # Left Frame
        left_main_frame = tk.Frame(self)
        left_main_frame.pack(side='left', anchor='w', expand=True, fill='both', pady=4, padx=4)
        # Right Frame
        right_main_frame = tk.Frame(self)
        right_main_frame.pack(side='right', anchor='e', expand=True, fill='both', padx=4, pady=4)

        # Top Left frame combobox and listbox
        top_left_frame = ttk.Frame(left_main_frame, relief="ridge", borderwidth=2)
        top_left_frame.pack(side='top', anchor='nw', expand=True, fill='both', padx=4, pady=4)

        # Top Right frame tree view
        top_right_frame = ttk.Frame(right_main_frame, relief="ridge", borderwidth=2)
        top_right_frame.pack(side='top', anchor='nw', expand=True, fill='both', padx=4, pady=4)

        # Left Frame Elements
        # Create the drop-down category
        ttk.Label(top_left_frame, text="Opened File:", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(side='top',
                                                                                                      padx=4,
                                                                                                      pady=4)
        self.category_box = ttk.Combobox(top_left_frame, values=[item for item in self.data.keys()],
                                         font=DEFAULT_FONT, state="readonly", style="R.TCombobox")
        self.category_box.pack(side='top', padx=4, pady=4)
        self.category_box.bind("<<ComboboxSelected>>", lambda event=None: self.update_list())

        # Create the listbox to display all the definitions
        self.list_box = CustomListBox(top_left_frame, height=SCREEN_HEIGHT, font=DEFAULT_FONT, selectmode=tk.EXTENDED,
                                      activestyle='none', data_handler=self.data_handler,
                                      category=self.category_box.current(0), borderwidth=0, highlightthickness=0)
        self.list_box.pack(side='top', expand=True, fill='both', pady=4, padx=4)
        self.list_box.lock_selection()

        # Create the definition scrollbar
        vert_scroll_bar = ttk.Scrollbar(self.list_box)
        vert_scroll_bar.pack(side='right', fill='y')
        vert_scroll_bar.config(command=self.list_box.yview)

        self.list_box.config(yscrollcommand=vert_scroll_bar.set)

        # Tree View Frame Elements
        right = tk.Frame(top_right_frame)
        right.pack(side='right', expand=True, fill='both')
        left = tk.Frame(top_right_frame)
        left.pack(side='left', expand=True, fill='both')

        ttk.Label(right, text="Functions:", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(side='top', pady=4,
                                                                                           padx=4)
        ttk.Button(right, style="Accent.TButton", text="Remove All", width=18,
                   command=lambda: self.tree_view.remove_all_elements()).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Remove Selected", width=18,
                   command=lambda: self.tree_view.remove_elements()).pack(side='top', pady=4, padx=4)

        ttk.Button(right, style="Accent.TButton", text="Import All", width=18,
                   command=lambda: self.tree_view.add_all_elements(self.formatted_data, importing=True)).pack(
            side='top', pady=4, padx=4)

        ttk.Button(right, style="Accent.TButton", text="Import Selected", width=18,
                   command=lambda: self.add_selected()).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Finish", width=18,
                   command=lambda: self.finalize()).pack(side='top', pady=4, padx=4)

        ttk.Label(left, text="Existing Data:", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(side='top', pady=4,
                                                                                              padx=4)
        self.tree_view = TreeView(left, style="R.Treeview")
        self.tree_view.pack(side='top', fill='both', expand=True, padx=4, pady=4)

    def _setup_tree_view(self):
        self.tree_view.add_default_items(self.data_handler.get_categories_definitions_formatted(), importing=True,
                                         exception=True)

    def set_category_list(self, category: str = None) -> None:
        """Set the category list to specified category or to the first one in the list."""
        if category is not None:
            temp_list = self.category_box['values']
            index = [index for index, i_d in enumerate(temp_list) if i_d == category]
            self.category_box.current(index[0])
        else:
            self.category_box.current(0)
        self.update_list()

    def update_list(self) -> None:
        """Updates the definition list from selected category or from the searched item."""
        category = self.category_box.get()
        if self.list_box.size() != 0:
            self.list_box.delete(0, self.list_box.size())
        temp_list = self.data[category]
        self.list_box.category = category
        if temp_list is not None:
            for definition in temp_list:
                self.list_box.insert(tk.END, definition)
        self.category_box.selection_clear()

    def update_categories(self) -> None:
        """Updates the category selection box with given values from the database."""
        self.category_box.config(values=[item for item in self.data.keys()])

    def add_selected(self):
        category = self.tree_view.item_selected
        if category is None:
            category = self.category_box.get()
        indexes = self.list_box.curselection()
        elements = [self.list_box.get(i) for i in indexes]

        self.tree_view.add_elements(category, elements)

    def finalize(self):
        """Passes data off to data_handler to import in into the current user's data."""
        data = self.tree_view.get_all_elements()

        if data == self.data_handler.get_categories_definitions_formatted():
            tk.messagebox.showinfo("Nothing to Add", "No Data to be imported.", parent=self)
            self.focus_set()
            return

        if data is None or data == {}:
            tk.messagebox.showinfo("No Data", "No Data to be imported.", parent=self)
            self.focus_set()
            return

        if tk.messagebox.askyesno("Importing Data", "Are you sure you want to import this data?", parent=self):
            backup = False
            if tk.messagebox.askyesno("Back Up Data", "Do you want to create a new backup of your existing data? "
                                                      "Any old backups will be overwritten!", parent=self):
                backup = True
            check = self.data_handler.import_data(data, self.data, backup)
            if check:
                self.main_layout.update_categories()
                self.main_layout.category_box.current(0)
                self.main_layout.update_list()
                tk.messagebox.showinfo("Import Success", "Data has been imported.", parent=self)
                self.destroy()


class ExportView(tk.Toplevel):
    __slots__ = "root", "data_handler", "category_box", "list_box", "tree_view"

    def __init__(self, root, data_handler, **kwargs):
        tk.Toplevel.__init__(self, root, **kwargs)

        self.root = root
        self.data_handler = data_handler

        self.category_box = None
        self.list_box = None
        self.tree_view = None

        self.create_ui()
        self.update_list()
        self.root.event_generate("<<ImportExportCreated>>")
        utils.set_window(self, 700, 500, "Export", offset=(0, 100))

    def create_ui(self):
        # Left Frame
        left_main_frame = tk.Frame(self)
        left_main_frame.pack(side='left', anchor='w', expand=True, fill='both', pady=4, padx=4)
        # Right Frame
        right_main_frame = tk.Frame(self)
        right_main_frame.pack(side='right', anchor='e', expand=True, fill='both', padx=4, pady=4)

        # Top Left frame combobox and listbox
        top_left_frame = ttk.Frame(left_main_frame, relief="ridge", borderwidth=2)
        top_left_frame.pack(side='top', anchor='nw', expand=True, fill='both', padx=4, pady=4)

        # Top Right frame tree view
        top_right_frame = ttk.Frame(right_main_frame, relief="ridge", borderwidth=2)
        top_right_frame.pack(side='top', anchor='nw', expand=True, fill='both', padx=4, pady=4)

        # Left Frame Elements
        # Create the drop-down category
        ttk.Label(top_left_frame, text="Categories", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(side='top',
                                                                                                    padx=4, pady=4)
        self.category_box = ttk.Combobox(top_left_frame, values=self.data_handler.get_categories_by_list(),
                                         font=DEFAULT_FONT, state="readonly", style="R.TCombobox")
        self.category_box.pack(side='top', padx=4, pady=4)
        self.category_box.bind("<<ComboboxSelected>>", lambda event=None: self.update_list())

        # Create the listbox to display all the definitions
        self.list_box = CustomListBox(top_left_frame, height=SCREEN_HEIGHT, font=DEFAULT_FONT,
                                      selectmode=tk.EXTENDED,
                                      activestyle='none', data_handler=self.data_handler,
                                      category=self.category_box.current(0), borderwidth=0, highlightthickness=0)
        self.list_box.pack(side='top', expand=True, fill='both', pady=4, padx=4)
        self.list_box.lock_selection()

        # Create the definition scrollbar
        vert_scroll_bar = ttk.Scrollbar(self.list_box)
        vert_scroll_bar.pack(side='right', fill='y')
        vert_scroll_bar.config(command=self.list_box.yview)

        self.list_box.config(yscrollcommand=vert_scroll_bar.set)

        # Tree View Frame Elements
        right = tk.Frame(top_right_frame)
        right.pack(side='right', expand=True, fill='both')
        left = tk.Frame(top_right_frame)
        left.pack(side='left', expand=True, fill='both')

        ttk.Label(right, text="Functions:", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(side='top', pady=4,
                                                                                           padx=4)
        ttk.Button(right, style="Accent.TButton", text="Remove All", width=18,
                   command=lambda: self.tree_view.remove_all_elements()).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Remove Selected", width=18,
                   command=lambda: self.tree_view.remove_elements()).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Export All", width=18,
                   command=lambda: self.tree_view.add_all_elements(
                       self.data_handler.get_categories_definitions_formatted())).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Export Selected", width=18,
                   command=lambda: self.add_selected()).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Finish", width=18,
                   command=lambda: self.finalize()).pack(side='top', pady=4, padx=4)

        ttk.Label(left, text="Preview:", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(side='top', pady=4, padx=4)
        self.tree_view = TreeView(left, style="R.Treeview")
        self.tree_view.pack(side='top', fill='both', expand=True, padx=4, pady=4)

    def set_category_list(self, category: str = None) -> None:
        """Set the category list to specified category or to the first one in the list."""
        if category is not None:
            temp_list = self.category_box['values']
            index = [index for index, i_d in enumerate(temp_list) if i_d == category]
            self.category_box.current(index[0])
        else:
            self.category_box.current(0)
        self.update_list()

    def update_list(self) -> None:
        """Updates the definition list from selected category or from the searched item."""
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

    def add_selected(self):
        category = self.category_box.get()
        if category == "Create a Category":
            return
        indexes = self.list_box.curselection()
        elements = [self.list_box.get(i) for i in indexes]

        self.tree_view.add_elements(category, elements)

    def finalize(self):
        """This will send all data to data_handler to export the proper data to a json file."""
        data = self.tree_view.get_all_elements()
        if data is None or data == {}:
            tk.messagebox.showinfo("No Data", "No Data to be exported.", parent=self)
            self.focus_set()
            return

        if tk.messagebox.askyesno("Exporting Data", "Are you sure you want to export this data?", parent=self):
            check = self.data_handler.export_data(data)
            if check:
                tk.messagebox.showinfo("Export Success", "Data has been exported.", parent=self)
                self.destroy()


class Layout(tk.Frame):
    __slots__ = "tk_window", "root", "data_handler", "alert_system", "copied_definition", "copied_text", \
                "copied_font", "copied_time_stamp", "category_frame", "category_box", "def_entry", \
                "add_definition_btn", "list_box", "notebook_frame", "notebook", "pin_color"

    def __init__(self, root, canvas, data_handler, alert_system, **kwargs):
        tk.Frame.__init__(self, canvas, **kwargs)
        self.tk_window = root
        self.root = canvas
        self.data_handler = data_handler
        self.alert_system = alert_system
        self.alert_system.layout = self
        self.copied_definition = None
        self.copied_text = None
        self.copied_font = None
        self.copied_time_stamp = None

        self.category_frame = None
        self.category_box = None

        self.def_entry = None
        self.add_definition_btn = None
        self.list_box = None

        self.notebook_frame = None
        self.notebook = None

        self.pin_color = "yellow"

        self.create_ui()
        self.event_biding()

        self.set_category_list(self.data_handler.get_last_category())

    def create_ui(self):
        parent_frame = ttk.Frame(self.root, relief="ridge", borderwidth=2, width=30)
        parent_frame.pack(anchor='nw', fill='x', pady=8, padx=8)
        # parent_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.17, bordermode="inside")

        # listbox frame
        listbox_frame = ttk.Frame(self.root, width=100,
                                  height=SCREEN_HEIGHT, relief="ridge", borderwidth=8)
        listbox_frame.pack(fill='both', side='left', padx=8, pady=8)

        self.category_frame = ttk.Frame(parent_frame)
        self.category_frame.pack(side='left', anchor='w', expand=True, fill='x')

        user_name_frame = ttk.Frame(parent_frame)
        user_name_frame.pack(side='right', anchor='se')

        ttk.Label(self.category_frame, text="Categories:", font=DEFAULT_FONT_BOLD,
                  style="H.TLabel").grid(row=0, column=0, pady=6)

        ttk.Button(self.category_frame, text="Add", style="Accent.TButton", width=0,
                   command=lambda: self.add_category_view()).grid(row=1, column=2, pady=4)

        # Create the drop-down category
        self.category_box = ttk.Combobox(self.category_frame, values=self.data_handler.get_categories_by_list(),
                                         font=DEFAULT_FONT_BOLD, state="readonly", style="R.TCombobox")
        self.category_box.grid(row=1, column=0, padx=4, pady=8)

        ttk.Label(self.category_frame, text="Alerts:", font=DEFAULT_FONT_BOLD, style="H.TLabel").grid(row=1,
                                                                                                      column=3,
                                                                                                      padx=2)

        ttk.Label(user_name_frame, text=f"User: {self.data_handler.current_user}", font=DEFAULT_FONT_BOLD,
                  style="H.TLabel").pack(side='left', anchor='e', padx=4, pady=8)

        ttk.Label(listbox_frame, text="Add Definitions:", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack()

        # Create the entry and button to add definitions
        self.def_entry = ttk.Entry(listbox_frame, validate="key", style="R.TEntry",
                                   validatecommand=(self.root.register(
                                       lambda event: utils.validate_entry(event, self.data_handler.entry_limit)), "%P"),
                                   font=DEFAULT_FONT,
                                   width=21)
        self.def_entry.pack(pady=4, padx=4)

        self.add_definition_btn = ttk.Button(listbox_frame, style="Accent.TButton", text="Add Definition", width=27,
                                             command=lambda: self.add_definition(
                                                 self.def_entry.get(),
                                                 self.category_box.get()))
        self.add_definition_btn.pack(side='top', padx=4, pady=4)

        # Create the listbox to display all the definitions
        self.list_box = CustomListBox(listbox_frame, font=DEFAULT_FONT, selectmode=tk.EXTENDED,
                                      activestyle='none', data_handler=self.data_handler,
                                      category=self.category_box.current(0),
                                      borderwidth=0, highlightthickness=0)
        self.list_box.pack(side='top', fill='both', expand=True, pady=4, padx=4)

        # Create the definition scrollbar
        vert_scroll_bar = ttk.Scrollbar(self.list_box)
        vert_scroll_bar.pack(side='right', fill='y')
        vert_scroll_bar.config(command=self.list_box.yview)

        self.list_box.config(yscrollcommand=vert_scroll_bar.set)

        # Notebook frame
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

    def set_category_list(self, category: str = None) -> None:
        """Set the category list to specified category or to the first one in the list."""
        if category is not None:
            temp_list = self.category_box['values']
            for index, i_d in enumerate(temp_list):
                if i_d == category:
                    self.category_box.current(index)
        else:
            self.category_box.current(0)
        self.update_list()

    def add_category(self, entry: str, window: tk.Toplevel, category: str = None) -> None:
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
                window.after_idle(utils.stay_on_top, window)

        self.def_entry.delete(0, len(entry))
        self.def_entry.focus_set()

    def delete_definition(self, instance: tk.Listbox, index: list) -> None:
        """Deletion of definitions from the given category list."""
        if tk.messagebox.askyesno("Are you sure?", "Deleting is permanent!"):
            category = self.category_box.get()

            # Appends selected definitions to a list
            temp_list = [instance.get(i) for i in index]

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

    def add_category_view(self):
        top_window = tk.Toplevel(self.root)
        utils.set_window(top_window, 250, 180, "Add Category")

        ttk.Label(top_window, text="Examples: ", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(pady=4)

        examples = ttk.Combobox(top_window, values=EXAMPLE_CATEGORIES, font=DEFAULT_FONT_BOLD, style="R.TCombobox",
                                state="readonly")
        examples.pack(padx=4, pady=4)

        ttk.Label(top_window, text="Add Custom Category: ", font=DEFAULT_FONT_BOLD, style="H.TLabel").pack(pady=4)
        entry = ttk.Entry(top_window, validate="key", style="R.TEntry", font=DEFAULT_FONT,
                          width=21,
                          validatecommand=(self.root.register(
                              lambda event: utils.validate_entry(
                                  event, self.data_handler.entry_limit)), "%P"))
        entry.pack(side='top', padx=4, pady=4)

        entry.focus_set()

        ttk.Button(top_window, text="Save Category", width=21, style="Accent.TButton",
                   command=lambda: self.add_category(entry.get(),
                                                     top_window)).pack(side='top', padx=4, pady=4)
        entry.bind("<Return>", lambda e=None: self.add_category(entry.get(), top_window))
        examples.bind("<<ComboboxSelected>>", lambda event=None: self.insert_example(entry, examples))

    @staticmethod
    def insert_example(entry: ttk.Entry, combobox: ttk.Combobox):
        entry.delete(0, tk.END)
        entry.insert(0, combobox.get())
        combobox.selection_clear()

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

    def pin_to_top(self, index):
        self.data_handler.pin_definition(self.category_box.get(), self.list_box.get(index))
        self.update_list()

    def remove_pin(self, index):
        self.data_handler.remove_pin(self.category_box.get())
        self.list_box.itemconfigure(index, foreground=self.list_box['foreground'],
                                    selectforeground=self.list_box['selectforeground'])
        self.list_box.pin = False

    def pop_up_menu(self, event: (tk.Listbox, ttk.Combobox, ttk.Entry)) -> None:
        """Create a popup menu by right-clicking with options."""
        instance = event.widget
        # Listbox drop down menu
        if isinstance(instance, tk.Listbox):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Paste",
                             command=lambda: self.paste_definition())
            index = instance.curselection()
            if index:
                menu.add_command(label="Delete", command=lambda: self.delete_definition(instance, index))
                if len(index) == 1:
                    menu.add_command(label="Rename",
                                     command=lambda: self.create_view(instance, index, state='rdefinition'))
                    menu.add_command(label="Copy",
                                     command=lambda: self.copy_definition(instance, index))
                    pinned = self.data_handler.pinned
                    if instance.get(index) not in pinned.values():
                        menu.add_command(label="Pin To Top",
                                         command=lambda: self.pin_to_top(index))
                    else:
                        menu.add_command(label="Remove Pin",
                                         command=lambda: self.remove_pin(index))

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
        if isinstance(instance, ttk.Entry):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Add Date", command=lambda: self.create_calender(instance))
            menu.add_command(label="Add Current Date", command=lambda: self.add_current_date(instance))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def create_calender(self, instance: ttk.Entry) -> None:
        """Creates the calendar in a top window."""
        top_window = tk.Toplevel(self.root)
        utils.set_window(top_window, 255, 230, "Calender")

        cal = Calendar(top_window)
        cal.pack(expand=1, fill='both', padx=4, pady=4)
        ttk.Button(top_window, text="Add Date", width=21, style="Accent.TButton",
                   command=lambda: self.add_date(instance, cal.format_date(cal.selection()), top_window)).pack(pady=4,
                                                                                                               padx=4)

    @staticmethod
    def add_current_date(instance: ttk.Entry) -> None:
        cur_date = utils.get_current_date()
        instance.delete(0, len(instance.get()))
        instance.insert(0, cur_date)

    @staticmethod
    def add_date(instance: ttk.Entry, date: str, top_window: tk.Toplevel) -> None:
        """Sets the selected date from the calendar into the entry widget."""
        instance.delete(0, len(instance.get()))
        instance.insert(0, date)
        top_window.destroy()

    def get_list_box_item(self) -> str:
        """Returns the selected list-box item if multiple are selected, will return the first one in the index."""
        index = self.list_box.curselection()
        if len(index) > 1:
            return self.list_box.get(index[0])
        else:
            return self.list_box.get(index)

    def update_list(self, word_list: list = None, search: bool = False) -> None:
        """Updates the definition list from selected category or from the searched item."""
        if search:
            self.list_box.delete(0, self.list_box.size())
            for definition in word_list:
                self.list_box.insert(0, definition)
        else:
            category = self.category_box.get()
            if self.list_box.size() != 0:
                self.list_box.delete(0, tk.END)
            temp_list = self.data_handler.get_definitions_by_list(category)
            pinned = self.data_handler.pinned
            if category in pinned.keys():
                self.list_box.insert(0, pinned[category])
                self.list_box.itemconfigure(0, foreground=self.pin_color, selectforeground=self.pin_color)
            self.list_box.category = category
            if temp_list is not None:
                for definition in temp_list:
                    try:
                        if definition != pinned[category]:
                            self.list_box.insert(tk.END, definition)
                    except KeyError:
                        self.list_box.insert(tk.END, definition)
            self.category_box.selection_clear()

    def update_categories(self) -> None:
        """Updates the category selection box with given values from the database."""
        self.category_box.config(values=self.data_handler.get_categories_by_list())


class CustomListBox(DefaultListbox):
    __slots__ = "root", "data_handler", "category", "pin"

    def __init__(self, root, data_handler, category, **kwargs):
        DefaultListbox.__init__(self, root, **kwargs)
        self.root = root
        self.data_handler = data_handler
        self.category = category
        self.pin = False

    def save_new_order(self):
        if self.data_handler is None:
            return
        new_list_order = list(self.get(0, tk.END))
        self.data_handler.update_listbox(new_list_order, self.category)

    def move_item(self, source, target):
        if not self.ctrl_clicked:
            item = self.get(source)
            # To stop any item from being moved to index 0
            if source != 0:
                self.delete(source)
                self.insert(target, item)

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

            pinned = self.data_handler.pinned
            definition = self.get(0)
            if definition in pinned.values():
                self.pin = True
                if self.selection_includes(0):
                    return "break"

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


class CustomNotebook(DefaultNotebook):
    __slots__ = "root", "data_handler", "alert_system", "_active", "packed", "frames"

    def __init__(self, root, alert_system, data_handler, *args, **kwargs):
        kwargs["style"] = "TNotebook"
        DefaultNotebook.__init__(self, root, *args, **kwargs)
        self.root = root
        self.data_handler = data_handler
        self.alert_system = alert_system

        self._active = None
        self.packed = False
        self.frames = {}

        self.bind("<ButtonRelease-1>", self.on_close_release)
        self.bind("<<NotebookTabClosed>>", lambda e=None: self.check_for_unpack())

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

    def delete_frames(self, frames: list) -> None:
        """Deletes frames from the self-frames dict."""
        hit_list = []
        for definition, f in self.frames.items():
            for frame in frames:
                if frame == f:
                    hit_list.append(definition)
        for i in hit_list:
            del self.frames[i]

    def set_tab(self, definition: str) -> None:
        """Brings a currently opened tab into focus."""
        frame = [frame for text, frame in self.frames.items() if text == definition]
        self.select(frame[0])

    def get_tab_frames(self, temp_list: list = None) -> list:
        """Returns the frames of the opened tabs in the notebook."""
        if self.frames == {}:
            return []

        # If given a list of definitions, will return only the frames of those given
        if temp_list:
            close_list = [frame for text, frame in self.frames.items() for i in temp_list if i == text]
        else:
            # Returns all opened tabs
            close_list = [frame for frame in self.frames.values()]
        return close_list

    def pack_notebook(self) -> None:
        """Packs the frame the notebook is on and the notebook itself."""
        # Notebook frame packing
        self.root.pack(expand=True, fill='both', pady=8, padx=8)
        self.pack(expand=True, fill='both', pady=2, padx=2)
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

        current_frame = [frame for frame in self.frames.values() if str(frame) == current_frame]

        if self._active == index:
            self.close_tabs([current_frame[0]], save=True)

        self.state(["!pressed"])
        self._active = None
