# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>
import json

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    import tkinter.font as tkfont

from PIL import ImageTk, Image
import random
from enchant import Dict, tokenize
from enchant.tokenize import en  # Need this for building with pyinstaller, otherwise it doesn't import the en.tokenizer
import os

from custom_calendar import Calendar
from custom_combobox import AutocompleteCombobox
from custom_listbox import CustomListBox
from custom_treeview import TreeView
from settings import *
import utils


class SettingSection:
    _title = "Settings"
    _entry_limit = [str(x) for x in range(1, 36)]
    _tab_limit = [str(x) for x in range(1, 6)]
    _supported_fonts = []
    _font_sizes = [str(x) for x in range(10, 20, 2)]

    def __init__(self, root, data_handler, canvas):
        self.root = root
        self.data_handler = data_handler
        self.canvas = canvas
        self.window = None
        self.limit_entry = None
        self.tab_entry = None
        self.font_choices = None
        self.font_size_choices = None
        self.save_btn = None

        self.background = None

        for i in tkfont.families():
            self._supported_fonts.append(i)

        self.images = [k for k in BACKGROUND_IMAGES.keys()]
        self.create_top_window_view()

    def on_closing(self):
        self.update_database()
        self.window.destroy()

    def create_top_window_view(self):
        self.window = tk.Toplevel(self.root)
        utils.set_window(self.window, 300, 300, self._title)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        top_frame = tk.Frame(self.window)
        middle_frame = tk.Frame(self.window)
        middle_2_frame = tk.Frame(self.window)
        bottom_frame = tk.Frame(self.window)

        # Title
        tk.Label(top_frame, text="Settings Section", font=DEFAULT_FONT_UNDERLINE_BOLD).pack(side='top')

        # Entry character limit
        tk.Label(top_frame, text="Entry Limit:", font=DEFAULT_FONT).pack(side='left', anchor='nw', pady=4, padx=4)
        self.limit_entry = ttk.Combobox(top_frame, values=self._entry_limit, width=3,
                                        font=DEFAULT_FONT, state="readonly")
        self.limit_entry.pack(side='left', anchor='nw', padx=4, pady=4)
        self.limit_entry.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())

        self.set_combobox(limit_entry=True)

        # Tab limit
        tk.Label(top_frame, text="Tab Limit:", font=DEFAULT_FONT).pack(side='left', anchor='nw', pady=4, padx=4)
        self.tab_entry = ttk.Combobox(top_frame, values=self._tab_limit, width=3,
                                      font=DEFAULT_FONT, state="readonly")
        self.tab_entry.pack(side='left', anchor='nw', padx=4, pady=4)
        self.tab_entry.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())

        self.set_combobox(tab_entry=True)

        # Default fonts
        tk.Label(middle_frame, text="Font:", font=DEFAULT_FONT).pack(side='left', anchor='nw', padx=4, pady=4)
        self.font_choices = AutocompleteCombobox(middle_frame, self._supported_fonts,
                                                 font=DEFAULT_FONT)
        self.set_combobox(font=True)

        self.font_choices.pack(side='left', anchor='nw', padx=4, pady=4)

        # Default font size
        tk.Label(middle_2_frame, text="Font Size:", font=DEFAULT_FONT).pack(side='left', anchor='nw', pady=4, padx=4)
        self.font_size_choices = ttk.Combobox(middle_2_frame, values=self._font_sizes, width=3,
                                              font=DEFAULT_FONT, state="readonly")
        self.font_size_choices.pack(side='left', anchor='nw', padx=4, pady=4)
        self.set_combobox(size=True)

        tk.Label(bottom_frame, text="Change Background:", font=DEFAULT_FONT).pack(side='top', padx=4,
                                                                                  pady=4)
        self.background = ttk.Combobox(bottom_frame, values=self.images, font=DEFAULT_FONT,
                                       state='readonly')
        self.background.pack(side='top', anchor='nw', pady=4, padx=4)

        # Command biding
        self.font_choices.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())
        self.font_choices.bind("<<FontChange>>", lambda event=None: self.update_database())
        self.font_size_choices.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())
        self.background.bind("<<ComboboxSelected>>", lambda event=None: self.change_background())

        top_frame.pack(side='top')
        middle_frame.pack(side='top')
        middle_2_frame.pack(side='top')
        bottom_frame.pack(side='top')

    def change_background(self):
        new_image = BACKGROUND_IMAGES[self.background.get()]
        self.canvas.change_background(new_image)
        self.background.selection_clear()

    def update_database(self):
        self.data_handler.entry_limit = int(self.limit_entry.get())
        self.limit_entry.selection_clear()
        self.data_handler.tab_limit = int(self.tab_entry.get())
        self.tab_entry.selection_clear()

        self.data_handler.set_font(self.font_choices.get(), int(self.font_size_choices.get()))
        self.font_choices.selection_clear()
        self.font_size_choices.selection_clear()

    def set_combobox(self, limit_entry: bool = False, tab_entry: bool = False,
                     font: bool = False, size: bool = False) -> None:
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
        if font:
            selection = self.data_handler.default_font[0]
            temp_list = self.font_choices['values']
            _use_default_font = False
            if selection not in temp_list:
                _use_default_font = True
            for index, i_d in enumerate(temp_list):
                if _use_default_font:
                    if i_d == DEFAULT_FONT_TAB:
                        self.font_choices.current(index)
                else:
                    if i_d == selection:
                        self.font_choices.current(index)
        if size:
            selection = str(self.data_handler.default_font[1])
            temp_list = self.font_size_choices['values']
            _use_default_size = False
            if selection not in temp_list:
                _use_default_size = True
            for index, i_d in enumerate(temp_list):
                if _use_default_size:
                    if i_d == DEFAULT_FONT_SIZE:
                        self.font_size_choices.current(index)
                else:
                    if i_d == selection:
                        self.font_size_choices.current(index)


class HelpSection:
    _title = "Help Section"
    _options = ["Keyboard Shortcuts", "Functions"]
    _functions_filepath = os.path.join(os.getcwd(), "Core", "Docs", "functions_docs.txt")
    _keyboard_filepath = os.path.join(os.getcwd(), "Core", "Docs", "keyboard_docs.txt")

    def __init__(self, root):
        self.root = root
        self.window = None
        self.text = None
        self.combo_box = None
        self._functions = utils.read_txt(self._functions_filepath)
        self._keyboard_shortcuts = utils.read_txt(self._keyboard_filepath)
        self.create_top_window_view()

    def create_top_window_view(self):
        self.window = tk.Toplevel(self.root)
        utils.set_window(self.window, 600, 500, self._title)
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

        text_frame.pack(expand=True, fill="both")

        self.window.focus_set()
        self.update_text()

    def update_text(self) -> None:
        if self.combo_box.get() == "Keyboard Shortcuts":
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", "end-1c")
            for item in self._keyboard_shortcuts:
                self.text.insert(tk.END, item)
                self.text.insert(tk.END, "\n")
            self.text.config(state=tk.DISABLED)
        elif self.combo_box.get() == "Functions":
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", "end-1c")
            for item in self._functions:
                self.text.insert(tk.END, item)
                self.text.insert(tk.END, "\n")
            self.text.config(state=tk.DISABLED)
        self.combo_box.selection_clear()


class BackGround(tk.Canvas):
    _bg_image = None

    def __init__(self, root, *args, **kwargs):
        tk.Canvas.__init__(self, root, *args, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.images_paths = [v for v in BACKGROUND_IMAGES.values()]
        self._image_path = random.choice(self.images_paths)
        image = Image.open(self._image_path).resize((self.winfo_width(), self.winfo_height()), Image.ANTIALIAS)
        self.background_img = ImageTk.PhotoImage(image)
        self.image = None
        self.pack(expand=True, fill="both")
        self.drawn = self.create_image(0, 0, image=self.background_img, anchor='nw')

    def on_resize(self, event):
        new_size = Image.open(self._image_path).resize((event.width, event.height), Image.ANTIALIAS)

        bg = ImageTk.PhotoImage(new_size)
        self.image = bg  # Need this so python doesn't get rid of it before it's drawn to the screen

        self.itemconfig(self.drawn, image=self.image)

    def change_background(self, image: str) -> None:
        # Image is the file path to the selected image.
        height = self.winfo_height()
        width = self.winfo_width()
        # Reset the image path
        self._image_path = image
        # Resize to the screen
        new_size = Image.open(image).resize((width, height), Image.ANTIALIAS)
        # Convert to photo image
        self.image = ImageTk.PhotoImage(new_size)
        # Set the canvas to the new image
        self.itemconfig(self.drawn, image=self.image)


class TextArea(tk.Text):
    locale = 'en'

    def __init__(self, text_frame, data_handler, category, definition, alert_system, *args, **kwargs):
        tk.Text.__init__(self, text_frame, *args, **kwargs)
        self.data_handler = data_handler
        self.alert_system = alert_system
        self.corpus = Dict(self.locale)
        self.tokenize = tokenize.get_tokenizer(self.locale)
        self._proxy = self._w + "_proxy"
        self.tk.call("rename", self._w, self._proxy)
        self.tk.createcommand(self._w, self._proxy_cmd)
        self.tag_configure('sic', foreground='red')
        self.bind('<<TextModified>>', self.on_modify)
        self.bind("<ButtonPress-3>", lambda event: self.pop_up_menu(event))

        self.selected_word = ""
        self.suggested_words = {}
        self.after_id = None

        self.insert(tk.END, self.data_handler.get_text_by_definition(category, definition))

        # Create the scrollbar for the text
        scroll_bar = ttk.Scrollbar(text_frame, orient='vertical', command=self.yview)
        self.config(yscrollcommand=scroll_bar.set)

        scroll_bar.pack(in_=text_frame, side='right', fill='y', expand=False)
        self.pack(in_=text_frame, side='left', fill='both', expand=True, padx=4)

    def pop_up_menu(self, event):
        try:
            self.selected_word = self.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return
        # Check if multiple words are selected via having a space in them.
        if " " in self.selected_word:
            return
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

    def replace_word(self, word):
        try:
            self.replace(tk.SEL_FIRST, tk.SEL_LAST, word)
        except tk.TclError:
            pass

    def add_to_dict(self, word):
        self.replace(tk.SEL_FIRST, tk.SEL_LAST, word)
        self.corpus.add(word)

    def _proxy_cmd(self, command, *args):
        """Intercept the Tk commands to the text widget and if any of the content
        modifying commands are called, post a TextModified event."""
        cmd = (self._proxy, command)
        if args:
            cmd = cmd + args
        try:
            result = self.tk.call(cmd)
            if command in ('insert', 'delete', 'replace'):
                self.event_generate('<<TextModified>>')
            return result
        except tk.TclError as e:
            self.alert_system.show_alert(("Highlight a text in order to spell check it.", "White"))

    def on_modify(self, event):
        """Rate limit the spell-checking with a 100ms delay. If another modification
        event comes in within this time, cancel the after call and re-schedule."""
        try:
            if self.after_id:
                self.after_cancel(self.after_id)
            self.after_id = self.after(250, self.on_modified)
        except IndexError:
            pass

    def on_modified(self):
        self.after_id = None
        self.tag_remove('sic', '1.0', 'end')
        num_lines = [int(val) for val in self.index("end").split(".")][0]
        for line in range(1, num_lines):
            data = self.get(f"{line}.0 linestart", f"{line}.0 lineend")
            for word, pos in self.tokenize(data):
                check = self.corpus.check(word)
                if not check:
                    start = f"{line}.{pos}"
                    end = f"{line}.{pos + len(word)}"
                    self.tag_add("sic", start, end)
                    self.suggested_words.update({word: self.corpus.suggest(word)})


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
        self.font_choices = AutocompleteCombobox(top_frame, self._supported_fonts,
                                                 font=DEFAULT_FONT)
        self.font_choices.pack(side='left', padx=4, pady=4)
        self.font_choices.bind("<<ComboboxSelected>>",
                               lambda event=None: self.change_font(self.font_choices.get(),
                                                                   self.font_size_choices.get(), category,
                                                                   definition))
        self.font_choices.bind("<<FontChange>>", lambda event=None: self.change_font(self.font_choices.get(),
                                                                                     self.font_size_choices.get(),
                                                                                     category,
                                                                                     definition))

        self.font_size_choices = ttk.Combobox(top_frame, values=self._font_sizes, width=3,
                                              font=DEFAULT_FONT, state="readonly")
        self.font_size_choices.pack(side='left', padx=4, pady=4)
        self.font_size_choices.bind("<<ComboboxSelected>>",
                                    lambda event=None: self.change_font(self.font_choices.get(),
                                                                        self.font_size_choices.get(), category,
                                                                        definition))

        # Create the text area
        self.text_area = TextArea(text_frame, self.data_handler, category, definition, self.alert_system,
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

        self.text_area.bind("<End>", lambda event=None: self.notebook.close_tabs(
            self.notebook.get_tab_frames([definition]), save=True))

        self.set_combobox(category, definition)

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
        for index, i_d in enumerate(fonts):
            if _use_default_font:
                if i_d == DEFAULT_FONT_TAB:
                    self.font_choices.current(index)
            else:
                if i_d == f:
                    self.font_choices.current(index)
        for index, i_d in enumerate(sizes):
            if _use_default_size:
                if i_d == DEFAULT_FONT_SIZE:
                    self.font_size_choices.current(index)
            else:
                if i_d == str(s):
                    self.font_size_choices.current(index)


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
            self.search_frame.grid(row=0, column=4, columnspan=5)
            self.search_entry = tk.Entry(self.search_frame, width=21, font=DEFAULT_FONT, validate="key",
                                         background=ENTRY_COLOR,
                                         validatecommand=(self.root.register(
                                             lambda event: utils.validate_entry(
                                                 event, self.data_handler.entry_limit)), "%P"))

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


class ImportView(tk.Toplevel):

    def __init__(self, root, data_handler, filepath, main_layout, **kwargs):
        tk.Toplevel.__init__(self, root, **kwargs)
        utils.set_window(self, 800, 500, "Import")
        self.data_handler = data_handler
        self.main_layout = main_layout

        with open(filepath, 'r') as file:
            self.data = json.load(file)

        self.formatted_data = {}
        for c in self.data.keys():
            self.formatted_data.update({c: list(self.data[c].keys())})

        self.category_box = None
        self.list_box = None
        self.tree_view = None

        self.create_ui()
        self.update_list()

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
        tk.Label(top_left_frame, text="Opened File:", font=DEFAULT_FONT).pack(side='top', padx=4, pady=4)
        self.category_box = ttk.Combobox(top_left_frame, values=[item for item in self.data.keys()],
                                         font=DEFAULT_FONT, state="readonly")
        self.category_box.pack(side='top', padx=4, pady=4)
        self.category_box.bind("<<ComboboxSelected>>", lambda event=None: self.update_list())

        # Create the listbox to display all the definitions
        self.list_box = CustomListBox(top_left_frame, height=SCREEN_HEIGHT, font=DEFAULT_FONT, selectmode=tk.EXTENDED,
                                      activestyle=tk.DOTBOX, data_handler=self.data_handler,
                                      category=self.category_box.current(0))
        self.list_box.pack(side='top', expand=True, fill='both', pady=4, padx=4)
        self.list_box.configure(highlightcolor=BLACK)
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

        tk.Label(right, text="Functions:", font=DEFAULT_FONT).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Remove All", width=18,
                   command=lambda: self.tree_view.remove_all_elements()).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Remove Selected", width=18,
                   command=lambda: self.tree_view.remove_elements()).pack(side='top', pady=4, padx=4)

        ttk.Button(right, style="Accent.TButton", text="Export All", width=18,
                   command=lambda: self.tree_view.add_all_elements(self.formatted_data, importing=True)).pack(
            side='top', pady=4, padx=4)

        ttk.Button(right, style="Accent.TButton", text="Export Selected", width=18,
                   command=lambda: self.add_selected()).pack(side='top', pady=4, padx=4)
        ttk.Button(right, style="Accent.TButton", text="Finish", width=18,
                   command=lambda: self.finalize()).pack(side='top', pady=4, padx=4)

        tk.Label(left, text="Existing Data:", font=DEFAULT_FONT).pack(side='top', pady=4, padx=4)
        self.tree_view = TreeView(left, self.data_handler)
        self.tree_view.add_default_items(self.data_handler.get_categories_definitions_formatted(), importing=True,
                                         exception=True)
        self.tree_view.pack(side='top', fill='both', expand=True, padx=4, pady=4)

    def add_selected(self):
        category = self.tree_view.item_selected
        if category is None:
            category = self.category_box.get()
        indexes = self.list_box.curselection()
        elements = [self.list_box.get(i) for i in indexes]

        self.tree_view.add_elements(category, elements)

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

    def finalize(self):
        """Passes data off to data_handler to import in into the current user's data."""
        data = self.tree_view.get_all_elements()

        if data == self.data_handler.get_categories_definitions_formatted():
            tk.messagebox.showinfo("Nothing to Add", "No Data to be imported.")
            self.focus_set()
            return

        if data is None:
            tk.messagebox.showinfo("No Data", "No Data to be imported.")
            self.focus_set()
            return

        if tk.messagebox.askyesno("Importing Data", "Are you sure you want to import this data?"
                                                    "A backup of your existing data will be created."):
            check = self.data_handler.import_data(data, self.data)
            if check:
                self.main_layout.update_categories()
                self.main_layout.category_box.current(0)
                self.main_layout.update_list()
                tk.messagebox.showinfo("Import Success", "Data has been imported.")
                self.destroy()


class ExportView(tk.Toplevel):

    def __init__(self, root, data_handler, **kwargs):
        tk.Toplevel.__init__(self, root, **kwargs)
        utils.set_window(self, 800, 500, "Export")
        self.data_handler = data_handler

        self.category_box = None
        self.list_box = None
        self.tree_view = None

        self.create_ui()
        self.update_list()

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
        tk.Label(top_left_frame, text="Categories", font=DEFAULT_FONT).pack(side='top', padx=4, pady=4)
        self.category_box = ttk.Combobox(top_left_frame, values=self.data_handler.get_categories_by_list(),
                                         font=DEFAULT_FONT, state="readonly")
        self.category_box.pack(side='top', padx=4, pady=4)
        self.category_box.bind("<<ComboboxSelected>>", lambda event=None: self.update_list())

        # Create the listbox to display all the definitions
        self.list_box = CustomListBox(top_left_frame, height=SCREEN_HEIGHT, font=DEFAULT_FONT, selectmode=tk.EXTENDED,
                                      activestyle=tk.DOTBOX, data_handler=self.data_handler,
                                      category=self.category_box.current(0))
        self.list_box.pack(side='top', expand=True, fill='both', pady=4, padx=4)
        self.list_box.configure(highlightcolor=BLACK)
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

        tk.Label(right, text="Functions:", font=DEFAULT_FONT).pack(side='top', pady=4, padx=4)
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

        tk.Label(left, text="Preview:", font=DEFAULT_FONT).pack(side='top', pady=4, padx=4)
        self.tree_view = TreeView(left, self.data_handler)
        self.tree_view.pack(side='top', fill='both', expand=True, padx=4, pady=4)

    def add_selected(self):
        category = self.category_box.get()
        indexes = self.list_box.curselection()
        elements = [self.list_box.get(i) for i in indexes]

        self.tree_view.add_elements(category, elements)

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

    def finalize(self):
        """This will send all data to data_handler to export the proper data to a json file."""
        data = self.tree_view.get_all_elements()
        if data is None:
            tk.messagebox.showinfo("No Data", "No Data to be exported.")
            self.focus_set()
            return

        if tk.messagebox.askyesno("Exporting Data", "Are you sure you want to export this data?"):
            check = self.data_handler.export_data(data)
            if check:
                tk.messagebox.showinfo("Export Success", "Data has been exported.")
                self.destroy()


class Layout(tk.Frame):

    def __init__(self, canvas, data_handler, alert_system, **kwargs):
        tk.Frame.__init__(self, canvas, **kwargs)
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

        self.create_ui()

        self.set_category_list(self.data_handler.get_last_category())

    def create_ui(self):
        parent_frame = ttk.Frame(self.root, relief="ridge", borderwidth=2, width=25)
        parent_frame.pack(anchor='nw', fill='x', pady=8, padx=8)

        self.category_frame = ttk.Frame(parent_frame)
        self.category_frame.pack(side='left', anchor='w')

        tool_frame = ttk.Frame(parent_frame)
        tool_frame.pack(side='right', anchor='se')

        tk.Label(self.category_frame, text="Select Category:", font=DEFAULT_FONT).grid(row=0, column=0, pady=6)

        ttk.Button(self.category_frame, text="Add", style="Accent.TButton", width=0,
                   command=lambda: self.create_view(state="acategory")).grid(row=1, column=2, pady=4)

        # Create the drop-down category
        self.category_box = ttk.Combobox(self.category_frame, values=self.data_handler.get_categories_by_list(),
                                         font=DEFAULT_FONT, state="readonly")
        self.category_box.grid(row=1, column=0, padx=4, pady=4)

        tk.Label(self.category_frame, text="Alerts:", font=DEFAULT_FONT).grid(row=1, column=3)

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
            menu.add_command(label="Add Current Date", command=lambda: self.add_current_date(instance))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def create_calender(self, instance: tk.Entry) -> None:
        """Creates the calendar in a top window."""
        top_window = tk.Toplevel(self.root)
        utils.set_window(top_window, 255, 230, "Calender")

        cal = Calendar(top_window)
        cal.pack(expand=1, fill='both', padx=4, pady=4)
        ttk.Button(top_window, text="Add Date", width=21, style="Accent.TButton",
                   command=lambda: self.add_date(instance, cal.format_date(cal.selection()), top_window)).pack(pady=4,
                                                                                                               padx=4)

    def add_current_date(self, instance: tk.Entry) -> None:
        cur_date = utils.get_current_date()
        instance.delete(0, len(instance.get()))
        instance.insert(0, cur_date)

    @staticmethod
    def add_date(instance: tk.Entry, date: str, top_window: tk.Toplevel) -> None:
        """Sets the selected date from the calendar into the entry widget."""
        instance.delete(0, len(instance.get()))
        instance.insert(0, date)
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

        self.style = ttk.Style(self.root)
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
