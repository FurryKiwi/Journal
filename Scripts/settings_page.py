# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog
    import tkinter.font as tkfont
    from tkinter.colorchooser import askcolor

import os
from PIL import Image

from CustomTkWidgets.custom_frames import SelectableFrames
from CustomTkWidgets.custom_combobox import AutocompleteCombobox, CustomComboWithClassName
from CustomTkWidgets.custom_scrollable_frames import VerticalScrolledFrame
import Scripts.utils as utils
from Scripts.settings import *


class SettingsPage(tk.Toplevel):
    _width, _height = 800, 500
    _title = "Settings"
    _headers = ["General", "Appearance", "Background", "Backup/Restore", "Documentation"]
    __slots__ = "root", "data_handler", "canvas", "style_manager", "main_layout"

    def __init__(self, root, data_handler, canvas, style_manager, main_layout):
        tk.Toplevel.__init__(self, root)
        self.root = root
        self.data_handler = data_handler
        self.canvas = canvas
        self.style_manager = style_manager
        self.main_layout = main_layout

        self.frame_bg = str(self.style_manager.style.lookup(self.style_manager.theme, "background"))
        self.frame_select_bg = str(self.style_manager.style.lookup(self.style_manager.theme, "selectbackground"))

        utils.set_window(self, self._width, self._height, self._title, parent=self.root, offset=(-380, -200))

        custom_frames = CustomFrames(self, self._headers, self.frame_bg, self.frame_select_bg, root, data_handler,
                                     canvas, style_manager, main_layout)
        custom_frames.pack(side='left', fill='y', expand=True, anchor='nw', padx=4, pady=4)


class CustomFrames(SelectableFrames):
    __slots__ = "top_level", "root", "data_handler", "canvas", "style_manager", "main_layout", "general", \
                "appearance", "backup", "docs",

    def __init__(self, top_level, headers: list, background: str, active_background: str, root,
                 data_handler, canvas, style_manager, main_layout, **kwargs):
        self.top_level = top_level
        self.root = root
        self.data_handler = data_handler
        self.canvas = canvas
        self.style_manager = style_manager
        self.main_layout = main_layout

        self.general = None
        self.appearance = None
        self.background_section = None
        self.backup = None
        self.docs = None

        SelectableFrames.__init__(self, top_level, headers, background, active_background, **kwargs)
        self._setup_frames()
        self.change_frame(widget=self.initial_selected)

    def _setup_frames(self):
        frame = self.get_new_frame("General")
        self.general = GeneralSection(frame, self.data_handler, class_="General")
        frame = self.get_new_frame("Appearance")
        self.appearance = AppearanceSection(frame, self.root, self.top_level,
                                            self.style_manager, class_="Appearance")
        frame = self.get_new_frame("Background")
        self.background_section = BackgroundSection(frame, self.data_handler, self.canvas, self.top_level,
                                                    class_="Background")
        frame = self.get_new_frame("Backup/Restore")
        self.backup = BackupSection(frame, self.root, self.main_layout, self.data_handler,
                                    self.top_level, class_="Backup/Restore")
        frame = self.get_new_frame("Documentation")
        self.help = HelpSection(frame, class_="Documentation")

    def select_frame(self, class_name):
        """Sets the selected frame. This method is meant to be overridden by child class."""
        if self.options_frame is not None and self.options_frame.class_name == class_name:
            return

        if self.options_frame is not None:
            self.deselect_frame()

        if class_name == "General":
            self.options_frame = self.general
            self.options_frame.parent.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        elif class_name == "Appearance":
            self.options_frame = self.appearance
            self.options_frame.parent.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        elif class_name == "Background":
            self.options_frame = self.background_section
            self.options_frame.parent.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        elif class_name == "Backup/Restore":
            self.options_frame = self.backup
            self.options_frame.parent.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        elif class_name == "Documentation":
            self.options_frame = self.help
            self.options_frame.parent.pack(side='left', fill='both', expand=True, padx=4, pady=4)
            self.root.event_generate("<<HelpSectionCreated>>")

    def deselect_frame(self):
        """Unpacks the selected frame. This method is meant to be overridden by child class."""
        if self.options_frame is not None:
            self.options_frame.parent.pack_forget()


class GeneralSection:
    _entry_limit = [str(x) for x in range(1, 36)]
    _tdl_limit = [str(x) for x in range(30, 210, 10)]
    _tab_limit = [str(x) for x in range(1, 5)]
    _font_sizes = [str(x) for x in range(10, 20, 2)]
    _default_font_tab = "Arial"
    _default_size_tab = "12"
    _font = ("Arial", 14)
    _pady = 15
    _padx = 7
    _defaults = {"limit_entry": 20,
                 "tdl_entry": 80,
                 "tab_entry": 4,
                 "font_size_choices": 12}
    _labels = ["Entry Limit", "ToDoList Limit", "Tab Limit", "Font Size", "Font"]
    __slots__ = "parent", "class_name", "data_handler", "limit_entry", "tab_entry", \
                "font_choices", "font_size_choices", "save_btn", \
                "_supported_fonts", "main_frame", "tdl_entry"

    def __init__(self, parent_frame, data_handler, **kwargs):
        self.class_name = kwargs['class_']
        self.parent = parent_frame
        self.data_handler = data_handler
        self.limit_entry = None
        self.tdl_entry = None
        self.tab_entry = None
        self.font_choices = None
        self.font_size_choices = None
        self.save_btn = None

        self._supported_fonts = []

        for i in tkfont.families():
            self._supported_fonts.append(i)
        # To make sure there are no duplicates being added.
        self._supported_fonts = set(self._supported_fonts)

        ttk.Button(self.parent, text="Reset To Defaults", style="Accent.TButton", width=16,
                   command=self.reset_config).pack(side='top', anchor='nw', padx=4)

        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(side='top', expand=True, fill='both')

        self.create_ui()

    def create_ui(self):

        combo_box_styles = {"limit_entry": self._entry_limit,
                            "tdl_entry": self._tdl_limit,
                            "tab_entry": self._tab_limit,
                            "font_size_choices": self._font_sizes
                            }

        vs_frame = VerticalScrolledFrame(self.main_frame, scroll_lock=True)
        vs_frame.pack(side='top', fill='both', expand=True, pady=10, anchor='center')

        utils.create_labels_grid(vs_frame.interior, self._labels, self._font, "R.TLabel", self._pady, self._padx + 30)
        returned_values, last_index = utils.create_dynamic_combo(vs_frame.interior, combo_box_styles, DEFAULT_FONT,
                                                                 "R.TCombobox", "readonly", self._pady,
                                                                 self._padx, offset=30)

        for key, combo in returned_values.items():
            if key == "limit_entry":
                self.limit_entry = combo
            elif key == "tdl_entry":
                self.tdl_entry = combo
            elif key == "tab_entry":
                self.tab_entry = combo
            elif key == "font_size_choices":
                self.font_size_choices = combo

        self.limit_entry.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())
        self.tdl_entry.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())
        self.tab_entry.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())
        self.font_size_choices.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())

        self.font_choices = AutocompleteCombobox(vs_frame.interior, self._supported_fonts, style="R.TCombobox",
                                                 font=DEFAULT_FONT)
        self.font_choices.grid(column=1, row=last_index, pady=self._pady, padx=self._padx)
        self.font_choices.bind("<<ComboboxSelected>>", lambda event=None: self.update_database())
        self.font_choices.bind("<Return>", lambda event=None: self.update_database())
        self.set_all_combos()

    def update_database(self):
        self.data_handler.entry_limit = int(self.limit_entry.get())
        self.limit_entry.selection_clear()
        self.data_handler.tdl_limit = int(self.tdl_entry.get())
        self.tdl_entry.selection_clear()
        self.data_handler.tab_limit = int(self.tab_entry.get())
        self.tab_entry.selection_clear()

        self.data_handler.set_font(self.font_choices.get(), int(self.font_size_choices.get()))
        self.font_choices.selection_clear()
        self.font_size_choices.selection_clear()

    def set_limit_entry_combo(self):
        selection = str(self.data_handler.entry_limit)
        temp_list = self.limit_entry['values']
        for index, i_d in enumerate(temp_list):
            if i_d == selection:
                self.limit_entry.current(index)

    def set_tab_entry_combo(self):
        selection = str(self.data_handler.tab_limit)
        temp_list = self.tab_entry['values']
        for index, i_d in enumerate(temp_list):
            if i_d == selection:
                self.tab_entry.current(index)

    def set_tdl_combo(self):
        selection = str(self.data_handler.tdl_limit)
        temp_list = self.tdl_entry['values']
        for index, i_d in enumerate(temp_list):
            if i_d == selection:
                self.tdl_entry.current(index)

    def set_font_combo(self):
        selection = self.data_handler.default_font[0]
        temp_list = self.font_choices['values']
        _use_default_font = False
        if selection not in temp_list:
            _use_default_font = True
        for index, i_d in enumerate(temp_list):
            if _use_default_font:
                if i_d == self._default_font_tab:
                    self.font_choices.current(index)
            else:
                if i_d == selection:
                    self.font_choices.current(index)

    def set_font_size_combo(self):
        selection = str(self.data_handler.default_font[1])
        temp_list = self.font_size_choices['values']
        _use_default_size = False
        if selection not in temp_list:
            _use_default_size = True
        for index, i_d in enumerate(temp_list):
            if _use_default_size:
                if i_d == self._default_size_tab:
                    self.font_size_choices.current(index)
            else:
                if i_d == selection:
                    self.font_size_choices.current(index)

    def set_all_combos(self):
        self.set_limit_entry_combo()
        self.set_tab_entry_combo()
        self.set_tdl_combo()
        self.set_font_combo()
        self.set_font_size_combo()

    def reset_config(self):
        self.data_handler.reset_default_config()
        self.set_all_combos()


class HelpSection:
    _title = "Help Section"
    _options = ["Keyboard Shortcuts", "Functions"]
    _functions_filepath = os.path.join(os.getcwd(), "Core", "Docs", "functions_docs.txt")
    _keyboard_filepath = os.path.join(os.getcwd(), "Core", "Docs", "keyboard_docs.txt")
    __slots__ = "parent", "class_name", "main_frame", "combo_box", "text", "_functions", "_keyboard_shortcuts"

    def __init__(self, parent_frame, **kwargs):
        self.class_name = kwargs['class_']
        self.parent = parent_frame

        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(side='top', expand=True, fill='both')

        self.combo_box = None
        self.text = None

        self._functions = utils.read_txt(self._functions_filepath)
        self._keyboard_shortcuts = utils.read_txt(self._keyboard_filepath)

        self.create_view()

    def create_view(self):
        self.combo_box = ttk.Combobox(self.main_frame, values=self._options, state="readonly",
                                      font=DEFAULT_FONT, style="R.TCombobox")
        self.combo_box.pack(side='top', pady=8, padx=4)
        self.combo_box.current(0)
        self.combo_box.bind("<<ComboboxSelected>>", lambda event=None: self.update_text())

        text_frame = ttk.Frame(self.main_frame, borderwidth=1, relief="sunken")

        self.text = tk.Text(text_frame, font=DEFAULT_FONT, wrap=tk.WORD)

        # Create the scrollbar for the text
        scroll_bar = ttk.Scrollbar(text_frame, orient='vertical', command=self.text.yview)
        self.text.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(in_=text_frame, side='right', fill='y', expand=False)
        self.text.pack(in_=text_frame, side='left', fill='both', expand=True)

        text_frame.pack(expand=True, fill="both", padx=4)

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


class AppearanceSection:
    _font = ("Arial", 14)
    _pady = 15
    _padx = 7
    _foreground_labels = ['Button FG', 'Export/Import FG', 'Tabs FG', 'Selector Boxes FG', 'Header Labels FG',
                          'Regular Labels FG', 'Settings Headers FG', 'Settings Frames FG', 'Entry FG',
                          'Document Text FG', 'Listbox FG', 'Menu FG', 'Pin Text FG', 'Checkbutton FG']
    _colors_dir_path = os.path.join(os.getcwd(), "Core", "Docs")
    _colors_txt_path = os.path.join(_colors_dir_path, "color_options.txt")

    __slots__ = "class_name", "parent", "root", "top_level", "style_manager", "_styles", "events", "main_frame", \
                "fg_combo_boxes", "color_box_labels", "fonts"

    def __init__(self, parent_frame, root, top_level, style_manager, **kwargs):
        self.class_name = kwargs['class_']
        self.parent = parent_frame
        self.root = root
        self.top_level = top_level
        self.style_manager = style_manager
        self._styles = self.style_manager.all_styles
        self.events = []

        title_frame = ttk.Frame(self.parent)
        title_frame.pack(side='top', fill='x')

        ttk.Button(title_frame, text="Reset To Defaults", style="Accent.TButton", width=16,
                   command=self.reset_to_defaults).pack(side='left', padx=4)
        ttk.Button(title_frame, text="Apply Style", style="Accent.TButton", width=16,
                   command=self.apply_style).pack(side='right', padx=4)

        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(side='top', expand=True, fill='both')

        self.fg_combo_boxes = None
        self.color_box_labels = None

        self.create_ui()

    def create_ui(self):

        vs_frame = VerticalScrolledFrame(self.main_frame)
        vs_frame.pack(side='top', fill='both', expand=True, pady=10, anchor='center')

        button_values = utils.read_colors_list(self._colors_txt_path)

        utils.create_labels_grid(vs_frame.interior, self._foreground_labels, self._font, "R.TLabel", self._pady,
                                 self._padx)
        self.fg_combo_boxes, self.color_box_labels = utils.create_combo_grid(vs_frame.interior, self._styles,
                                                                             "foreground", button_values,
                                                                             font=DEFAULT_FONT, style="R.TCombobox",
                                                                             state="readonly",
                                                                             pad_y=self._pady, pad_x=self._padx)
        for combo in self.fg_combo_boxes:
            combo.bind("<<ComboboxSelected>>", lambda event: self.events.append(event))
        for label in self.color_box_labels:
            label.bind("<Button-1>", lambda event: self.change_color(event))

        self.set_combo_boxes()

    def change_color(self, event):
        event.widget.choose_color()
        self.events.append(event)

    def set_combo_boxes(self):
        for combo in self.fg_combo_boxes:
            value = self.style_manager.get_style(combo.class_name, combo.type_class)
            for index, val in enumerate(combo['values']):
                if value not in combo['values']:
                    combo.current(0)
                if value == val:
                    combo.current(index)

        for label in self.color_box_labels:
            value = self.style_manager.get_style(label.class_name, label.type_class)
            label["background"] = value

    def apply_style(self):
        self.style_manager.set_style(self.events)
        self.events = []
        self.set_combo_boxes()

    def reset_to_defaults(self):
        self.style_manager.reset_to_defaults()
        self.set_combo_boxes()


class BackupSection:
    _offset = 4
    _font = ("Arial", 14)
    _pady = 15
    _padx = 7 + _offset
    _labels = ["Create a Back Up", "Restore Last Back Up", "Auto Back Up:(Seconds)"]
    __slots__ = "class_name", "parent", "root", "main_layout", "data_handler", "top_level", "main_frame"

    def __init__(self, parent_frame, root, main_layout, data_handler, top_level, **kwargs):
        self.class_name = kwargs['class_']
        self.parent = parent_frame
        self.root = root
        self.main_layout = main_layout
        self.data_handler = data_handler
        self.top_level = top_level

        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(side='top', expand=True, fill='both')

        self.root.bind("<<RestoredData>>", lambda event=None: self.setup())

        self.create_ui()

    def create_ui(self):
        index = 0

        vs_frame = VerticalScrolledFrame(self.main_frame, scroll_lock=True)
        vs_frame.pack(side='top', fill='both', expand=True, pady=10, anchor='center')

        utils.create_labels_grid(vs_frame.interior, self._labels, self._font, "R.TLabel", self._pady, self._padx)

        ttk.Button(vs_frame.interior, text="Manual Back Up", width=27, style="Accent.TButton",
                   command=lambda: self.backup_data()).grid(column=1, row=index, pady=self._pady, padx=self._padx)
        index += 1

        ttk.Button(vs_frame.interior, text="Restore", width=27, style="Accent.TButton",
                   command=self.restore_user).grid(column=1, row=index, pady=self._pady, padx=self._padx)
        index += 1

        auto_backup_frame = ttk.Frame(vs_frame.interior)
        auto_backup_frame.grid(column=1, row=index, padx=self._padx, pady=self._pady - 10)

        times = [t for t in self.data_handler.time_frames.keys()]
        time_choice = ttk.Combobox(auto_backup_frame, values=times, width=4,
                                   font=DEFAULT_FONT, state="readonly", style="R.TCombobox")
        time_choice.pack(side='left', pady=self._pady, padx=self._padx - self._offset)
        time_choice.current(0)

        ttk.Button(auto_backup_frame, text="Auto", width=7, style="Accent.TButton",
                   command=lambda: self.data_handler.start_auto_backup(time_choice.get())) \
            .pack(side='left', pady=self._pady, padx=self._padx - self._offset)

        ttk.Button(auto_backup_frame, text="Cancel", width=7, style="Accent.TButton",
                   command=lambda: self.data_handler.cancel_backup()).pack(side='left',
                                                                           pady=self._pady,
                                                                           padx=self._padx - self._offset)

    def restore_user(self) -> None:
        """Calls the restore function of the current user's data."""
        self.data_handler.restore_backup(self.top_level)

    def setup(self):
        self.main_layout.notebook.close_tabs(clearing=True)
        self.main_layout.update_categories()
        self.main_layout.set_category_list()
        self.main_layout.update_list()
        self.top_level.focus_set()

    def backup_data(self) -> None:
        if tk.messagebox.askyesno("Backup Data", "Are you sure you want to backup your data?",
                                  parent=self.top_level):
            self.data_handler.backup_data()
        self.top_level.focus_set()


class BackgroundSection:
    _image_path = os.path.join(os.getcwd(), "Core", "User Added Images")
    _labels = ["Change Background", "Add Image"]
    _font = ("Arial", 14)
    _pady = 15
    _padx = 7
    __slots__ = "class_name", "parent", "data_handler", "canvas", "top_level", "background_images", "background", \
                "main_frame"

    def __init__(self, parent_frame, data_handler, canvas, top_level, **kwargs):
        self.class_name = kwargs['class_']
        self.parent = parent_frame
        self.data_handler = data_handler
        self.canvas = canvas
        self.top_level = top_level
        self.background_images = [k for k in self.canvas.image_loc.keys()]
        self.background = None

        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(side='top', expand=True, fill='both')

        self.create_ui()

    def create_ui(self):
        combo_boxes = {"background": self.background_images}
        vs_frame = VerticalScrolledFrame(self.main_frame, scroll_lock=True)
        vs_frame.pack(side='top', fill='both', expand=True, pady=10, anchor='center')

        utils.create_labels_grid(vs_frame.interior, self._labels, self._font, "R.TLabel", self._pady, self._padx + 20)

        returned_values, last_index = utils.create_dynamic_combo(vs_frame.interior, combo_boxes, DEFAULT_FONT,
                                                                 "R.TCombobox", "readonly", self._pady,
                                                                 self._padx, offset=20)
        for key, combo in returned_values.items():
            if key == "background":
                self.background = combo

        self.background.bind("<<ComboboxSelected>>", lambda event=None: self.change_background())
        self.background.bind("<ButtonPress-3>", lambda event=None: self.pop_up_menu(event))
        self.set_background_combobox()

        ttk.Button(vs_frame.interior, text="Add Image", style="Accent.TButton", width=27,
                   command=lambda: self.add_background_view()).grid(column=1, row=last_index, pady=self._pady,
                                                                    padx=self._padx)

    def update_background_combobox(self):
        self.background['values'] = [k for k in self.canvas.image_loc.keys()]

    def delete_background(self):
        if tk.messagebox.askyesno("Deleting Image", "Are you sure you want to remove this image?",
                                  parent=self.top_level):
            image_path_to_delete = self.canvas.image_loc[self.background.get()]
            os.remove(image_path_to_delete)
            del self.canvas.image_loc[self.background.get()]
            self.canvas.save_image_paths()
            self.canvas.reload_image()
            self.update_background_combobox()
            self.set_background_combobox()

    def set_background_combobox(self):
        for index, i_d in enumerate(self.background['values']):
            if i_d == self.canvas.image_name:
                self.background.current(index)

    def change_background(self):
        new_image = self.canvas.image_loc[self.background.get()]
        self.canvas.change_background(new_image)
        self.background.selection_clear()

    def add_background_view(self):
        try:
            filepath = tk.filedialog.askopenfilename(filetypes=[("jpeg", ".jpeg"), ("png", ".png"), ("jpg", ".jpg")],
                                                     parent=self.top_level)
            if filepath == '':
                tk.messagebox.showinfo("No File", "Please select a file to open.", parent=self.top_level)
            else:
                top_window, entry = utils.create_pop_up("Name the Image", self.top_level, self.data_handler.entry_limit)
                ttk.Button(top_window, text="Save Image", style="Accent.TButton", width=24,
                           command=lambda: self.save_new_image(filepath, entry.get(), top_window)).pack(side='top',
                                                                                                        padx=4,
                                                                                                        pady=4)
                entry.bind("<Return>", lambda event=None: self.save_new_image(filepath, entry.get(), top_window))
                entry.focus_set()
        except FileNotFoundError:
            tk.messagebox.showinfo("No File", "Please select a file to open.", parent=self.top_level)
            self.top_level.focus_set()

    def save_new_image(self, filepath: str, image_name: str, top_window: tk.Toplevel):
        # Check if image name matches one of the default images
        if image_name in BACKGROUND_IMAGES.keys():
            tk.messagebox.showinfo("Invalid Name", "Image can not be save as one of the default image names.",
                                   parent=self.top_level)
            top_window.focus_set()
            return
        # Check if image name matches one that's already loaded.
        if image_name in self.canvas.image_loc.keys():
            tk.messagebox.showinfo("Invalid Name", "That name already exists.", parent=self.top_level)
            top_window.focus_set()
            return

        self.save_image(filepath, image_name)

        self.update_background_combobox()
        top_window.destroy()
        self.top_level.lift()

    def save_image(self, filepath: str, image_name: str) -> None:
        utils.check_folder_and_create(self._image_path)
        image = Image.open(filepath)
        file_extension = os.path.splitext(filepath)
        new_image_path = os.path.join(self._image_path, (image_name + file_extension[1]))
        image.save(new_image_path)
        self.canvas.image_loc.update({image_name: new_image_path})

    def pop_up_menu(self, event):
        if self.background.get() not in BACKGROUND_IMAGES.keys():
            menu = tk.Menu(self.top_level, tearoff=0)
            menu.add_command(label="Delete", command=self.delete_background)
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
