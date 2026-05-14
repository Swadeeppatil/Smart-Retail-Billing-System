
"""
Smart Retail Billing System - GUI Application
Advanced billing and inventory management system with local data storage
"""

import sys
import tkinter as tk
from gui.splash_screen import SplashScreen
from gui.main_window import MainWindow


def main():
    """Launch the application with splash screen"""
    root = tk.Tk()
    root.title("Smart Retail Billing System")
    root.geometry("1000x600")
    root.minsize(800, 600)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Show splash screen, then start app
    def on_splash_done():
        app = MainWindow(root)

    splash = SplashScreen(root, on_complete=on_splash_done)
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
