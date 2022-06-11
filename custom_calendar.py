try:
    import Tkinter
    import tkFont
except ImportError:  # Python 3
    import tkinter as Tkinter
    import tkinter.font as tkFont
    from tkinter import ttk

import calendar


class Calendar(ttk.Frame):
    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta
    months = {"01": "Jan",
              "02": "Feb",
              "03": "Mar",
              "04": "Apr",
              "05": "May",
              "06": "June",
              "07": "July",
              "08": "Aug",
              "09": "Sept",
              "10": "Oct",
              "11": "Nov",
              "12": "Dec"}

    def __init__(self, master=None, **kw):
        """
        WIDGET-SPECIFIC OPTIONS
            locale, firstweekday, year, month, selectbackground,
            selectforeground, font
        """
        fwday = kw.pop('firstweekday', calendar.MONDAY)
        year = kw.pop('year', self.datetime.now().year)
        month = kw.pop('month', self.datetime.now().month)
        locale = kw.pop('locale', None)
        sel_bg = kw.pop('selectbackground', '#007fff')
        sel_fg = kw.pop('selectforeground', '#ffffff')

        self.font = kw.pop('font', ("Arial", 10))

        self._date = self.datetime(year, month, 1)

        self._selection = None

        ttk.Frame.__init__(self, master, **kw)

        if locale is None:
            self._cal = calendar.TextCalendar(fwday)
        else:
            self._cal = calendar.LocaleTextCalendar(fwday, locale)

        self._setup_styles()
        self._place_widgets()
        self._config_calendar()

        self._setup_selection(sel_bg, sel_fg)

        self._items = [self._calendar.insert('', 'end', values=[])
                       for _ in range(6)]
        self._build_calendar()

    def _setup_styles(self):
        style = ttk.Style(self.master)
        button_left = ([('Button.focus', {'children': [('Button.leftarrow', None)]})])
        button_right = ([('Button.focus', {'children': [('Button.rightarrow', None)]})])

        style.layout('L.TButton', button_left)
        style.layout('R.TButton', button_right)

    def _place_widgets(self):
        header = ttk.Frame(self, relief="ridge", borderwidth=2)

        left = ttk.Button(header, style='L.TButton', command=self._prev_month)
        right = ttk.Button(header, style='R.TButton', command=self._next_month)
        self._header = ttk.Label(header, width=15, anchor='center')

        self._calendar = ttk.Treeview(self, show='', selectmode='none', height=1)

        header.pack(side='top', pady=4, fill='x')

        left.grid(row=0, column=0, padx=14)
        self._header.grid(row=0, column=1, padx=24)
        right.grid(row=0, column=2, padx=12)

        self._calendar.pack(expand=1, fill='both', side='bottom')

    def _config_calendar(self):
        cols = self._cal.formatweekheader(4).split()
        self._calendar['columns'] = cols
        self._calendar.tag_configure('header', background='#848689')
        self._calendar.insert('', 'end', values=cols, tag='header')

        for col in cols:
            self._calendar.column(col, width=7, minwidth=7,
                                  anchor='center')

    def _setup_selection(self, sel_bg, sel_fg):
        self._canvas = Tkinter.Canvas(self._calendar,
                                      background=sel_bg, borderwidth=0, highlightthickness=0)
        self._canvas.text = self._canvas.create_text(0, 0, fill=sel_fg, anchor='w', font=self.font)

        self._canvas.bind('<ButtonPress-1>', lambda event: self._canvas.place_forget())
        self._calendar.bind('<Configure>', lambda event: self._canvas.place_forget())
        self._calendar.bind('<ButtonPress-1>', self._mouse_click)

    def _build_calendar(self):
        year, month = self._date.year, self._date.month

        header = self._cal.formatmonthname(year, month, 0)
        self._header['text'] = header.title()

        cal = self._cal.monthdayscalendar(year, month)
        for index, item in enumerate(self._items):
            week = cal[index] if index < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            self._calendar.item(item, values=fmt_week)

    def _show_selection(self, text, bbox):
        """Creates a canvas overtop the treeview with the selected text."""
        x, y, width, height = bbox

        self._canvas.configure(width=width, height=height)
        self._canvas.coords(self._canvas.text, width - 24, height / 2)
        self._canvas.itemconfigure(self._canvas.text, text=text)
        self._canvas.place(in_=self._calendar, x=x, y=y)

    def _mouse_click(self, evt):
        """Mouse click on the calendar."""
        x, y, widget = evt.x, evt.y, evt.widget
        item = widget.identify_row(y)
        column = widget.identify_column(x)

        if not column or item not in self._items:
            return

        item_values = widget.item(item)['values']
        if not len(item_values):
            return

        text = item_values[int(column[1]) - 1]
        if not text:
            return

        bbox = widget.bbox(item, column)
        if not bbox:
            return

        text = '%02d' % text
        self._selection = (text, item, column)
        self._show_selection(text, bbox)

    def _prev_month(self):
        """Go back to the previous month."""
        self._canvas.place_forget()

        self._date = self._date - self.timedelta(days=1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar()

    def _next_month(self):
        """Go to the next month."""
        self._canvas.place_forget()

        year, month = self._date.year, self._date.month
        self._date = self._date + self.timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar()

    def selection(self):
        """Return year, month, day in a tuple."""
        if not self._selection:
            return None

        year, month = self._date.year, self._date.month
        return self.datetime(year, month, int(self._selection[0]))

    def format_date(self, date: str) -> str:
        """Formats datetime object to month(Abbreviated), day, year in form of string and returns value."""
        date = str(date)  # Convert from datetime object to string
        month = self.months[date[5:7]]
        day = date[8:10]
        year = date[:4]
        return month + " " + day + ", " + year
