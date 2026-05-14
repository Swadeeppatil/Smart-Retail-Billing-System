# Smart Retail Billing System

A comprehensive, advanced GUI-based retail billing and inventory management system built with Python. Completely offline with local data storage (JSON/CSV based).


https://github.com/user-attachments/assets/4f942efb-b2fb-46e0-b38d-a6a86cba742d


## 🎯 Features

### Core Features

#### 1. **Product Management**
- Add/edit/delete products
- Auto-generated unique product IDs
- Barcode generation (Code128 & QR codes)
- Product categories and descriptions
- Cost and selling price management
- Low stock alerts (customizable threshold)

#### 2. **Barcode System**
- Auto-generate barcodes for each product
- QR code generation
- Barcode image storage locally
- Search products by barcode
- Scan barcode via webcam during billing (requires OpenCV & pyzbar)
- Alternatively select a saved barcode image if camera is unavailable
- Easy product lookup during billing

#### 3. **Billing System**
- Create professional invoices
- Add products by:
  - Product name search or barcode scan (use the "Scan" button to read via webcam)
  - Manual quantity entry
  - Discount per item or invoice-wide
- GST calculation (customizable percentage)
- Payment modes: Cash, UPI, Card
- PDF invoice generation with professional layout
- Invoice history with search

#### 4. **Inventory Management**
- Real-time stock tracking
- Automatic stock deduction on sale
- Stock purchase entries
- Stock movement history
- Low stock notifications
- Inventory reports

#### 5. **Dashboard**
- Sales summary (daily, monthly)
- Revenue statistics
- Low stock items display
- Top-selling products chart
- Profit analytics
- Real-time inventory value

#### 6. **Reports & Analytics**
- Daily/weekly/monthly sales reports
- Profit analysis with visual charts
- Product-wise sales breakdown
- Customer purchase history
- GST collection reports
- Export reports to CSV

#### 7. **Advanced Features**
- User authentication (Admin/Staff roles)
- Password protection with bcrypt hashing
- Data backup and restore
- Settings customization
- Multi-user support
- Profit calculation (cost vs selling price)
- Loyalty points tracking (extensible)
- Dark mode ready

#### 8. **Data Security**
- Local-only storage (no cloud dependency)
- Encrypted password storage
- Data backup functionality
- JSON-based storage for portability
- No external database required

## 📁 Project Structure

```
Agrement/
├── app.py                      # Main entry point (GUI)
├── main.py                     # Alternative CLI entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── gui/                        # GUI Components
│   ├── main_window.py         # Main application window
│   ├── login_window.py        # Login interface
│   ├── dashboard.py           # Dashboard with analytics
│   ├── products.py            # Product management UI
│   ├── billing.py             # Billing/Invoice creation
│   ├── reports.py             # Reports and charts
│   └── settings.py            # Settings and user management
│
├── models/                     # Data Models
│   ├── models.py              # Product, Invoice, Customer, User dataclasses
│   └── __init__.py
│
├── utils/                      # Utility Modules
│   ├── storage.py             # JSON-based storage manager
│   ├── auth.py                # Authentication and user management
│   ├── billing.py             # Billing calculations
│   ├── barcode.py             # Barcode generation/handling
│   ├── pdf_generator.py       # PDF invoice generation
│   └── __init__.py
│
├── data/                       # Data Storage (Auto-created)
│   ├── products.json          # Products database
│   ├── invoices.json          # Invoice index
│   ├── customers.json         # Customer records
│   ├── users.json             # User accounts
│   ├── stock_movements.json   # Stock history
│   └── backups/               # Backup files
│
├── barcodes/                   # Generated Barcode Images
│   ├── barcode_*.png
│   └── qr_*.png
│
└── invoices/                   # Generated PDF Invoices
    └── INV-*.pdf


**Note:** Barcode scanning uses your camera and requires the `opencv-python` and `pyzbar` packages from `requirements.txt`.```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project
```bash
cd Agrement
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

Or for CLI version:
```bash
python main.py
```

### First Time Setup
- On first launch, a default admin account is created: `username: admin, password: admin123`
- **Change this password immediately in Settings > Account > Change Password**

## 💻 Usage Guide

### Login
1. Start the application
2. Enter credentials (default: admin/admin123)
3. Click Login

### Dashboard
- View today's sales
- Monitor monthly revenue
- Check low stock items
- See top-selling products
- View analytics charts

### Product Management
1. Click "Products" button
2. Add new products with:
   - Name, Category, Cost Price, Selling Price
   - Stock quantity
   - Auto-generated barcode
3. Edit existing products
4. Delete products (if not referenced in sales)
5. Search products by name

### Create Invoice/Bill
1. Click "Billing" button
2. Enter customer name (optional)
3. Add products:
   - Select from dropdown
   - Enter quantity
   - Apply item-wise discount if needed
4. Set invoice-wide discount (%)
5. Select GST rate
6. Choose payment mode
7. Click "Finalize & Save" to record sale
8. Click "Generate PDF" for invoice document

### View Reports
1. Click "Reports" button
2. Select date range
3. View different report types:
   - Sales Report (daily chart)
   - Profit Analysis (profit trends)
   - Product Sales (top selling items)
   - Summary (totals and statistics)
4. Export reports to CSV

### Settings
1. Click "Settings" button
2. **General**: Configure GST rate and low stock level
3. **Account**: Change your password
4. **User Management** (Admin only):
   - Add new users
   - Delete users
   - Manage roles
5. **Backup & Restore**:
   - Create automatic backups
   - Restore from previous backups
   - Clear all data (use with caution)

## 🔐 User Roles

### Admin
- All permissions
- Can manage users
- Can access all reports
- Can create backups
- Can change settings

### Staff/Cashier
- Can create invoices
- Can view products
- Can view their own reports
- Cannot manage users
- Cannot change settings

## 📊 Data Storage

All data is stored locally in JSON format:
- **products.json**: Product catalog with pricing and stock
- **invoices.json**: Invoice index and details
- **customers.json**: Customer information and history
- **users.json**: User accounts with encrypted passwords
- **stock_movements.json**: Stock transaction history

### Backup & Restore
- Automatic backup creation with timestamp
- Store in `data/backups/` directory
- One-click restore from any backup
- Prevents accidental data loss

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| UI Framework | Tkinter (Standard Python GUI) |
| Data Storage | JSON files (Local) |
| Authentication | bcrypt (Password hashing) |
| Barcode Generation | python-barcode, qrcode |
| PDF Generation | ReportLab |
| Charts/Graphs | matplotlib |
| Image Processing | OpenCV, Pillow |

## 📈 Key Metrics Tracked

- **Sales**: Daily, weekly, monthly revenue
- **Profit**: Based on cost price vs selling price
- **Inventory**: Stock levels, stock movements, low stock items
- **Products**: Sales count, profit per product
- **Customers**: Purchase history, total spent
- **GST**: Collected GST amount and rate

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Login | Enter (in password field) |
| Add Item | Ctrl+N (in billing) |
| Save Invoice | Ctrl+S (in billing) |
| Generate PDF | Ctrl+P (in billing) |

## 🐛 Troubleshooting

### Application won't start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Barcode generation fails
- Ensure `barcodes/` directory exists
- Check file write permissions

### PDF generation issues
- Ensure `invoices/` directory exists
- Check free disk space

### Data not saving
- Check `data/` directory permissions
- Ensure disk is not full

## 📝 License

This project is provided as-is for retail billing purposes.

## 🤝 Contributing

Improvements welcome! Areas for expansion:
- Multi-language support
- Customer loyalty programs
- Advanced analytics
- Mobile app integration
- Cloud sync (optional)

## 📞 Support

For issues or questions:
1. Check the data directory for error logs
2. Verify all dependencies are installed
3. Ensure JSON files in data/ are valid
4. Clear data/backups and restore from backup if corrupted

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Status**: Production Ready ✅
