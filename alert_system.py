try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

from settings import *


class AlertSystem:

    def __init__(self, root, data_handler, main_layout):
        self.root = root
        self.data_handler = data_handler
        self.main_layout = main_layout
        self.queue = []
        self.shown = False
        self.after_id = ''

    def show_alert(self) -> None:
        if not self.shown:
            try:
                message, color = self.queue.pop()
                label = tk.Label(self.main_layout.tool_frame, text=message, fg=color, font=DEFAULT_FONT)
                label.pack(side='left', anchor='w', padx=4, pady=4)
                self.shown = True
                self.after_id = self.root.after(2000, lambda: self.clear_canvas(label))
            except IndexError:
                return

    def clear_canvas(self, label):
        label.pack_forget()
        del label
        self.shown = False
        self.show_alert()

    def cancel_after(self):
        self.root.after_cancel(self.after_id)

    def saved_text(self):
        self.queue.append(("Entry has been saved.", "white"))
        self.show_alert()

    def tab_limit(self):
        self.queue.append(("Tab limit has been met.", "red"))
        self.show_alert()

    def data_cleared(self):
        self.queue.append(("Data was cleared.", "white"))
        self.show_alert()

    def auto_backup_started(self):
        self.queue.append(("Auto backup has started.", "white"))
        self.show_alert()

    def auto_backup_stopped(self):
        self.queue.append(("Auto backup has stopped.", "red"))
        self.show_alert()

    def auto_backup_not_started(self):
        self.queue.append(("Auto backup has not been started.", "red"))
        self.show_alert()

    def auto_backup_no_data(self):
        self.queue.append(("Auto backup could not be set with no data.", "red"))
        self.show_alert()

    def backup_failed(self):
        self.queue.append(("No data to backup.", "red"))
        self.show_alert()

    def backup_success(self):
        self.queue.append(("Backup complete.", "white"))
        self.show_alert()

    def restore_success(self):
        self.queue.append(("Restored user's data.", "white"))
        self.show_alert()

    def restore_failed(self):
        self.queue.append(("No data to restore for user.", "red"))
        self.show_alert()

    def category_failed(self):
        self.queue.append(("Could not save category.", "red"))
        self.show_alert()

    def delete_category_failed(self):
        self.queue.append(("Category doesn't exist.", "red"))
        self.show_alert()

    def definition_failed(self):
        self.queue.append(("Could not save definition.", "red"))
        self.show_alert()

    def delete_definition_failed(self):
        self.queue.append(("Definition doesn't exist.", "red"))
        self.show_alert()
