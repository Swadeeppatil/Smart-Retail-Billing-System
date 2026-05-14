# SETUP.md - Installation and Setup Guide

## Smart Retail Billing System - Complete Setup Guide

---

## 📋 SYSTEM REQUIREMENTS

### Minimum Requirements
- **OS**: Windows 7+, macOS 10.12+, Linux (Ubuntu 16.04+)
- **Python**: 3.8 or higher
- **RAM**: 2 GB minimum
- **Disk Space**: 500 MB (including dependencies)
- **Display**: 1024x768 minimum resolution

### Recommended Requirements
- **OS**: Windows 10+, macOS 11+, Ubuntu 20.04+
- **Python**: 3.9 or higher
- **RAM**: 4 GB
- **Disk Space**: 1 GB
- **Display**: 1920x1080

---

## 🔧 INSTALLATION STEPS

### Step 1: Install Python

#### Windows
1. Download Python from [python.org](https://python.org)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"

#### macOS
```bash
# Using Homebrew
brew install python3

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

### Step 2: Verify Python Installation

```bash
python --version
# Should show Python 3.8+

pip --version
# Should show pip version
```

### Step 3: Download the Project

```bash
# Clone if using git
git clone https://github.com/yourusername/smart-retail-billing.git

# Or extract from ZIP file
unzip smart-retail-billing.zip
cd Agrement
```

### Step 4: Install Dependencies

```bash
# Navigate to project directory
cd Agrement

# Install all required packages
pip install -r requirements.txt

# Or install individually (if preferred)
pip install tkinter bcrypt qrcode python-barcode reportlab matplotlib pillow opencv-python pyzbar

> **Note:** Barcode scanning uses your system camera and requires the `opencv-python` and `pyzbar` packages. Ensure a webcam is connected and accessible.```

### Step 5: Verify Installation

```bash
python test_installation.py

# You should see:
# ✓ All tests passed! You can run the application with:
#   python app.py
```

### Step 6: Create Demo Data (Optional)

```bash
python quick_start.py --demo

# This creates:
# - Admin and staff users
# - 5 sample products
# - 2 sample customers
```

---

## 🚀 RUNNING THE APPLICATION

### Method 1: Direct Python (Recommended)

```bash
python app.py
```

### Method 2: Using Python Executable

```bash
python3 app.py  # On macOS/Linux
```

### Method 3: Create Shortcut (Windows)

Create a file named `run.bat`:
```batch
@echo off
python app.py
pause
```

Double-click `run.bat` to run the application.

### Method 4: Run on Startup (Optional)

#### Windows
1. Press `Win + R`
2. Type: `shell:startup`
3. Create shortcut to `run.bat` or `app.py`

#### macOS/Linux
Add to `~/.bashrc` or `~/.zshrc`:
```bash
alias billing="cd ~/Agrement && python app.py"
```

---

## 🔑 FIRST TIME LOGIN

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`

### ⚠️ IMPORTANT SECURITY STEPS

1. **Open the application**
   ```bash
   python app.py
   ```

2. **Login with default credentials**
   - Username: admin
   - Password: admin123

3. **Change password immediately**
   - Click "Settings" button
   - Select "Account" tab
   - Enter old password: `admin123`
   - Enter new password: (strong password)
   - Click "Change Password"

4. **Create staff user (optional)**
   - In Settings, select "User Management"
   - Click "Add User"
   - Enter username, password, select role "staff"
   - Click "Create"

---

## 📁 DIRECTORY STRUCTURE AFTER SETUP

```
Agrement/
├── app.py                      # Run this to start
├── main.py                     # Alternative CLI version
├── quick_start.py              # Create demo data
├── test_installation.py        # Verify setup
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
├── FEATURES.md                 # Feature list
├── SETUP.md                    # This file
│
├── gui/                        # GUI Components
│   ├── main_window.py
│   ├── login_window.py
│   ├── dashboard.py
│   ├── products.py
│   ├── billing.py
│   ├── reports.py
│   ├── settings.py
│   └── __init__.py
│
├── models/                     # Data Models
│   ├── models.py
│   └── __init__.py
│
├── utils/                      # Utilities
│   ├── storage.py
│   ├── auth.py
│   ├── billing.py
│   ├── barcode.py
│   ├── pdf_generator.py
│   └── __init__.py
│
├── data/                       # Auto-created on first run
│   ├── products.json
│   ├── invoices.json
│   ├── customers.json
│   ├── users.json
│   ├── stock_movements.json
│   └── backups/
│
├── barcodes/                   # Auto-created
│   ├── barcode_*.png
│   └── qr_*.png
│
└── invoices/                   # Auto-created
    └── INV-*.pdf
```

---

## 🐛 TROUBLESHOOTING

### "Python not found"
```bash
# Windows: Use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python310\python.exe app.py

# macOS/Linux
which python3
python3 app.py
```

### "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or install specific missing package
pip install [package_name]
```

### "No module named 'tkinter'"

#### Windows
Tkinter should be installed with Python. If not:
- Reinstall Python
- Check "tcl/tk and IDLE" during installation

#### macOS
```bash
brew install python-tk@3.10
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt install python3-tk
```

### "Permission denied"
```bash
# Windows: Run as Administrator
# macOS/Linux: Use sudo
sudo python app.py

# Or change directory permissions
chmod -R 755 /path/to/Agrement
```

### Application won't start
```bash
# Test individual imports
python -c "import tkinter; print('OK')"
python -c "import bcrypt; print('OK')"

# Run test script
python test_installation.py

# Check logs in data/ directory
```

### JSON files corrupted
```bash
# Delete corrupted data
rm -r data/

# Application will auto-create new data structure
python app.py
```

### Cannot login
1. Check username and password spelling
2. Verify users.json exists: `cat data/users.json`
3. Reset data and create demo data: `python quick_start.py --demo`

### Slow performance
1. Check if you have many invoices (>10000)
2. Archive old invoices if needed
3. Reduce chart data range in reports
4. Close other applications
5. Increase available RAM

### PDF generation fails
```bash
# Check if invoices directory exists
ls -la invoices/

# Check disk space
df -h

# Check permissions
chmod 755 invoices/

# Reinstall reportlab
pip install --upgrade reportlab
```

---

## 🔄 DATA MANAGEMENT

### Backup Data
```bash
python quick_start.py
# Or from UI: Settings → Backup & Restore → Create Backup
```

### Restore Data
From UI: Settings → Backup & Restore → Restore from Backup

### Move Data to Another Computer
1. Copy entire `Agrement` folder
2. Install Python and dependencies on new computer
3. Run `python app.py`
4. All your data will be available

### Reset Everything
```bash
# Delete all data (use with caution!)
rm -r data/
python quick_start.py --demo  # Create fresh demo data
```

---

## 📊 UPGRADING

### From Version 0.x to 1.0

1. **Backup your data**
   ```bash
   cp -r data/ data_backup/
   ```

2. **Update code**
   - Download latest version
   - Replace files (keep `data/` folder)

3. **Update dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Run application**
   ```bash
   python app.py
   ```

---

## 🔐 SECURITY SETUP

### Change Default Credentials
```bash
# Step 1: Open app and login with admin/admin123
python app.py

# Step 2: Go to Settings → Account → Change Password
# Old: admin123
# New: Strong Password (mix of letters, numbers, symbols)
```

### Create Limited Access Users
```bash
# Don't use admin for daily operations
# Create staff users for cashiers
Settings → User Management → Add User
- Role: staff (not admin)
```

### Regular Backups
```bash
# Create backups weekly
Settings → Backup & Restore → Create Backup

# Or automate with cron/scheduler
```

### Data Protection
- Keep `data/` folder in a secure location
- Use system-level file encryption if possible
- Regular backups on external drive
- Never share password_hash values

---

## 📱 MULTI-USER SETUP

### Admin Setup
1. Admin creates login for each cashier
2. Each cashier gets unique username/password
3. Staff users can only create invoices
4. Admin tracks who created each invoice

### Network Setup (Advanced)
For multi-location use, consider:
1. NAS/shared folder for data/
2. Sync data between locations daily
3. Or use database (requires modification)

---

## 🎯 QUICK REFERENCE

| Task | Command |
|------|---------|
| Start App | `python app.py` |
| Create Demo Data | `python quick_start.py --demo` |
| Test Installation | `python test_installation.py` |
| Install Dependencies | `pip install -r requirements.txt` |
| Check Python Version | `python --version` |
| List Installed Packages | `pip list` |
| Update Pip | `pip install --upgrade pip` |
| Reset Data | `rm -r data/` |
| Backup Data | UI: Settings → Backup & Restore |
| Restore Data | UI: Settings → Backup & Restore |

---

## 🆘 SUPPORT & HELP

### Check System Info
```bash
python -c "import sys; print(sys.version)"
python -c "import tkinter; print(tkinter.TkVersion)"
python -c "import json; print('JSON OK')"
```

### Enable Debug Mode
```python
# Add at top of app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Error Messages

| Error | Solution |
|-------|----------|
| `No module named 'X'` | `pip install X` |
| `Permission denied` | Run as admin/sudo |
| `Port already in use` | Close other applications |
| `JSON decode error` | Delete corrupted data/ directory |
| `Tkinter error` | Reinstall Python with Tk |

---

## 📞 GETTING HELP

1. Check README.md for features
2. Review FEATURES.md for complete list
3. Run test_installation.py to verify setup
4. Check data/ directory for logs
5. Review error messages carefully

---

## ✅ SETUP COMPLETE!

If you've successfully completed all steps:
1. ✓ Python installed and verified
2. ✓ Dependencies installed
3. ✓ Test installation passed
4. ✓ Application runs without errors
5. ✓ Login working with default credentials
6. ✓ Password changed
7. ✓ Data appears in Dashboard

You're ready to use the Smart Retail Billing System!

```bash
python app.py
```

---

**Need help?** Refer to README.md or check inline code comments.

**Found a bug?** Check test_installation.py or review error logs.

**Happy billing!** 🎉

---

Version: 1.0.0  
Last Updated: February 2026  
Status: Production Ready ✅
