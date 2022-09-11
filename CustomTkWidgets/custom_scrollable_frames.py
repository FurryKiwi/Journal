from tkinter import ttk
import tkinter as tk
import sys


class VerticalScrolledFrame(ttk.Frame):
    __slots__ = "scroll_lock", "canvas", "interior", "interior_id"

    def __init__(self, parent, scroll_lock=False, *args, **kw):
        self.scroll_lock = scroll_lock

        if sys.platform == "linux":
            import functools
            fp = functools.partial

            def _on_mousewheel(event, scroll):
                if not self.scroll_lock:
                    self.canvas.yview_scroll(int(scroll), "units")

            def _bind_to_mousewheel(event):
                self.canvas.bind_all("<Button-4>", fp(_on_mousewheel, scroll=-1))
                self.canvas.bind_all("<Button-5>", fp(_on_mousewheel, scroll=1))

            def _unbind_from_mousewheel(event):
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")

        elif sys.platform == "win32":

            def _on_mousewheel(event):
                if not self.scroll_lock:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            def _bind_to_mousewheel(event):
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

            def _unbind_from_mousewheel(event):
                self.canvas.unbind_all("<MouseWheel>")

        ttk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                                yscrollcommand=vscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())


if __name__ == "__main__":
    import Scripts.utils as utils

    _master = {'Button Foreground': 'Accent.TButton', 'Export/Import Foreground': 'R.Treeview',
               'Tabs Foreground': 'TNotebook.Tab', 'Selector Boxes': 'R.TCombobox', 'Header Labels': 'H.TLabel',
               'Regular Labels': 'R.TLabel', 'Settings Headers': 'S.TLabel', 'Settings Frames': 'SF.TLabel',
               'Entry Foreground': 'R.TEntry', 'Document Text Foreground': 'Help_Text',
               'Listbox Foreground': 'Listbox',
               'Menu Foreground': 'Menu', 'Pin Text Color': 'Pin_Color'}

    # Set Up root of app
    root = tk.Tk()
    root.geometry("600x500+50+50")
    root.title("VerticalScrolledFrame Sample")

    # Create a frame to put the VerticalScrolledFrame inside
    holder_frame = ttk.Frame(root)
    holder_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE, anchor='center')

    # Create the VerticalScrolledFrame
    vs_frame = VerticalScrolledFrame(holder_frame)
    vs_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.TRUE, anchor='center')
    import os

    # _colors_dir_path = os.path.join(os.getcwd())
    # _colors_txt_path = os.path.join(_colors_dir_path, "colors.txt")

    labels = [key for key in _master.keys()]
    button_values = ['custom', 'red', 'blue', 'green', 'orange', 'white', 'grey', 'black', 'purple', 'brown',
                              'yellow', 'violet']

    utils.create_labels_grid(vs_frame.interior, labels, ("Arial", 14), "R.TLabel", 15, 7)
    utils.create_combo_grid(vs_frame.interior, labels, "foreground", button_values, font=("Arial", 12),
                            style="R.TCombobox", state="readonly", pad_y=15, pad_x=7)

    # Run mainloop to start app
    root.mainloop()
