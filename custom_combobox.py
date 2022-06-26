try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk

"""
A Tkinter widget that features autocompletion.

Created by Mitja Martini on 2008-11-29.
Updated by Russell Adams, 2011/01/24 to support Python 3 and Combobox.
Updated by Dominic Kexel to use Tkinter and ttk instead of tkinter and tkinter.ttk
Licensed same as original (not specified?), or public domain, whichever is less restrictive.
"""

__version__ = "1.1"


class AutocompleteCombobox(ttk.Combobox):

    def __init__(self, root, items, *args, **kwargs):
        ttk.Combobox.__init__(self, root, *args, **kwargs)

        self._hits = []
        self._hit_index = 0
        self.position = 0
        self._completion_list = sorted(items, key=str.lower)  # Work with a sorted list
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list

    def autocomplete(self, delta=0):
        """Autocomplete the Combobox."""
        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())

        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):
                _hits.append(element)

        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits

        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)

        if self._hits:
            self.delete(0, tk.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def set_combobox(self):
        self.icursor(tk.END)
        self.selection_clear()
        self.event_generate("<<FontChange>>")

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        if event.keysym == "Return":
            self.position = self.index(tk.END)
            self.set_combobox()
        if len(event.keysym) == 1:
            self.autocomplete()
