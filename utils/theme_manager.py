"""Theme Manager for Smart Retail Billing System

Provides Dark Mode / Light Mode toggle with smooth theme switching.
"""

import tkinter as tk
from tkinter import ttk


# ── Theme Definitions ────────────────────────────────────────────────────
THEMES = {
    "light": {
        "name": "Light Mode ☀️",
        "bg": "#f5f5f5",
        "fg": "#333333",
        "accent": "#007acc",
        "accent_hover": "#005f99",
        "card_bg": "#ffffff",
        "card_fg": "#333333",
        "border": "#dddddd",
        "success": "#27ae60",
        "danger": "#e74c3c",
        "warning": "#f39c12",
        "disabled_bg": "#cccccc",
        "disabled_fg": "#888888",
        "input_bg": "white",
        "input_fg": "#333333",
        "treeview_bg": "white",
        "treeview_fg": "#333333",
        "treeview_selected": "#007acc",
        "header_bg": "#f5f5f5",
        "header_fg": "#333333",
        "separator": "#cccccc",
    },
    "dark": {
        "name": "Dark Mode 🌙",
        "bg": "#1e1e2e",
        "fg": "#cdd6f4",
        "accent": "#89b4fa",
        "accent_hover": "#74c7ec",
        "card_bg": "#313244",
        "card_fg": "#cdd6f4",
        "border": "#45475a",
        "success": "#a6e3a1",
        "danger": "#f38ba8",
        "warning": "#fab387",
        "disabled_bg": "#45475a",
        "disabled_fg": "#6c7086",
        "input_bg": "#313244",
        "input_fg": "#cdd6f4",
        "treeview_bg": "#313244",
        "treeview_fg": "#cdd6f4",
        "treeview_selected": "#89b4fa",
        "header_bg": "#181825",
        "header_fg": "#cdd6f4",
        "separator": "#45475a",
    },
}


class ThemeManager:
    """Manages application-wide theme switching"""

    def __init__(self):
        self._current_theme = "light"
        self._callbacks = []  # list of callables to invoke after theme change

    @property
    def current(self) -> str:
        return self._current_theme

    @property
    def colors(self) -> dict:
        return THEMES[self._current_theme]

    @property
    def is_dark(self) -> bool:
        return self._current_theme == "dark"

    def toggle(self):
        """Toggle between light and dark mode"""
        self._current_theme = "dark" if self._current_theme == "light" else "light"
        self._apply()

    def set_theme(self, theme_name: str):
        """Set a specific theme"""
        if theme_name in THEMES:
            self._current_theme = theme_name
            self._apply()

    def register_callback(self, callback):
        """Register a callback to be called when theme changes"""
        self._callbacks.append(callback)

    def _apply(self):
        """Notify all callbacks about theme change"""
        for cb in self._callbacks:
            try:
                cb(self.colors)
            except Exception:
                pass

    def apply_to_style(self, style: ttk.Style):
        """Apply current theme to ttk Style"""
        c = self.colors
        style.theme_use('clam')
        style.configure('TFrame', background=c['bg'])
        style.configure('TLabelframe', background=c['bg'], foreground=c['fg'])
        style.configure('TLabelframe.Label', background=c['bg'], foreground=c['fg'])
        style.configure('TLabel', background=c['bg'], foreground=c['fg'])
        style.configure('TButton', background=c['accent'], foreground='white')
        style.map('TButton',
                  background=[('active', c['accent_hover']), ('disabled', c['disabled_bg'])],
                  foreground=[('disabled', c['disabled_fg'])])
        style.configure('TCombobox', fieldbackground=c['input_bg'],
                        background=c['input_bg'], foreground=c['input_fg'])
        style.configure('TEntry', fieldbackground=c['input_bg'], foreground=c['input_fg'])
        style.configure('TNotebook', background=c['bg'])
        style.configure('TNotebook.Tab', background=c['card_bg'], foreground=c['card_fg'],
                        padding=[10, 4])
        style.map('TNotebook.Tab',
                  background=[('selected', c['accent'])],
                  foreground=[('selected', 'white')])
        style.configure('Treeview', background=c['treeview_bg'],
                        foreground=c['treeview_fg'], fieldbackground=c['treeview_bg'])
        style.configure('Treeview.Heading', background=c['accent'],
                        foreground='white')
        style.map('Treeview', background=[('selected', c['treeview_selected'])])
        style.configure('TSeparator', background=c['separator'])
        style.configure('Horizontal.TProgressbar', background=c['accent'])

    def apply_to_root(self, root: tk.Tk):
        """Apply theme to root window background"""
        root.configure(bg=self.colors['bg'])

    def apply_to_toplevel(self, toplevel: tk.Toplevel):
        """Apply theme to a Toplevel window"""
        toplevel.configure(bg=self.colors['bg'])
