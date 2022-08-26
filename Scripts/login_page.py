# Copyright © 2022 FurryKiwi <normalusage2@gmail.com>

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

from Scripts.settings import *
import Scripts.utils as utils


class LoginPage(ttk.Notebook):
    _tcl_path = TCL_PATH

    def __init__(self, journal, login_handler, *args, **kwargs):
        self.root = tk.Tk()
        self.root.tk.call("source", self._tcl_path)
        self.root.tk.call("set_theme", "dark")

        self.journal = journal
        self.login_handler = login_handler

        utils.set_window(self.root, 315, 315, "Login Page")

        kwargs['style'] = "TNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self.style = ttk.Style()
        self.set_style()

        self.signup_user = None
        self.signup_password = None

        self.signup_btn = None
        self.login_page_btn = None

        self.user_login = None
        self.password_login = None

        self.auto_sign = None

        self.reset_users_combo = None
        self.reset_entry = None
        self.reset_btn = None
        self.reset_user_entry = None
        self.delete_btn = None

        self.change_user = False

        self.create_login_page()
        self.create_signup_page()
        self.create_reset_page()

        self.pack(expand=True, fill="both")

    def create_login_page(self) -> None:
        """Creates the login page tab view and all it's elements."""
        login_frame = tk.Frame()

        user_label = tk.Label(login_frame, text="Username:", font=DEFAULT_FONT_BOLD)
        user_label.pack(pady=8)

        self.user_login = ttk.Combobox(login_frame, values=self.login_handler.get_users(),
                                       state="readonly", width=25, font=DEFAULT_FONT)
        self.user_login.pack()
        # Gets from the database if there was a last signed-in user and sets the combobox
        if self.login_handler.last_signed_in:
            self.set_username_combobox(self.login_handler.last_signed_in)
        else:
            # Sets it to the first one in the list otherwise
            self.user_login.current(0)

        pass_label = tk.Label(login_frame, text="Password:", font=DEFAULT_FONT_BOLD)
        pass_label.pack(pady=8)

        self.password_login = tk.Entry(login_frame, validate="key",
                                       validatecommand=(self.root.register(
                                           lambda event: utils.validate_entry
                                           (event, self.login_handler.password_limit)), "%P"), width=25,
                                       font=DEFAULT_FONT, background=ENTRY_COLOR, show="*")
        self.password_login.pack()

        self.auto_sign = tk.IntVar()

        ttk.Checkbutton(login_frame, text="Stay Signed In", takefocus=0, variable=self.auto_sign).pack(pady=8)

        # Sets the auto sign-in check button from the database
        if self.login_handler.signed_in_btn:
            self.auto_sign.set(self.login_handler.signed_in_btn)
            user, pw = self.login_handler.get_credentials(self.login_handler.last_signed_in)
            self.password_login.insert(0, user)

        self.login_page_btn = ttk.Button(login_frame, style="Accent.TButton", text="Login", width=24,
                                         command=lambda: self.login(self.user_login.get(),
                                                                    self.password_login.get()))
        self.login_page_btn.pack(pady=8)

        self.password_login.focus_set()

        self.add(login_frame, text="Login")

    def create_signup_page(self) -> None:
        """Creates the signup page tab view with all it's elements."""
        signup_frame = tk.Frame()

        user_label = tk.Label(signup_frame, text="Create Username:", font=DEFAULT_FONT_BOLD)
        user_label.pack(pady=8)

        self.signup_user = tk.Entry(signup_frame, validate="key",
                                    validatecommand=(self.root.register(
                                        lambda event: utils.validate_entry(event, self.login_handler.entry_limit)),
                                                     "%P"),
                                    width=25,
                                    font=DEFAULT_FONT, background=ENTRY_COLOR)
        self.signup_user.pack()

        pass_label = tk.Label(signup_frame, text="Create Password:", font=DEFAULT_FONT_BOLD)
        pass_label.pack(pady=8)

        self.signup_password = tk.Entry(signup_frame, validate="key",
                                        validatecommand=(self.root.register(
                                            lambda event: utils.validate_entry(event, self.login_handler.entry_limit)),
                                                         "%P"), width=25,
                                        font=DEFAULT_FONT, background=ENTRY_COLOR, show="*")
        self.signup_password.pack()

        self.signup_btn = ttk.Button(signup_frame, style="Accent.TButton", text="Create", width=24,
                                     command=lambda: self.sign_up(self.signup_user.get(), self.signup_password.get()))
        self.signup_btn.pack(pady=16)

        self.add(signup_frame, text="Sign Up")

    def create_reset_page(self) -> None:
        """Creates the reset page view with all it's elements."""
        reset_page = tk.Frame()

        user_label = tk.Label(reset_page, text="Existing User:", font=DEFAULT_FONT_BOLD)
        user_label.pack(pady=8)

        self.reset_users_combo = ttk.Combobox(reset_page, values=self.login_handler.get_users(),
                                              state="readonly", width=25, font=DEFAULT_FONT)
        self.reset_users_combo.pack()

        tk.Label(reset_page, text="Enter new username:", font=DEFAULT_FONT_BOLD).pack(pady=8)

        self.reset_user_entry = tk.Entry(reset_page, validate="key",
                                         validatecommand=(self.root.register(
                                             lambda event: utils.validate_entry(event, self.login_handler.entry_limit)),
                                                          "%P"), width=25,
                                         font=DEFAULT_FONT, background=ENTRY_COLOR)
        self.reset_user_entry.pack()

        tk.Label(reset_page, text="Enter new password:", font=DEFAULT_FONT_BOLD).pack(pady=8)

        self.reset_entry = tk.Entry(reset_page, validate="key",
                                    validatecommand=(self.root.register(
                                        lambda event: utils.validate_entry(event, self.login_handler.entry_limit)),
                                                     "%P"), width=25,
                                    font=DEFAULT_FONT, background=ENTRY_COLOR)
        self.reset_entry.pack(pady=8)

        self.reset_btn = ttk.Button(reset_page, style="Accent.TButton", text="Reset", width=10,
                                    command=lambda: self.reset_password(self.reset_users_combo.get(),
                                                                        self.reset_user_entry.get(),
                                                                        self.reset_entry.get()))
        self.reset_btn.pack(side="left", pady=8, padx=42)

        self.delete_btn = ttk.Button(reset_page, style="Accent.TButton", text="Delete", width=10,
                                     command=lambda: self.delete_user(self.reset_users_combo.get()))
        self.delete_btn.pack(side="left", pady=8)

        self.add(reset_page, text="Reset")

    def changed_users(self) -> None:
        """Clears password and user login entry/combobox."""
        self.password_login.delete(0, len(self.password_login.get()))
        self.user_login.selection_clear()
        self.auto_sign.set(0)
        self.change_user = True

    def delete_user(self, user: str) -> None:
        """Calls the data_handler method for deleting users and notifies user of progress."""
        if tk.messagebox.askyesno("Deletion", "Are you sure you want to delete user?"):
            deleted = self.login_handler.delete_user(user)
            if deleted:
                self.select(0)
                self.reset_combobox()
                self.delete_entries()
                self.set_username_combobox()
                self.auto_sign.set(0)
            else:
                tk.messagebox.showerror("Error", "Unable to delete user.")

    def delete_entries(self) -> None:
        """Deletes all the entry boxes on the login page."""
        self.password_login.delete(0, len(self.password_login.get()))
        self.reset_entry.delete(0, len(self.reset_entry.get()))
        self.reset_user_entry.delete(0, len(self.reset_user_entry.get()))
        self.signup_user.delete(0, len(self.signup_user.get()))
        self.signup_password.delete(0, len(self.signup_password.get()))

    def event_handling(self) -> None:
        """Handles all the events."""
        self.login_page_btn.bind("<Return>", lambda event=None: self.login_page_btn.invoke())
        self.signup_btn.bind("<Return>", lambda event=None: self.signup_btn.invoke())

        self.user_login.bind("<<ComboboxSelected>>", lambda event=None: self.changed_users())

        self.reset_entry.bind("<Return>", lambda event=None: self.reset_btn.invoke())

        self.signup_password.bind("<Return>", lambda event=None: self.signup_btn.invoke())
        self.password_login.bind("<Return>", lambda event=None: self.login_page_btn.invoke())

    def login(self, user: str, pw: str) -> None:
        """Calls database validation of user and password, if true,
        Closes login window and calls journal run method to start main application."""
        if self.login_handler.signed_in_btn and self.change_user is False:
            check = self.login_handler.bypass(user, self.auto_sign.get())
            if check:
                self.root.destroy()
                self.journal.run()
                return
        logged_in = self.login_handler.validate_login(user, pw, self.auto_sign.get())
        if logged_in:
            self.root.destroy()
            self.journal.run()
            return
        else:
            self.password_login.delete(0, len(self.password_login.get()))
            self.password_login.focus_set()
            tk.messagebox.showerror(title="Incorrect Credentials", message="Invalid user or password")

    def reset_combobox(self) -> None:
        """Resets the combo boxes values by getting the data from the data_handler."""
        self.user_login.config(values=self.login_handler.get_users())
        self.reset_users_combo.config(values=self.login_handler.get_users())

    def reset_password(self, user: str, new_user: str, new_pw: str) -> None:
        """Calls the reset password method from the data_handler and notifies user of progress."""
        if tk.messagebox.askyesno("Reset User/Password", "Are you sure?"):
            # If user doesn't specify a new user_name, it uses the old username
            if new_user == '':
                new_user = user
            if new_pw == '':
                if tk.messagebox.askyesno("No Password Set", "Are you sure you don't want a password?"):
                    new_pw = new_pw
                else:
                    return
            check = self.login_handler.reset_password(user, new_user, new_pw)
            if check:
                self.delete_entries()
                self.auto_sign.set(0)
                self.reset_combobox()
                self.set_username_combobox(new_user)
                self.reset_users_combo.set('')
                self.select(0)
                tk.messagebox.showinfo("User/Password Changed", "Password/Username changed.")
                self.password_login.focus_set()
            else:
                tk.messagebox.showerror("Password Error", "Password/Username was not changed.")

    def sign_up(self, user: str, pw: str) -> None:
        """Calls database validation if user already exists returns false,
        Refreshes login tab and sets user to the newly created user."""
        sign_up = self.login_handler.create_new_user(user, pw)
        if sign_up:
            self.select(0)
            self.reset_combobox()
            self.set_username_combobox(user)
            self.delete_entries()
            self.auto_sign.set(0)
            self.password_login.focus_set()
        else:
            tk.messagebox.showinfo("User already exists", "Pick a different username")
            self.signup_user.focus_set()

    def set_username_combobox(self, user: str = None) -> None:
        """Sets the username combobox with the last signed-in user otherwise the default."""
        temp_list = self.user_login['values']
        if temp_list and user:
            for index, i_d in enumerate(temp_list):
                if i_d == user:
                    self.user_login.current(index)
        elif temp_list and not user:
            self.user_login.current(0)
            self.reset_users_combo.set("")
        else:
            self.user_login.set("SignUp")
            self.reset_users_combo.set("SignUp")

    def set_style(self) -> None:
        """Configuration for the theme/style settings for the notebook and tabs."""
        self.style.theme_settings("azure-dark", {
            "TNotebook": {"configure": {"font": ("Arial", 18, "bold"), "padding": [0, 2]}},
            "TNotebook.Tab": {
                "configure": {"padding": [0, 0], "font": ("Arial", 19, "bold")},
                "map": {"background": [("selected", BUTTON_BG)],
                        "expand": [("selected", [0, 0, 0, 0])]}}})

    def run(self) -> None:
        self.password_login.focus_force()
        self.event_handling()
        self.root.mainloop()
