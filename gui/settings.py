"""Settings window"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from utils.storage import StorageManager
from utils.auth import AuthManager
from models.models import User


class SettingsWindow:
    """Settings and Configuration UI"""

    def __init__(self, parent, storage: StorageManager, auth: AuthManager, user: User):
        self.parent = parent
        self.storage = storage
        self.auth = auth
        self.user = user
        
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("900x700")
        self.window.minsize(800, 600)
        self.window.configure(bg='#f5f5f5')
        
        self.setup_ui()

    def setup_ui(self):
        """Create settings UI"""
        # Notebook
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # General settings tab
        general_frame = ttk.Frame(notebook, padding="15")
        notebook.add(general_frame, text="General")

        ttk.Label(general_frame, text="Current GST Rate (%):").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.gst_entry = ttk.Entry(general_frame, width=20)
        self.gst_entry.grid(row=0, column=1, pady=10)
        self.gst_entry.insert(0, "18")

        ttk.Label(general_frame, text="Shop Name:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.shop_name_entry = ttk.Entry(general_frame, width=30)
        self.shop_name_entry.grid(row=1, column=1, pady=10)
        self.shop_name_entry.insert(0, "Smart Retail Billing")

        ttk.Label(general_frame, text="Low Stock Alert Level:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.low_stock_entry = ttk.Entry(general_frame, width=20)
        self.low_stock_entry.grid(row=2, column=1, pady=10)
        self.low_stock_entry.insert(0, "10")

        ttk.Button(general_frame, text="Save Settings", command=self.save_general_settings).grid(row=3, column=0, columnspan=2, pady=20)

        # Account tab
        account_frame = ttk.Frame(notebook, padding="15")
        notebook.add(account_frame, text="Account")

        ttk.Label(account_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=10)
        ttk.Label(account_frame, text=self.user.username, font=("Arial", 10)).grid(row=0, column=1, sticky=tk.W, pady=10)

        ttk.Label(account_frame, text="Role:").grid(row=1, column=0, sticky=tk.W, pady=10)
        ttk.Label(account_frame, text=self.user.role, font=("Arial", 10)).grid(row=1, column=1, sticky=tk.W, pady=10)

        ttk.Label(account_frame, text="Current Password:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.current_pass = ttk.Entry(account_frame, width=30, show="*")
        self.current_pass.grid(row=2, column=1, pady=10)

        ttk.Label(account_frame, text="New Password:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.new_pass = ttk.Entry(account_frame, width=30, show="*")
        self.new_pass.grid(row=3, column=1, pady=10)

        ttk.Label(account_frame, text="Confirm Password:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.confirm_pass = ttk.Entry(account_frame, width=30, show="*")
        self.confirm_pass.grid(row=4, column=1, pady=10)

        ttk.Button(account_frame, text="Change Password", command=self.change_password).grid(row=5, column=0, columnspan=2, pady=20)

        # User Management tab (only for admin)
        if self.user.role == "admin":
            users_frame = ttk.Frame(notebook, padding="15")
            notebook.add(users_frame, text="User Management")

            ttk.Label(users_frame, text="Users:").pack(anchor=tk.W, pady=10)

            # Users list
            tree_frame = ttk.Frame(users_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            self.users_tree = ttk.Treeview(tree_frame, columns=("Role", "Created"), height=10)
            self.users_tree.column("#0", width=150)
            self.users_tree.column("Role", width=100)
            self.users_tree.column("Created", width=200)

            self.users_tree.heading("#0", text="Username")
            self.users_tree.heading("Role", text="Role")
            self.users_tree.heading("Created", text="Created At")

            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
            self.users_tree.configure(yscroll=scrollbar.set)
            self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.refresh_users_list()

            button_frame = ttk.Frame(users_frame)
            button_frame.pack(fill=tk.X, pady=10)

            ttk.Button(button_frame, text="Add User", command=self.add_user).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT, padx=5)

        # Backup tab
        backup_frame = ttk.Frame(notebook, padding="15")
        notebook.add(backup_frame, text="Backup & Restore")

        ttk.Label(backup_frame, text="Data Management", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=10)

        ttk.Button(backup_frame, text="Create Backup", command=self.create_backup, width=30).pack(pady=5, fill=tk.X)
        ttk.Button(backup_frame, text="Restore from Backup", command=self.restore_backup, width=30).pack(pady=5, fill=tk.X)

        ttk.Label(backup_frame, text="Danger Zone", font=("Arial", 11, "bold"), foreground="red").pack(anchor=tk.W, pady=20)
        ttk.Button(backup_frame, text="Clear All Data (This cannot be undone)", command=self.clear_all_data, width=30).pack(pady=5, fill=tk.X)

    def save_general_settings(self):
        """Save general settings"""
        messagebox.showinfo("Success", "Settings saved successfully")

    def change_password(self):
        """Change password"""
        current = self.current_pass.get()
        new = self.new_pass.get()
        confirm = self.confirm_pass.get()

        if not current or not new:
            messagebox.showerror("Error", "Please fill all fields")
            return

        if new != confirm:
            messagebox.showerror("Error", "New passwords don't match")
            return

        success, msg = self.auth.change_password(self.user.user_id, current, new)
        if success:
            messagebox.showinfo("Success", msg)
            self.current_pass.delete(0, tk.END)
            self.new_pass.delete(0, tk.END)
            self.confirm_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)

    def refresh_users_list(self):
        """Refresh users list"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        users = self.storage.get_all_users()
        for user in users:
            self.users_tree.insert("", tk.END, text=user.username, values=(
                user.role,
                user.created_at[:10]
            ))

    def add_user(self):
        """Add new user dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add User")
        dialog.geometry("300x200")

        frame = ttk.Frame(dialog, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Username:").pack(anchor=tk.W, pady=5)
        username_entry = ttk.Entry(frame, width=30)
        username_entry.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text="Password:").pack(anchor=tk.W, pady=5)
        password_entry = ttk.Entry(frame, width=30, show="*")
        password_entry.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text="Role:").pack(anchor=tk.W, pady=5)
        role_var = tk.StringVar(value="staff")
        role_combo = ttk.Combobox(frame, textvariable=role_var, values=["admin", "staff"], state="readonly", width=28)
        role_combo.pack(fill=tk.X, pady=5)

        def create():
            username = username_entry.get().strip()
            password = password_entry.get()
            role = role_var.get()

            if not username or not password:
                messagebox.showerror("Error", "Username and password required")
                return

            success, msg = self.auth.create_user(username, password, role)
            if success:
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.refresh_users_list()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(frame, text="Create", command=create).pack(pady=20)

    def delete_user(self):
        """Delete selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return

        username = self.users_tree.item(selection[0], "text")
        if username == self.user.username:
            messagebox.showerror("Error", "Cannot delete your own account")
            return

        if messagebox.askyesno("Confirm", f"Delete user '{username}'?"):
            users = self.storage.get_all_users()
            for u in users:
                if u.username == username:
                    u.is_active = False
                    self.storage.update_user(u)
                    self.refresh_users_list()
                    messagebox.showinfo("Success", "User deleted")
                    break

    def create_backup(self):
        """Create data backup"""
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if self.storage.backup_data(backup_name):
            messagebox.showinfo("Success", f"Backup created: {backup_name}")
        else:
            messagebox.showerror("Error", "Backup failed")

    def restore_backup(self):
        """Restore from backup"""
        import os
        backup_dir = os.path.join(self.storage.base_path, "backups")
        if not os.path.exists(backup_dir):
            messagebox.showerror("Error", "No backups found")
            return

        backups = os.listdir(backup_dir)
        if not backups:
            messagebox.showerror("Error", "No backups found")
            return

        backup_name = tk.simpledialog.askstring("Restore Backup", f"Available backups:\n{chr(10).join(backups[:5])}\n\nEnter backup name:")
        if backup_name:
            if self.storage.restore_data(backup_name):
                messagebox.showinfo("Success", "Data restored successfully")
            else:
                messagebox.showerror("Error", "Restore failed")

    def clear_all_data(self):
        """Clear all data"""
        if messagebox.askyesno("Confirm", "This will delete all data. Continue?"):
            if messagebox.askyesno("Confirm Again", "Are you absolutely sure? This cannot be undone!"):
                import os
                import shutil
                for file in os.listdir(self.storage.base_path):
                    if file != "backups":
                        file_path = os.path.join(self.storage.base_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                self.storage._initialize_files()
                messagebox.showinfo("Success", "All data cleared")
