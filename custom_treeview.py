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
        self.parents = []
        self.children_of_parents = []
        self.item_selected = None
        self.exempt = []
        self.bind('<ButtonRelease-1>', lambda event: self.selected_item(event))

    def add_default_items(self, data: dict, importing: bool = False, exception: bool = False):
        """Adds default items into the treeview, with options of importing the data at which the existing elements in
        the tree view won't be destroyed. If exception is True, the given dict will be added to the exempt list at which
        they can't be removed."""
        self.add_all_elements(data, importing, exception)

    def selected_item(self, event):
        """Sets the selected item from the tree view with the text given to that element."""
        item = self.identify('item', event.x, event.y)
        if len(item) == 0:
            self.selection_remove(self.focus())
            self.item_selected = None
        else:
            self.item_selected = self.item(item)['text']

    def add_elements(self, category: str, elements: list):
        """Adds items to the treeview with the category being the parent and elements being the children."""
        cat = ''
        if self.parents is not None:
            for i in self.parents:
                if self.exists(i):
                    if self.item(i)['text'] == category:
                        cat = i

            # Adds a new category with the elements to that category
            if cat == '':
                cat = self.insert('', len(self.parents), text=category)
                self.parents.append(cat)
                for ind, ele in enumerate(elements):
                    self.children_of_parents.append(self.insert(cat, ind, text=ele))
            else:
                # Checks the existing category elements for repeats
                texts = [self.item(c)['text'] for c in self.get_children(cat)]
                for index, e in enumerate(elements):
                    if e not in texts:
                        self.children_of_parents.append(self.insert(cat, index, text=e))
        else:
            # If there's no categories created
            self.parents = []
            cat = self.insert('', 0, text=category)
            self.parents.append(cat)
            for ind, ele in enumerate(elements):
                self.children_of_parents.append(self.insert(cat, ind, text=ele))

    def add_all_elements(self, data: dict, importing: bool = False, exception: bool = False):
        """Add a dictionary of elements to the treeview, if specified importing, the treeview won't delete
        all elements and create a new tree view. If specified exception, the data will be added to the exempt list
        at which they can't be removed after."""
        if not importing:
            if self.parents is not None:
                for i in self.parents:
                    if self.exists(i):
                        self.delete(i)
            self.parents = []
        if exception:
            for index, key in enumerate(data.keys()):
                cat = self.insert('', index, text=key)
                self.parents.append(cat)
                self.exempt.append(cat)
                for ind, value in enumerate(data[key]):
                    self.exempt.append(self.insert(cat, ind, text=value))
        else:
            for index, key in enumerate(data.keys()):
                cat = self.insert('', index, text=key)
                self.parents.append(cat)
                for ind, value in enumerate(data[key]):
                    self.children_of_parents.append(self.insert(cat, ind, text=value))

    def remove_elements(self):
        """Removes parents and children from the tree view that are not in the exempt list."""
        selected = list(self.selection())

        remove_parents = []
        remove_children = []
        for i in selected:
            if i in self.exempt:
                return
            if i in self.parents:
                for index, child in enumerate(self.parents):
                    if i == child:
                        remove_parents.append(index)
            if i in self.children_of_parents:
                for index, c in enumerate(self.children_of_parents):
                    if i == c:
                        remove_children.append(index)
            if self.exists(i):
                self.delete(i)

        if remove_parents:
            for c in sorted(remove_parents, reverse=True):
                self.parents.pop(c)
            if len(self.parents) == 0:
                self.parents = []
        if remove_children:
            for c in sorted(remove_children, reverse=True):
                self.children_of_parents.pop(c)
            if len(self.children_of_parents) == 0:
                self.children_of_parents = []

    def remove_all_elements(self):
        """Removes all elements in the tree view that are not in the exempt list."""
        if self.parents is not None:
            remove_parents = []
            for index, parent in enumerate(self.parents):
                if parent not in self.exempt:
                    if self.exists(parent):
                        self.delete(parent)
                        remove_parents.append(index)
            if remove_parents:
                for c in sorted(remove_parents, reverse=True):
                    self.parents.pop(c)

    def get_all_elements(self) -> dict:
        """Returns all the parents and children in the treeview as a dict with their given text."""
        all_data = {}
        if self.parents is not None:
            for cat in self.parents:
                if self.exists(cat):
                    temp = self.get_children(cat)
                    texts = []
                    for i in temp:
                        texts.append(self.item(i)['text'])
                    all_data.update({self.item(cat)['text']: texts})
            return all_data
