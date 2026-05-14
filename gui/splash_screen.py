"""Animated Splash Screen for Smart Retail Billing System"""

import tkinter as tk
from tkinter import ttk
import threading
import time


class SplashScreen:
    """Professional animated splash screen shown on app startup"""

    def __init__(self, root, on_complete=None):
        self.root = root
        self.on_complete = on_complete
        self.root.withdraw()  # Hide main window

        self.splash = tk.Toplevel()
        self.splash.overrideredirect(True)

        # Center on screen
        w, h = 520, 340
        x = (self.splash.winfo_screenwidth() // 2) - (w // 2)
        y = (self.splash.winfo_screenheight() // 2) - (h // 2)
        self.splash.geometry(f"{w}x{h}+{x}+{y}")
        self.splash.configure(bg="#1a1a2e")

        # Main frame with gradient-like effect
        frame = tk.Frame(self.splash, bg="#1a1a2e")
        frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # Top accent line
        tk.Frame(frame, bg="#007acc", height=4).pack(fill=tk.X)

        # Logo area
        logo_frame = tk.Frame(frame, bg="#1a1a2e")
        logo_frame.pack(fill=tk.X, pady=(30, 10))

        tk.Label(logo_frame, text="🛒", font=("Segoe UI Emoji", 42),
                 bg="#1a1a2e", fg="white").pack()

        # Title
        tk.Label(frame, text="Smart Retail Billing System",
                 font=("Arial", 18, "bold"), bg="#1a1a2e", fg="#e0e0e0").pack(pady=(5, 2))

        tk.Label(frame, text="Advanced POS & Inventory Management",
                 font=("Arial", 9), bg="#1a1a2e", fg="#888888").pack()

        # Version
        tk.Label(frame, text="v2.0  |  MCA Project",
                 font=("Arial", 8), bg="#1a1a2e", fg="#555555").pack(pady=(3, 15))

        # Progress bar
        style = ttk.Style()
        style.configure("Splash.Horizontal.TProgressbar",
                         troughcolor="#2a2a3e", background="#007acc", thickness=6)
        self.progress = ttk.Progressbar(frame, length=400, mode='determinate',
                                         style="Splash.Horizontal.TProgressbar")
        self.progress.pack(pady=(10, 5))

        # Status label
        self.status_label = tk.Label(frame, text="Starting...",
                                      font=("Arial", 8), bg="#1a1a2e", fg="#aaaaaa")
        self.status_label.pack()

        # Bottom accent
        tk.Frame(frame, bg="#007acc", height=2).pack(fill=tk.X, side=tk.BOTTOM)

        # Copyright
        tk.Label(frame, text="© 2026 Smart Retail Solutions",
                 font=("Arial", 7), bg="#1a1a2e", fg="#444444").pack(side=tk.BOTTOM, pady=5)

        # Start loading animation
        self.splash.after(100, self._animate)

    def _animate(self):
        """Run loading animation"""
        steps = [
            (10, "Initializing database..."),
            (25, "Loading product catalog..."),
            (40, "Setting up billing engine..."),
            (55, "Configuring barcode scanner..."),
            (70, "Loading analytics modules..."),
            (80, "Initializing voice commands..."),
            (90, "Applying theme settings..."),
            (100, "Ready! Launching application..."),
        ]

        def run():
            for value, text in steps:
                self.splash.after(0, lambda v=value, t=text: self._update(v, t))
                time.sleep(0.3)
            self.splash.after(400, self._finish)

        threading.Thread(target=run, daemon=True).start()

    def _update(self, value, text):
        try:
            self.progress['value'] = value
            self.status_label.config(text=text)
        except Exception:
            pass

    def _finish(self):
        try:
            self.splash.destroy()
            self.root.deiconify()
            if self.on_complete:
                self.on_complete()
        except Exception:
            pass
