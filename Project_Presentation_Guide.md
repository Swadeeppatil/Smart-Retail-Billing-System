# 🎓 Smart Retail Billing System — Complete Project Presentation Guide

> **Read this document fully before your presentation. It covers everything the examiner may ask.**

---

## 1. PROJECT OVERVIEW

### What is this project?
**Smart Retail Billing System** is a **desktop application** built using **Python** for retail shop billing and inventory management. It helps shopkeepers manage products, create invoices, track inventory, generate PDF bills, scan barcodes/QR codes, and view sales analytics.

### Problem Statement
Small and medium retail shops still rely on **manual billing** using pen-and-paper or basic calculators. This leads to:
- Errors in calculations (GST, discounts)
- No inventory tracking (products go out of stock without notice)
- No sales records or reports
- No security (anyone can access billing)
- Time-consuming manual invoice creation

### Solution
This system **automates** the entire retail billing process with:
- Computerized billing with automatic GST and discount calculations
- Real-time inventory management with low-stock alerts
- Barcode and QR code scanning for fast product lookup
- PDF invoice generation
- Sales analytics and reporting with charts
- User authentication with role-based access (Admin/Staff)
- Data backup and restore

### Project Type
- **Type:** Desktop Application (GUI-based)
- **Domain:** Retail / Point of Sale (POS)
- **Development Model:** Modular Architecture (MVC-like pattern)

---

## 2. TECHNOLOGY STACK

| Component | Technology | Why We Used It |
|-----------|-----------|---------------|
| **Language** | Python 3.10 | Easy to learn, rich library ecosystem, rapid development |
| **GUI Framework** | Tkinter (with ttk) | Built-in with Python, no extra installation, cross-platform |
| **Database** | SQLite | Lightweight, serverless, file-based, no setup needed |
| **PDF Generation** | ReportLab | Professional PDF creation with tables, styles, headers |
| **Barcode Generation** | python-barcode | Generates Code128 barcode images |
| **QR Code Generation** | qrcode (with PIL) | Generates QR code images for products and UPI payments |
| **Barcode/QR Scanning** | OpenCV + pyzbar | Camera-based scanning and image file decoding |
| **Charts & Graphs** | Matplotlib | Embedded charts in dashboard and reports |
| **Password Security** | bcrypt | Industry-standard password hashing algorithm |
| **Image Processing** | Pillow (PIL) | Image handling for barcodes, QR codes |

### Why These Technologies?

**Why Python?** → Python is ideal for rapid application development. It has extensive libraries for GUI, database, PDF generation, and image processing — all needed in this project.

**Why Tkinter?** → It comes built-in with Python (no extra installation). It supports cross-platform GUI development. The `ttk` module provides modern-looking themed widgets.

**Why SQLite?** → It's a serverless, zero-configuration database. The entire database is stored in a single file (`pos_database.sqlite`). Perfect for desktop applications that don't need a separate database server.

**Why bcrypt?** → It uses salted hashing, making it resistant to rainbow table attacks. It's the industry standard for password storage. Each password gets a unique salt automatically.

---

## 3. PROJECT ARCHITECTURE

### Folder Structure
```
Smart Retail Billing System/
├── app.py                  ← Entry point (starts the application)
├── requirements.txt        ← All Python dependencies
│
├── models/
│   └── models.py           ← Data classes (Product, Invoice, User, etc.)
│
├── utils/
│   ├── storage.py          ← Database operations (SQLite CRUD)
│   ├── auth.py             ← Authentication (login, password hashing)
│   ├── billing.py          ← Billing calculations (totals, GST, stock)
│   ├── barcode.py          ← Barcode/QR generation and scanning
│   └── pdf_generator.py    ← PDF invoice creation
│
├── gui/
│   ├── login_window.py     ← Login screen
│   ├── main_window.py      ← Main menu and navigation
│   ├── dashboard.py        ← Dashboard with stats and charts
│   ├── products.py         ← Product management (CRUD)
│   ├── billing.py          ← Invoice creation and billing
│   ├── reports.py          ← Sales reports and analytics
│   └── settings.py         ← Settings, user management, backup
│
├── data/
│   └── pos_database.sqlite ← SQLite database file
│
├── barcodes/               ← Generated barcode and QR code images
└── invoices/               ← Generated PDF invoices
```

### Architecture Pattern: MVC-like (Model-View-Controller)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   VIEW      │     │ CONTROLLER  │     │   MODEL      │
│ (gui/*.py)  │────▶│(utils/*.py) │────▶│(models/*.py) │
│ Tkinter UI  │     │ Business    │     │ Data Classes │
│ Screens     │◀────│ Logic       │◀────│ + SQLite DB  │
└─────────────┘     └─────────────┘     └─────────────┘
```

- **Model** (`models/models.py`): Defines data structures — Product, Invoice, BillItem, User, Customer, StockMovement
- **View** (`gui/*.py`): All the Tkinter screens the user sees and interacts with
- **Controller** (`utils/*.py`): Business logic — storage, authentication, billing calculations, barcode handling, PDF generation

---

## 4. DATABASE DESIGN

### Database: SQLite (file: `data/pos_database.sqlite`)

### Table 1: `products`
| Column | Type | Description |
|--------|------|-------------|
| product_id | TEXT (PK) | Auto-generated unique ID (e.g., PRD-a1b2c3d4) |
| name | TEXT | Product name |
| category | TEXT | Product category |
| cost_price | REAL | Purchase/cost price |
| selling_price | REAL | Selling price to customer |
| stock_quantity | INTEGER | Current stock count |
| barcode | TEXT | Barcode string (12-char hash) |
| expiry_date | TEXT | Product expiry date |
| created_at | TEXT | Record creation timestamp |
| updated_at | TEXT | Last update timestamp |

### Table 2: `invoices`
| Column | Type | Description |
|--------|------|-------------|
| invoice_id | TEXT (PK) | Auto-generated (e.g., INV-20260424185300) |
| customer_name | TEXT | Customer name (default: Walk-in Customer) |
| customer_phone | TEXT | Customer phone number |
| customer_email | TEXT | Customer email |
| subtotal | REAL | Sum of all items before discount/GST |
| discount_percent | REAL | Overall discount percentage |
| discount_amount | REAL | Calculated discount amount |
| gst_percent | REAL | GST percentage (default 18%) |
| gst_amount | REAL | Calculated GST amount |
| grand_total | REAL | Final amount after discount + GST |
| payment_mode | TEXT | Cash / UPI / Card |
| created_at | TEXT | Invoice creation timestamp |
| created_by | TEXT | Cashier/user who created it |
| notes | TEXT | Additional notes |

### Table 3: `bill_items`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Auto-increment ID |
| invoice_id | TEXT (FK) | Links to invoices table |
| product_id | TEXT | Product reference |
| product_name | TEXT | Product name |
| quantity | INTEGER | Quantity purchased |
| unit_price | REAL | Price per unit |
| discount_percent | REAL | Item-level discount |
| line_total | REAL | Total for this line item |

### Table 4: `users`
| Column | Type | Description |
|--------|------|-------------|
| user_id | TEXT (PK) | Unique user ID |
| username | TEXT (UNIQUE) | Login username |
| password_hash | TEXT | bcrypt hashed password |
| role | TEXT | "admin" or "staff" |
| name | TEXT | Display name |
| created_at | TEXT | Account creation date |
| is_active | INTEGER | 1=active, 0=deactivated |

### Table 5: `customers`
| Column | Type | Description |
|--------|------|-------------|
| customer_id | TEXT (PK) | Unique customer ID |
| name | TEXT | Customer name |
| phone | TEXT | Phone number |
| email | TEXT | Email address |
| loyalty_points | REAL | Loyalty points earned |
| total_purchases | REAL | Total purchase amount |
| created_at | TEXT | Registration date |

### Table 6: `stock_movements`
| Column | Type | Description |
|--------|------|-------------|
| movement_id | TEXT (PK) | Unique movement ID |
| product_id | TEXT | Which product |
| movement_type | TEXT | SALE / PURCHASE / ADJUSTMENT |
| quantity | INTEGER | Quantity moved (negative for sales) |
| reference_id | TEXT | Invoice ID reference |
| created_at | TEXT | Movement timestamp |
| notes | TEXT | Additional notes |

### Relationships
- **invoices ↔ bill_items**: One-to-Many (one invoice has many items)
- **products ↔ bill_items**: One-to-Many (one product can appear in many bills)
- **products ↔ stock_movements**: One-to-Many (one product has many movements)

---

## 5. MODULE DESCRIPTIONS

### Module 1: Login & Authentication
**File:** `gui/login_window.py`, `utils/auth.py`

**What it does:**
- Shows a login screen when the app starts
- Validates username and password against the database
- Passwords are stored as **bcrypt hashes** (never in plain text)
- Default admin account: username=`admin`, password=`admin123`
- Supports creating new users from the login screen

**How password hashing works:**
```
User enters: "admin123"
    ↓
bcrypt generates random salt: "$2b$12$xyz..."
    ↓
bcrypt creates hash: "$2b$12$xyz...hashed_password_here"
    ↓
Hash stored in database (original password is NEVER stored)
    ↓
During login: bcrypt.checkpw("admin123", stored_hash) → True/False
```

### Module 2: Dashboard
**File:** `gui/dashboard.py`

**What it does:**
- Shows **real-time statistics**: Total Products, Today's Sales, Today's Invoices, Monthly Revenue
- **Sales Chart** (last 7 days) — bar chart using Matplotlib
- **Top Selling Products** — horizontal bar chart
- **Low Stock Items** — table of products with stock ≤ 10
- **Expiring Items** — products expiring within 30 days (highlighted in red/yellow)
- Red alert banner if expired products exist

### Module 3: Product Management
**File:** `gui/products.py`

**What it does:**
- **Add Product**: Name, category, cost price, selling price, stock quantity, barcode, expiry date
- **Edit Product**: Modify any product detail
- **Delete Product**: Remove product from database
- **Search Products**: Search by name
- **Generate Barcode**: Creates unique 12-character barcode using SHA-256 hash
- **Generate QR Code**: Auto-creates QR code image for each product
- Color-coded rows: Red = low stock, Pink = expired, Yellow = expiring soon

### Module 4: Billing / Invoice Creation
**File:** `gui/billing.py`, `utils/billing.py`

**What it does:**
- Select products from dropdown or **scan barcode/QR code**
- Add items with quantity and per-item discount
- **Auto-calculates**: Subtotal, Overall Discount, GST (configurable: 0%, 5%, 12%, 18%), Grand Total
- **Beep sound** when product is added (Windows)
- **Expiry check**: Blocks billing of expired products, warns for soon-expiring ones
- **Generate PDF Invoice** — professional PDF with company header, item table, totals
- **Send via WhatsApp** — formats bill as WhatsApp message with customer phone
- **UPI QR Code** — generates dynamic UPI payment QR code for the bill amount
- **Stock auto-deduction** — stock quantity reduces when invoice is finalized
- **Stock movement tracking** — records every sale in stock_movements table

**Billing Calculation Formula:**
```
Subtotal = Σ (quantity × unit_price - item_discount) for each item
Discount Amount = Subtotal × (discount_percent / 100)
Taxable Amount = Subtotal - Discount Amount
GST Amount = Taxable Amount × (gst_percent / 100)
Grand Total = Taxable Amount + GST Amount
```

### Module 5: Reports & Analytics
**File:** `gui/reports.py`

**What it does:**
- **Date filter**: Filter reports by From/To date range
- **Sales Report**: Line chart showing daily sales
- **Profit Analysis**: Bar chart (green = profit, red = loss)
- **Product Sales**: Top 10 selling products bar chart
- **Summary Tab**: Total Revenue, Total Profit, GST Collected, Profit Margin %, Total Invoices, Avg Invoice Value
- **Export to CSV**: Export filtered data as CSV file

### Module 6: Settings & Administration
**File:** `gui/settings.py`

**What it does:**
- **General Settings**: Configure GST rate, shop name, low stock alert level
- **Account Management**: Change password (with old password verification)
- **User Management** (Admin only): Add/delete staff users, view all users
- **Backup & Restore**: Create database backup, restore from backup
- **Clear All Data**: Danger zone — deletes all data (double confirmation required)

---

## 6. KEY FEATURES SUMMARY

| # | Feature | How It Works |
|---|---------|-------------|
| 1 | Multi-user Authentication | bcrypt hashed passwords, admin/staff roles |
| 2 | Product CRUD | Add, edit, delete, search products with SQLite |
| 3 | Barcode Generation | SHA-256 hash → 12-char code → Code128 barcode image |
| 4 | QR Code Generation | Product barcode data → QR code image via qrcode library |
| 5 | Barcode/QR Scanning | OpenCV camera + pyzbar decoder (also supports image file) |
| 6 | Automated Billing | Auto-calculate subtotal, discount, GST, grand total |
| 7 | PDF Invoice | ReportLab generates professional PDF with tables |
| 8 | WhatsApp Integration | Formats bill as text → opens WhatsApp Web link |
| 9 | UPI QR Payment | Generates UPI deep link QR code for quick payment |
| 10 | Inventory Tracking | Auto stock deduction on sale + stock movement logs |
| 11 | Low Stock Alerts | Dashboard highlights products with stock ≤ 10 |
| 12 | Expiry Tracking | Blocks expired products, warns for soon-expiring |
| 13 | Sales Charts | Matplotlib bar/line charts embedded in Tkinter |
| 14 | Profit Analysis | Calculates profit per invoice (selling - cost price) |
| 15 | CSV Export | Export sales data as CSV for Excel |
| 16 | Backup/Restore | Copy SQLite file for backup, restore by replacing |
| 17 | Beep on Scan | Windows sound feedback on product selection |

---

## 7. APPLICATION FLOW

```
App Start (app.py)
    │
    ▼
Login Screen ──── Wrong credentials ──→ Show error
    │
    ▼ (Correct credentials)
Main Menu Screen
    │
    ├── 📊 Dashboard ──→ Stats, Charts, Alerts
    ├── 📦 Products ──→ Add/Edit/Delete/Search Products
    ├── 💳 Billing ──→ Create Invoice → Generate PDF / WhatsApp / UPI QR
    ├── 📈 Reports ──→ Sales/Profit Charts, CSV Export
    └── ⚙️ Settings ──→ Password, Users, Backup/Restore
```

### Billing Flow (Most Important):
```
Select Product (dropdown or scan) → Enter Qty → Add Item
    ↓
Items appear in invoice table → Totals auto-calculated
    ↓
Click "Finalize & Save"
    ↓
├── Stock quantity reduced in products table
├── Stock movement recorded in stock_movements table
├── Invoice saved in invoices table
└── Bill items saved in bill_items table
    ↓
Optionally: Generate PDF / Send WhatsApp / Show UPI QR
```

---

## 8. SECURITY FEATURES

1. **Password Hashing**: Uses bcrypt with random salt (not plain text or MD5)
2. **Role-Based Access**: Admin can manage users; Staff can only do billing
3. **Login Required**: No access to any feature without authentication
4. **Double Confirmation**: Dangerous actions (delete data) require 2 confirmations
5. **SQL Injection Prevention**: Uses parameterized queries (`?` placeholders), NOT string concatenation
6. **Foreign Keys**: Database enforces referential integrity

---

## 9. EXPECTED VIVA QUESTIONS & ANSWERS

### General Questions

**Q1: What is the objective of your project?**
> To develop a desktop-based Smart Retail Billing System that automates product management, invoice generation, inventory tracking, and sales analytics for small and medium retail shops.

**Q2: What programming language and why?**
> Python 3.10. It has rich library support for GUI (Tkinter), database (sqlite3), PDF generation (ReportLab), image processing (Pillow), and barcode handling — all needed in this project.

**Q3: What is the database used?**
> SQLite — a lightweight, serverless, file-based relational database. The entire database is stored in one file (`pos_database.sqlite`). No separate database server installation needed.

**Q4: Why SQLite instead of MySQL?**
> SQLite is ideal for desktop applications because: (1) No server setup required, (2) Zero configuration, (3) Single file storage — easy to backup/distribute, (4) Comes built-in with Python.

**Q5: What is Tkinter?**
> Tkinter is Python's standard GUI toolkit. It comes built-in with Python. We use `ttk` (themed Tkinter) for modern-looking widgets like buttons, tables, and dropdown menus.

### Technical Questions

**Q6: How do you store passwords?**
> Using **bcrypt** hashing with automatic salting. The original password is never stored. During login, `bcrypt.checkpw()` compares the entered password against the stored hash.

**Q7: What is bcrypt?**
> bcrypt is a password hashing function designed to be slow (computationally expensive) to resist brute-force attacks. It automatically generates a random salt for each password.

**Q8: How does barcode scanning work?**
> We use OpenCV to capture camera frames, then pyzbar library decodes the barcode/QR code from the image. The decoded string is matched against the product's barcode field in the database.

**Q9: How is GST calculated?**
> GST is calculated on the taxable amount (subtotal minus discount). Formula: `GST = (Subtotal - Discount) × GST_Rate / 100`. Supported rates: 0%, 5%, 12%, 18%.

**Q10: How do you generate PDF invoices?**
> Using the ReportLab library. We create a `SimpleDocTemplate`, add header paragraphs, item tables with styled rows, totals section, and footer — then build the PDF document.

**Q11: What is the difference between Code128 and QR Code?**
> **Code128** is a 1D linear barcode — stores only text/numbers in horizontal bars. **QR Code** is a 2D code — stores more data, can be scanned from any angle, and works better with phone cameras.

**Q12: How do you prevent SQL injection?**
> We use **parameterized queries** with `?` placeholders: `cursor.execute('SELECT * FROM users WHERE username=?', (username,))`. The database engine escapes special characters automatically.

**Q13: What design pattern is used?**
> MVC-like architecture. **Model** = data classes in `models.py`. **View** = GUI screens in `gui/` folder. **Controller** = business logic in `utils/` folder.

**Q14: How does the stock management work?**
> When an invoice is finalized: (1) Product stock_quantity is reduced by the sold quantity, (2) A StockMovement record is created with type "SALE" and negative quantity, linking to the invoice.

**Q15: How does WhatsApp integration work?**
> We format the bill as a text message, URL-encode it, and open `https://wa.me/{phone}?text={encoded_message}` in the browser. WhatsApp Web opens with the pre-filled message.

**Q16: How does UPI QR code work?**
> We construct a UPI deep link: `upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR`, then generate a QR code image from it using the qrcode library. Any UPI app can scan this.

**Q17: What happens if the camera is not available for scanning?**
> The system falls back to a file picker dialog where the user can select a barcode/QR code image file from their computer. pyzbar decodes the image file.

**Q18: How is data backup done?**
> The SQLite database file is simply copied to a `data/backups/` folder with a timestamped name. To restore, the backup file is copied back as the main database.

**Q19: What is the role-based access control?**
> Two roles: **Admin** (full access — can manage users, delete data, change settings) and **Staff** (can only do billing, view products and reports). The User Management tab only appears for admins.

**Q20: How do you handle expired products?**
> During billing, the system checks each product's expiry date. **Expired products are blocked** from being billed. Products expiring within 2 days show a warning. The dashboard shows all items expiring within 30 days.

### Database Questions

**Q21: How many tables are in the database?**
> 6 tables: products, invoices, bill_items, customers, users, stock_movements.

**Q22: What is the primary key of each table?**
> products: product_id, invoices: invoice_id, bill_items: id (auto-increment), users: user_id, customers: customer_id, stock_movements: movement_id.

**Q23: What foreign key exists?**
> `bill_items.invoice_id` references `invoices.invoice_id` with ON DELETE CASCADE — deleting an invoice automatically deletes its bill items.

**Q24: What is a dataclass in Python?**
> A `@dataclass` decorator automatically generates `__init__`, `__repr__`, and other methods for a class. We use it for Product, Invoice, User, etc. to reduce boilerplate code.

### Software Engineering Questions

**Q25: What is the SDLC model used?**
> Incremental/Iterative model. We built the core features first (login, products, billing), then added advanced features (barcode, PDF, charts, WhatsApp) in iterations.

**Q26: What are the functional requirements?**
> User authentication, product CRUD, invoice creation, GST calculation, PDF generation, barcode/QR scanning, inventory tracking, sales reporting, data backup.

**Q27: What are the non-functional requirements?**
> Fast response time, user-friendly interface, data security (bcrypt), reliability (SQLite ACID compliance), portability (runs on Windows/Mac/Linux).

**Q28: What testing was done?**
> Unit testing for billing calculations, integration testing for database CRUD operations, and manual UI testing for all screens and user flows.

**Q29: What are the system requirements?**
> Python 3.10+, Windows/Mac/Linux, 4GB RAM minimum, webcam (optional for barcode scanning), ~50MB disk space.

**Q30: Future enhancements?**
> Cloud database sync, mobile app, email invoices, customer loyalty programs, multi-branch support, GST return report generation, purchase order management.

---

## 10. HOW TO DEMONSTRATE

### Demo Flow (Follow this order):

**Step 1 — Login:** Show login screen → Login with admin/admin123

**Step 2 — Dashboard:** Click Dashboard → Show stats, charts, low stock, expiry alerts

**Step 3 — Add Product:** Click Products → Add Product → Fill details → Generate barcode → Save

**Step 4 — Billing:**
- Click Billing → Select product from dropdown → Add item
- Show GST calculation and totals
- Click "Generate PDF" → Show the PDF invoice
- Click "Display UPI QR" → Show payment QR code

**Step 5 — Scan (if asked):**
- Click "Scan Barcode/QR" → Show camera or select barcode image from `barcodes/` folder

**Step 6 — Reports:** Click Reports → Show sales chart, profit chart, summary

**Step 7 — Settings:** Click Settings → Show user management (admin only), backup feature

**Step 8 — Security:** Mention bcrypt hashing, role-based access, parameterized queries

---

## 11. KEY LIBRARIES QUICK REFERENCE

| Library | Import | Purpose |
|---------|--------|---------|
| tkinter | `import tkinter as tk` | GUI windows, buttons, labels |
| ttk | `from tkinter import ttk` | Themed modern widgets |
| sqlite3 | `import sqlite3` | Database operations |
| bcrypt | `import bcrypt` | Password hashing |
| reportlab | `from reportlab.platypus import ...` | PDF generation |
| matplotlib | `import matplotlib.pyplot as plt` | Charts and graphs |
| cv2 | `import cv2` | Camera access for scanning |
| pyzbar | `from pyzbar import pyzbar` | Decode barcode/QR from image |
| qrcode | `import qrcode` | Generate QR code images |
| barcode | `import barcode` | Generate barcode images |
| Pillow | `from PIL import Image` | Image processing |

---

> **Good luck with your presentation! 🎯**
> Remember: Speak confidently, show the working demo first, then explain the code if asked.
