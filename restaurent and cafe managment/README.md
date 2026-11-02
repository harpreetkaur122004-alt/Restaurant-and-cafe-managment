# 🍽️ Restaurant & Café Management System

A modern, responsive, full-stack web application designed and built for **MCA 1st Semester Mini Project** using **Python Flask**, **MySQL**, **Bootstrap 5**, and **Vanilla JavaScript**.

---

## 📋 1. Project Overview

The **Restaurant & Café Management System** is a dynamic hospitality platform that enables café patrons to browse an appetizing multi-category menu, place custom dine-in/takeaway/delivery food orders, reserve tables with automated collision prevention, and obtain printable GST-compliant invoices. 

Concurrently, it provides café owners and managers with a secure, role-protected **Admin Panel** to manage dishes, fulfill customer orders, confirm/cancel table reservations, inspect customer lifetime value, and analyze gross sales analytics.

### Key Highlights:
- **Zero Framework Bloat**: Pure Flask + HTML5/CSS3/JavaScript + MySQL Connector.
- **Dual Database Flexibility**: Works natively with **MySQL** (`restaurant_db`), and includes a zero-config SQLite automatic fallback (`restaurant.db`) so the application never fails during viva demonstrations if MySQL is stopped.
- **Parametric SQL & Secure Auth**: Werkzeug `scrypt` password hashing and 100% parameterized queries preventing SQL Injection.
- **Real-Time Features**: Live client-side menu search, veg/non-veg filter pills, conflict-free table booking, and printable tax receipts.

---

## 💻 2. System Requirements

### Software Requirements:
- **Operating System**: Windows 10/11, Linux (Ubuntu/Debian), or macOS.
- **Python**: Python 3.8 to Python 3.14.
- **Database Server**: MySQL 5.7+ / MySQL 8.0+ / MariaDB (or XAMPP / WampServer).
- **Code Editor**: Visual Studio Code (VS Code) or PyCharm.
- **Web Browser**: Google Chrome, Mozilla Firefox, Microsoft Edge, or Safari.

### Hardware Requirements:
- **Processor**: Intel Core i3 / AMD Ryzen 3 or higher.
- **RAM**: Minimum 4 GB (8 GB recommended).
- **Disk Storage**: At least 500 MB free disk space.

---

## 📁 3. Folder & File Structure

```text
restaurent and cafe managment/
│
├── app.py                      # Core Flask Application & Route Controllers
├── config.py                   # Central Application Configuration & Tax Settings
├── db.py                       # Database Abstraction (MySQL + SQLite Fallback)
├── init_db.py                  # One-Click Database Seeding & Setup Script
├── test_app.py                 # Automated Unit & Integration Test Suite
├── database.sql                # Complete MySQL Schema, Constraints & Seed Data
├── requirements.txt            # Python Package Dependencies
├── README.md                   # Complete Setup & Project Guide
├── MCA_VIVA_GUIDE.md           # MCA Viva Preparation & Interview Questions
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Master Layout (Navbar, Flash Alerts, Footer)
│   ├── index.html              # Home Landing Page (Hero, Featured Dishes, Reviews)
│   ├── login.html              # User & Admin Login Portal
│   ├── register.html           # Customer Registration Form
│   ├── menu.html               # Menu with Category Pills, Search & Diet Filter
│   ├── cart.html               # Interactive Shopping Basket & Bill Summary
│   ├── checkout.html           # Checkout, Address, Dining Type & Payment Method
│   ├── order_confirmation.html # Order Placed Banner & Reference ID
│   ├── invoice.html            # Printable Official Tax Invoice
│   ├── reservations.html       # Conflict-Free Table Booking Form
│   ├── my_orders.html          # Customer Past Order History & Status
│   ├── contact.html            # Contact Inquiries & Feedback Form
│   └── admin/                  # Protected Admin Views
│       ├── base_admin.html     # Admin Sidebar Layout
│       ├── dashboard.html      # KPI Cards, Live Order Status & Bookings
│       ├── menu_management.html# Add, Edit, Delete & Toggle Dishes
│       ├── orders.html         # Order Fulfillment & Filtering
│       ├── reservations.html   # Table Booking Approvals
│       ├── customers.html      # Registered Customers & Total Spend
│       ├── sales_reports.html  # Revenue Analytics & Bestsellers
│       └── messages.html       # Customer Contact Inquiries
│
└── static/                     # Static Web Assets
    ├── css/
    │   └── style.css           # Café Theme CSS (Warm Brown, Amber & Cream)
    ├── js/
    │   └── script.js           # Client-side Search, Validation & Alerts
    └── images/                 # Restaurant Logo & Food Vectors
        ├── logo.svg
        └── default_food.svg
```

---

## 🗄️ 4. Database Architecture (`restaurant_db`)

The database consists of **9 relational tables** designed with proper primary keys, foreign keys, and referential constraints:

1. **`users`**: Customer and administrator credentials with hashed passwords and saved addresses.
2. **`categories`**: Menu categories (Breakfast, Starters, Main Course, Pizza & Burgers, Coffee & Tea, Cold Drinks, Desserts).
3. **`menu_items`**: Dish catalog with price, category relationship, diet indicator (veg/non-veg), stock status, and image URLs.
4. **`restaurant_tables`**: Dining capacity, table codes (T-01 to T-08), and dining zones (Window, Patio, Hall).
5. **`reservations`**: Guest reservation records with table foreign key, date, time slot, and conflict safeguards.
6. **`orders`**: Customer transactions, unique alphanumeric order number, fulfillment status, subtotal, 5% GST, and delivery fees.
7. **`order_items`**: Line items mapped to order IDs and menu item IDs with unit prices and quantities.
8. **`contact_messages`**: Visitor inquiries, subject lines, phone numbers, and read status.
9. **`reviews`**: Customer testimonials, ratings (1-5 stars), and moderation approval flag.

---

## 🚀 5. Quick Start & Installation

### Step 1: Open the Project Directory
Open **VS Code**, click `File` -> `Open Folder...`, and select:
```text
D:\restaurent and cafe managment
```

### Step 2: Install Python Dependencies
Open the VS Code Terminal (`Ctrl + ` `~` or `Terminal -> New Terminal`) and run:
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database

#### Option A: Running with MySQL (Standard MCA Submission)
1. Start your MySQL service (e.g. start **Apache & MySQL** from **XAMPP Control Panel** or start MySQL Windows Service).
2. If your MySQL root user has a password, open `config.py` and set:
   ```python
   DB_PASSWORD = 'your_mysql_password'
   ```
3. Run the automated database initializer:
   ```bash
   python init_db.py
   ```
   *This automatically creates `restaurant_db` and seeds all sample categories, 26 delicious food items, 8 tables, demo accounts, and reviews.*

#### Option B: Zero-Config Standalone Demo (Instant)
If MySQL is not installed on the exam machine, no problem! `init_db.py` automatically initializes `restaurant.db` (SQLite) with identical tables and seed data. Simply run:
```bash
python init_db.py
```

### Step 4: Run the Flask Web Application
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🔑 6. Default Demo Credentials

| Role | Email Address | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@restaurant.com` | `admin123` | Full Admin Panel, Menu CRUD, Status Updates, Sales Reports |
| **Customer** | `customer@gmail.com` | `customer123` | Ordering, Cart, Table Booking, Past Order History & Invoices |

*(You can also register brand-new customer accounts directly via the Sign Up page).*

---

## 🧪 7. Automated Testing

To verify all routes, cart calculations, orders, conflict checks, and admin protections, run the automated test suite:
```bash
python test_app.py
```
**Expected Output:**
```text
[PASS] Test 01: Home page loads with featured dishes and reviews.
[PASS] Test 02: Menu page & category filtering work.
[PASS] Test 03: Cart add, increment, and tax calculation work.
[PASS] Test 04: Customer login and order history work.
[PASS] Test 05: Order placement, unique ID generation, and invoice work.
[PASS] Test 06: Reservation conflict prevention verified.
[PASS] Test 07: Admin security, dashboard KPI, and sales reports verified.
Ran 7 tests in 0.896s
OK
```

---

## ⚙️ 8. Configuration Settings (`config.py`)

All key restaurant business parameters can be modified inside `config.py`:
- `RESTAURANT_NAME`: Café display name.
- `CURRENCY_SYMBOL`: Default `₹` (Indian Rupee), easily changed to `$`, `€`, or `£`.
- `TAX_RATE_PERCENTAGE`: Tax percentage applied to bills (default: `5.0` for 5% GST).
- `DELIVERY_FEE`: Flat shipping charge (default: `40.00`).
- `FREE_DELIVERY_THRESHOLD`: Free delivery on orders over this amount (default: `500.00`).

---

## 🛠️ 9. Troubleshooting Common Errors

1. **Port 5000 Already in Use**:
   - If port 5000 is occupied by another app, open `app.py` and change the bottom line to:
     ```python
     app.run(debug=True, host='127.0.0.1', port=5001)
     ```
2. **Access Denied for MySQL user 'root'@'localhost'**:
   - Ensure the password in `config.py` matches your local MySQL root password. In XAMPP, default password is empty (`''`).
3. **ModuleNotFoundError**:
   - Run `python -m pip install -r requirements.txt`.

