try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk, messagebox


class TreeView(ttk.Treeview):
    def __init__(self, top_window, data_handler, **kwargs):
        ttk.Treeview.__init__(self, top_window, **kwargs)
        self.data_handler = data_handler
        self.parents = None

    def add_elements(self, category: str, elements: list):
        cat = ''
        temp = []
        if self.parents is not None:
            for i in self.parents:
                if self.item(i)['text'] == category:
                    cat = i

            # Adds a new category with the elements to that category
            if cat == '':
                cat = self.insert('', len(self.parents), text=category)
                self.parents.append(cat)
                for ind, ele in enumerate(elements):
                    temp.append(self.insert(cat, ind, text=ele))
            else:
                # Checks the existing category elements for repeats
                texts = [self.item(c)['text'] for c in self.get_children(cat)]
                for index, e in enumerate(elements):
                    if e not in texts:
                        temp.append(self.insert(cat, index, text=e))
        else:
            # If there's no categories created
            self.parents = []
            cat = self.insert('', 0, text=category)
            self.parents.append(cat)
            for ind, ele in enumerate(elements):
                temp.append(self.insert(cat, ind, text=ele))

    def add_all_elements(self, data: dict):
        if self.parents is not None:
            for i in self.parents:
                self.delete(i)
        self.parents = []
        for index, key in enumerate(data.keys()):
            cat = self.insert('', index, text=key)
            self.parents.append(cat)
            for ind, value in enumerate(data[key]):
                self.insert(cat, ind, text=value)

    def remove_elements(self):
        selected = list(self.selection())
        to_be_removed = []
        for i in selected:
            if i in self.parents:
                for index, child in enumerate(self.parents):
                    if i == child:
                        to_be_removed.append(index)
            if self.exists(i):
                self.delete(i)

        if to_be_removed:
            for c in sorted(to_be_removed, reverse=True):
                self.parents.pop(c)
            if len(self.parents) == 0:
                self.parents = None

    def remove_all_elements(self):
        if self.parents is not None:
            for i in self.parents:
                self.delete(i)
        self.parents = None

    def get_all_elements(self) -> dict:
        all_data = {}
        if self.parents is not None:
            for cat in self.parents:
                temp = self.get_children(cat)
                texts = []
                for i in temp:
                    texts.append(self.item(i)['text'])
                all_data.update({self.item(cat)['text']: texts})
            return all_data
