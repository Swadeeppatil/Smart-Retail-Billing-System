"""Login window for authentication"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.storage import StorageManager
from utils.auth import AuthManager
from models.models import User


class LoginWindow:
    """Login UI"""

    def __init__(self, root, storage: StorageManager, auth: AuthManager):
        self.root = root
        self.storage = storage
        self.auth = auth
        self.current_user = None
        self.root.title("Smart Retail Billing - Login")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Clear any existing widgets on root
        for widget in self.root.winfo_children():
            widget.destroy()

        self.setup_ui()

    def setup_ui(self):
        """Create login UI"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        # Title
        title_label = ttk.Label(main_frame, text="Smart Retail Billing System",
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        subtitle_label = ttk.Label(main_frame, text="User Login",
                                   font=("Arial", 12))
        subtitle_label.pack(pady=10)
        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=5)
        self.username_entry.focus()
        # Password
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.pack(fill=tk.X, pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        login_btn = ttk.Button(button_frame, text="Login", command=self.login)
        login_btn.pack(side=tk.LEFT, padx=5)
        create_btn = ttk.Button(button_frame, text="Create User", command=self.show_create_user)
        create_btn.pack(side=tk.LEFT, padx=5)
        exit_btn = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        exit_btn.pack(side=tk.RIGHT, padx=5)
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.login())
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=10)

    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return

        user = self.auth.authenticate(username, password)
        if user:
            self.current_user = user
            self.on_login_success(user)
        else:
            self.status_label.config(text="Invalid credentials", foreground="red")
            self.password_entry.delete(0, tk.END)

    def show_create_user(self):
        """Show create user dialog"""
        users = self.storage.get_all_users()
        if users and all(u.role != "admin" for u in users):
            messagebox.showerror("Error", "No admin user found. Cannot create users.")
            return
        create_window = tk.Toplevel(self.root)
        create_window.title("Create User")
        create_window.geometry("300x250")
        frame = ttk.Frame(create_window, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Username:").pack(anchor=tk.W, pady=5)
        username_entry = ttk.Entry(frame, width=25)
        username_entry.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text="Password:").pack(anchor=tk.W, pady=5)
        password_entry = ttk.Entry(frame, width=25, show="*")
        password_entry.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="Name:").pack(anchor=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=25)
        name_entry.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="Role:").pack(anchor=tk.W, pady=5)
        role_var = tk.StringVar(value="staff")
        role_combo = ttk.Combobox(frame, textvariable=role_var, values=["admin", "staff"],
                                  state="readonly", width=23)
        role_combo.pack(fill=tk.X, pady=5)

        def create():
            username = username_entry.get().strip()
            password = password_entry.get()
            name = name_entry.get().strip()
            role = role_var.get()
            if not username or not password:
                messagebox.showerror("Error", "Username and password required")
                return
            success, msg = self.auth.create_user(username, password, role, name)
            if success:
                messagebox.showinfo("Success", msg)
                create_window.destroy()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(frame, text="Create", command=create).pack(pady=20)

    def on_login_success(self, user):
        """Callback on successful login - overridden by MainWindow"""
        pass
