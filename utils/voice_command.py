"""Voice command module for Smart Retail Billing System

Provides voice recognition capabilities for hands-free operation.
Uses the SpeechRecognition library with Google's speech-to-text API.
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox


class VoiceCommandManager:
    """Manages voice command recognition and processing"""

    # Predefined command mappings
    COMMANDS = {
        # Navigation commands
        "open dashboard": "navigate_dashboard",
        "go to dashboard": "navigate_dashboard",
        "show dashboard": "navigate_dashboard",
        "open products": "navigate_products",
        "go to products": "navigate_products",
        "show products": "navigate_products",
        "open billing": "navigate_billing",
        "go to billing": "navigate_billing",
        "create invoice": "navigate_billing",
        "new invoice": "navigate_billing",
        "open reports": "navigate_reports",
        "go to reports": "navigate_reports",
        "show reports": "navigate_reports",
        "open settings": "navigate_settings",
        "go to settings": "navigate_settings",
        # Product commands
        "add product": "add_product",
        "new product": "add_product",
        "search product": "search_product",
        "find product": "search_product",
        "refresh products": "refresh_products",
        # Billing commands
        "add item": "add_item",
        "finalize invoice": "finalize_invoice",
        "save invoice": "finalize_invoice",
        "generate pdf": "generate_pdf",
        "print invoice": "generate_pdf",
        "new bill": "new_invoice",
        "clear bill": "new_invoice",
        # General commands
        "logout": "logout",
        "log out": "logout",
        "exit": "exit_app",
        "close": "close_window",
        "help": "show_help",
    }

    def __init__(self):
        self.is_listening = False
        self._recognizer = None
        self._microphone = None
        self._available = False
        self._callback = None
        self._status_callback = None
        self._listen_thread = None
        self._check_availability()

    def _check_availability(self):
        """Check if speech recognition libraries are available"""
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._microphone = sr.Microphone()
            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False

    @property
    def available(self):
        return self._available

    def set_command_callback(self, callback):
        """Set callback function for when a command is recognized
        callback(command_key: str, raw_text: str)
        """
        self._callback = callback

    def set_status_callback(self, callback):
        """Set callback function for status updates
        callback(status: str, is_error: bool)
        """
        self._status_callback = callback

    def _update_status(self, status, is_error=False):
        """Update status via callback"""
        if self._status_callback:
            self._status_callback(status, is_error)

    def start_listening(self):
        """Start listening for voice commands in a background thread"""
        if not self._available:
            self._update_status("Voice recognition not available. Install SpeechRecognition and PyAudio.", True)
            return False

        if self.is_listening:
            return True

        self.is_listening = True
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()
        self._update_status("🎤 Listening for voice commands...")
        return True

    def stop_listening(self):
        """Stop listening for voice commands"""
        self.is_listening = False
        self._update_status("🔇 Voice commands stopped")

    def _listen_loop(self):
        """Background listening loop"""
        import speech_recognition as sr

        while self.is_listening:
            try:
                with self._microphone as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self._update_status("🎤 Listening... Speak a command")
                    audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=5)

                try:
                    text = self._recognizer.recognize_google(audio, language="en-IN").lower().strip()
                    self._update_status(f"🗣️ Heard: \"{text}\"")
                    self._process_command(text)
                except sr.UnknownValueError:
                    self._update_status("🔇 Could not understand. Try again...")
                except sr.RequestError as e:
                    self._update_status(f"⚠️ Speech service error: {e}", True)

            except sr.WaitTimeoutError:
                # Timeout waiting for speech, just continue
                continue
            except Exception as e:
                if self.is_listening:
                    self._update_status(f"⚠️ Error: {str(e)}", True)

    def _process_command(self, text):
        """Process recognized text and find matching command"""
        # Try exact match first
        for phrase, command_key in self.COMMANDS.items():
            if phrase in text:
                self._update_status(f"✅ Command: {phrase}")
                if self._callback:
                    self._callback(command_key, text)
                return

        # If no command matched, report it
        self._update_status(f"❓ Unknown command: \"{text}\". Say 'help' for commands.")

    def listen_once(self, callback=None):
        """Listen for a single voice input and return the text.
        Useful for filling form fields via voice.
        """
        if not self._available:
            return None

        def _single_listen():
            import speech_recognition as sr
            try:
                with self._microphone as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self._update_status("🎤 Listening for input...")
                    audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=8)

                text = self._recognizer.recognize_google(audio, language="en-IN").strip()
                self._update_status(f"✅ Got: \"{text}\"")
                if callback:
                    callback(text)
            except Exception as e:
                self._update_status(f"⚠️ Could not understand: {e}", True)
                if callback:
                    callback(None)

        t = threading.Thread(target=_single_listen, daemon=True)
        t.start()

    def get_help_text(self):
        """Return help text with all available commands"""
        help_lines = [
            "🎤 Available Voice Commands:\n",
            "📍 Navigation:",
            "  • 'Open Dashboard' / 'Open Products'",
            "  • 'Open Billing' / 'Open Reports'",
            "  • 'Open Settings'",
            "",
            "📦 Products:",
            "  • 'Add Product' / 'New Product'",
            "  • 'Search Product' / 'Find Product'",
            "  • 'Refresh Products'",
            "",
            "💳 Billing:",
            "  • 'Add Item' / 'New Bill'",
            "  • 'Finalize Invoice' / 'Save Invoice'",
            "  • 'Generate PDF' / 'Print Invoice'",
            "",
            "⚙️ General:",
            "  • 'Logout' / 'Exit' / 'Close'",
            "  • 'Help' - Show this help",
        ]
        return "\n".join(help_lines)


class VoiceCommandWidget(ttk.Frame):
    """A reusable widget that provides voice command UI controls"""

    def __init__(self, parent, voice_manager: VoiceCommandManager, **kwargs):
        super().__init__(parent, **kwargs)
        self.voice_manager = voice_manager
        self._setup_ui()

    def _setup_ui(self):
        """Create voice command UI elements"""
        # Mic button
        self.mic_btn = ttk.Button(self, text="🎤 Voice", command=self.toggle_listening,
                                   width=12)
        self.mic_btn.pack(side=tk.LEFT, padx=2)

        # Status label
        self.status_label = ttk.Label(self, text="", font=("Arial", 8),
                                       foreground="#666666", width=40)
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Help button
        self.help_btn = ttk.Button(self, text="❓", command=self.show_help, width=3)
        self.help_btn.pack(side=tk.LEFT, padx=2)

        # Set status callback
        self.voice_manager.set_status_callback(self._on_status_update)

        if not self.voice_manager.available:
            self.mic_btn.configure(state="disabled")
            self.status_label.configure(text="Voice: Install SpeechRecognition & PyAudio")

    def toggle_listening(self):
        """Toggle voice listening on/off"""
        if self.voice_manager.is_listening:
            self.voice_manager.stop_listening()
            self.mic_btn.configure(text="🎤 Voice")
        else:
            if self.voice_manager.start_listening():
                self.mic_btn.configure(text="🔴 Stop")

    def _on_status_update(self, status, is_error=False):
        """Handle status updates from voice manager (thread-safe)"""
        try:
            self.after(0, lambda: self._update_status_label(status, is_error))
        except Exception:
            pass

    def _update_status_label(self, status, is_error):
        """Update status label on main thread"""
        try:
            color = "#e74c3c" if is_error else "#27ae60"
            self.status_label.configure(text=status, foreground=color)
            if not self.voice_manager.is_listening:
                self.mic_btn.configure(text="🎤 Voice")
        except Exception:
            pass

    def show_help(self):
        """Show voice command help"""
        help_text = self.voice_manager.get_help_text()
        messagebox.showinfo("Voice Commands Help", help_text)
