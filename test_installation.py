#!/usr/bin/env python3
"""
Test script to verify the Smart Retail Billing System installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    tests = [
        ("tkinter", "GUI Framework"),
        ("bcrypt", "Password Hashing"),
        ("qrcode", "QR Code Generation"),
        ("barcode", "Barcode Generation"),
        ("pyzbar", "Barcode Scanning"),
        ("reportlab", "PDF Generation"),
        ("matplotlib", "Charts and Graphs"),
        ("PIL", "Image Processing"),
        ("cv2", "OpenCV (Optional)"),
    ]
    
    failed = []
    for module, description in tests:
        try:
            __import__(module)
            print(f"✓ {module:20} - {description}")
        except ImportError as e:
            if module == "cv2":
                print(f"⚠ {module:20} - {description} (Optional, can skip)")
            else:
                print(f"✗ {module:20} - {description}")
                failed.append(module)
    
    return len(failed) == 0

def test_structure():
    """Test if all required directories exist"""
    print("\nTesting directory structure...")
    
    directories = [
        "data",
        "barcodes", 
        "invoices",
        "gui",
        "models",
        "utils",
    ]
    
    for dir_name in directories:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing")
            return False
    
    return True

def test_files():
    """Test if all required files exist"""
    print("\nTesting required files...")
    
    files = [
        ("app.py", "Main GUI Application"),
        ("models/models.py", "Data Models"),
        ("utils/storage.py", "Storage Manager"),
        ("utils/auth.py", "Authentication"),
        ("utils/billing.py", "Billing Engine"),
        ("utils/barcode.py", "Barcode Manager"),
        ("utils/pdf_generator.py", "PDF Generator"),
        ("gui/main_window.py", "Main Window"),
        ("gui/login_window.py", "Login Window"),
        ("gui/dashboard.py", "Dashboard"),
        ("gui/products.py", "Products UI"),
        ("gui/billing.py", "Billing UI"),
        ("gui/reports.py", "Reports UI"),
        ("gui/settings.py", "Settings UI"),
    ]
    
    missing = []
    for file_path, description in files:
        if os.path.exists(file_path):
            print(f"✓ {file_path:30} - {description}")
        else:
            print(f"✗ {file_path:30} - {description}")
            missing.append(file_path)
    
    return len(missing) == 0

def test_storage():
    """Test if storage is working"""
    print("\nTesting storage...")
    
    try:
        from utils.storage import StorageManager
        storage = StorageManager()
        print("✓ Storage manager initialized")
        
        # Test basic operations
        products = storage.get_all_products()
        print(f"✓ Can read products ({len(products)} products)")
        
        users = storage.get_all_users()
        print(f"✓ Can read users ({len(users)} users)")
        
        return True
    except Exception as e:
        print(f"✗ Storage error: {e}")
        return False


def test_barcode_generation():
    """Test barcode module and generation and simple decoding"""
    print("\nTesting barcode generation...")
    try:
        from utils.barcode import BarcodeManager
        bm = BarcodeManager('barcodes')
        path = bm.generate_barcode('TEST1234', 'test')
        if path and os.path.exists(path):
            print(f"✓ Barcode generated at {path}")
            # attempt to decode using pyzbar directly
            try:
                from pyzbar import pyzbar
                from PIL import Image
                img = Image.open(path)
                decoded = pyzbar.decode(img)
                if decoded:
                    print("✓ Barcode file decoded successfully")
                else:
                    print("⚠ Barcode file could not be decoded")
            except ImportError:
                print("⚠ pyzbar not installed, skipping decode test")
            return True
        else:
            print("✗ Barcode file not created")
            return False
    except Exception as e:
        print(f"✗ Barcode error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Smart Retail Billing System - Installation Test")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Directory Structure": test_structure(),
        "Required Files": test_files(),
        "Storage": test_storage(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:30} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! You can run the application with:")
        print("  python app.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("  Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
