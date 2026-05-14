"""Barcode generation and utilities"""

import qrcode
import barcode
from barcode.writer import ImageWriter
import os
from typing import Optional
from PIL import Image


class BarcodeManager:
    """Manage barcode generation and scanning"""

    def __init__(self, barcode_dir: str = "barcodes"):
        self.barcode_dir = barcode_dir
        os.makedirs(barcode_dir, exist_ok=True)

    def generate_barcode(self, barcode_data: str, product_id: str) -> Optional[str]:
        """Generate barcode image"""
        try:
            # Create barcode using ImageWriter and options
            barcode_obj = barcode.get('code128', barcode_data, writer=ImageWriter())
            filename = os.path.join(self.barcode_dir, f"barcode_{product_id}")
            # specify writer options separately (module_width removed from constructor)
            barcode_obj.save(filename, {'module_width': 0.5})
            return f"{filename}.png"
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None

    def generate_qr_code(self, data: str, product_id: str) -> Optional[str]:
        """Generate QR code"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            filename = os.path.join(self.barcode_dir, f"qr_{product_id}.png")
            img.save(filename)
            return filename
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None

    def get_barcode_image(self, product_id: str) -> Optional[Image.Image]:
        """Get barcode image"""
        try:
            barcode_path = os.path.join(self.barcode_dir, f"barcode_{product_id}.png")
            if os.path.exists(barcode_path):
                return Image.open(barcode_path)
        except Exception as e:
            print(f"Error loading barcode: {e}")
        return None

    def get_qr_code_image(self, product_id: str) -> Optional[Image.Image]:
        """Get QR code image"""
        try:
            qr_path = os.path.join(self.barcode_dir, f"qr_{product_id}.png")
            if os.path.exists(qr_path):
                return Image.open(qr_path)
        except Exception as e:
            print(f"Error loading QR code: {e}")
        return None

    def scan_barcode(self, parent=None) -> Optional[str]:
        """Scan a barcode using the default camera (or image file) and return data."""
        try:
            import cv2
            from pyzbar import pyzbar
        except ImportError:
            print("Barcode scanning requires opencv-python and pyzbar packages")
            return None
        # first try camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            try:
                from tkinter import messagebox
                messagebox.showwarning('Camera Unavailable',
                                        'Unable to access camera; please select an image file instead.',
                                        parent=parent)
            except ImportError:
                pass
            # fallback to file dialog
            return self._scan_from_file(parent=parent)
        barcode_data = None
        import sys, os, contextlib
        # helper to silence stderr messages from zbar
        @contextlib.contextmanager
        def _suppress_stderr():
            old_err = sys.stderr
            sys.stderr = open(os.devnull, 'w')
            try:
                yield
            finally:
                sys.stderr.close()
                sys.stderr = old_err

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            with _suppress_stderr():
                decoded = pyzbar.decode(frame)
            if decoded:
                barcode_data = decoded[0].data.decode('utf-8')
                break
            cv2.imshow('Scan Barcode - press q to cancel', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        if barcode_data:
            return barcode_data
        # if nothing captured, allow user to pick file
        return self._scan_from_file(parent=parent)

    def _scan_from_file(self, parent=None) -> Optional[str]:
        """Prompt user to choose an image file and decode barcode from it."""
        try:
            from tkinter import filedialog, messagebox
            from PIL import Image
            from pyzbar import pyzbar
        except ImportError:
            print("Image scanning requires tkinter, pillow and pyzbar")
            return None
        path = filedialog.askopenfilename(title="Select barcode image",
                                          filetypes=[('Image files','*.png;*.jpg;*.jpeg;*.bmp')],
                                          parent=parent)
        if not path:
            return None
        try:
            img = Image.open(path)
            import sys, os, contextlib
            @contextlib.contextmanager
            def _suppress_stderr():
                old_err = sys.stderr
                sys.stderr = open(os.devnull, 'w')
                try:
                    yield
                finally:
                    sys.stderr.close()
                    sys.stderr = old_err
            with _suppress_stderr():
                decoded = pyzbar.decode(img)
            if decoded:
                return decoded[0].data.decode('utf-8')
            else:
                messagebox.showerror('Scan Failed', 'No barcode found in selected image.', parent=parent)
        except Exception as e:
            print(f"Error decoding image: {e}")
        return None

    @staticmethod
    def generate_unique_barcode(product_id: str) -> str:
        """Generate a unique barcode number"""
        import hashlib
        hash_obj = hashlib.sha256(product_id.encode())
        return hash_obj.hexdigest()[:12].upper()
