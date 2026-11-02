# 🎓 MCA 1st Semester Mini Project Viva & Technical Guide

### Project Title: Restaurant & Café Management System
**Technologies**: Python Flask, MySQL, Bootstrap 5, HTML5/CSS3/JavaScript  
**Target Examination**: MCA 1st Semester Mini Project Practical Viva

---

## 📌 1. Project High-Level Architecture (MVC Pattern)

This project follows the industry-standard **Model-View-Controller (MVC)** architectural pattern:

```text
       ┌────────────────────────────────────────────────────────┐
       │                        BROWSER                         │
       │     (HTML5, CSS3, JavaScript, Bootstrap 5 UI)          │
       └─────────────────────────┬──────────────────────────────┘
                                 │ HTTP Requests (GET / POST)
                                 ▼
       ┌────────────────────────────────────────────────────────┐
       │                       CONTROLLER                       │
       │            Flask Application Routes (app.py)           │
       │    - Form validation & Session auth decorators         │
       │    - Business logic (Cart calculations, GST tax)       │
       └──────────────┬───────────────────────────▲─────────────┘
                      │                           │
        Queries/Updates                           │ Data Records
                      ▼                           │
       ┌────────────────────────┐       ┌────────────────────────┐
       │         MODEL          │       │          VIEW          │
       │  MySQL (restaurant_db) │       │ Jinja2 HTML Templates  │
       │  Tables & Constraints  │       │ (templates/*.html)     │
       └────────────────────────┘       └────────────────────────┘
```

1. **Model (Data Layer)**: 
   - MySQL database `restaurant_db` containing 9 relational tables.
   - Handles data integrity, foreign key cascades (`ON DELETE CASCADE`), and constraints.
2. **View (Presentation Layer)**:
   - Jinja2 template engine rendering responsive HTML5 templates with Bootstrap 5.
   - Dynamic injection of café configuration, cart items, customer name, and bill totals.
3. **Controller (Application Logic)**:
   - Python Flask routes inside `app.py` responding to client HTTP requests.
   - Implements authentication decorators (`@login_required`, `@admin_required`).

---

## 📊 2. Entity-Relationship (ER) Diagram Walkthrough

```text
   +-------------------+          +------------------+
   |    CATEGORIES     | 1      N |    MENU_ITEMS    |
   |-------------------|----------|------------------|
   | PK id             |          | PK id            |
   |    name           |          | FK category_id   |
   |    slug           |          |    name          |
   +-------------------+          |    price         |
                                  |    is_veg        |
                                  |    is_available  |
                                  +--------+---------+
                                           | 1
                                           |
                                           | N
   +-------------------+          +--------+---------+          +-------------------+
   |       USERS       | 1      N |   ORDER_ITEMS    | N      1 |      ORDERS       |
   |-------------------|----------|------------------|----------|-------------------|
   | PK id             |          | PK id            |          | PK id             |
   |    full_name      |          | FK order_id      |          |    order_number   |
   |    email (UNIQUE) |          | FK menu_item_id  |          | FK user_id        |
   |    phone          |          |    unit_price    |          |    subtotal       |
   |    password_hash  |          |    quantity      |          |    tax_amount     |
   |    role           |          |    subtotal      |          |    total_amount   |
   +--------+----------+          +------------------+          |    status         |
            | 1                                                 +-------------------+
            |
            | N
   +--------+----------+          +-------------------+
   |   RESERVATIONS    | N      1 | RESTAURANT_TABLES |
   |-------------------|----------|------------------|
   | PK id             |          | PK id            |
   | FK user_id        |          |    table_number  |
   | FK table_id       |          |    capacity      |
   |    reservation_dt |          |    location      |
   |    reservation_tm |          |    status        |
   |    status         |          +-------------------+
   +-------------------+
```

### Table Relationships:
- **`categories` to `menu_items` (1 : N)**: One food category contains multiple dishes. Deleting a category cascades to delete associated items.
- **`users` to `orders` (1 : N)**: One customer can place many orders. If a customer is removed, past order history is preserved via `ON DELETE SET NULL`.
- **`orders` to `order_items` (1 : N)**: One order has multiple item lines. Deleting an order cascades to remove item rows.
- **`restaurant_tables` to `reservations` (1 : N)**: Each table can have multiple date/time reservations.

---

## 🛡️ 3. Database Normalization (1NF to 3NF)

- **1NF (First Normal Form)**:
  - All attributes are atomic (no comma-separated items inside a single column). Order line items are separated into their own table (`order_items`).
- **2NF (Second Normal Form)**:
  - In 1NF and all non-key attributes are fully functionally dependent on the entire primary key (no partial dependencies).
- **3NF (Third Normal Form)**:
  - In 2NF and no transitive dependencies exist. For example, `category_name` is not stored in `menu_items`; only `category_id` foreign key is stored.

---

## 🔒 4. Key Security & Implementation Concepts

### A. Preventing SQL Injection:
- **Flawed approach**: `cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")` (Vulnerable to `' OR '1'='1`).
- **Our implementation**: Parameterized queries using placeholders:
  ```python
  cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
  ```
  The database driver escapes input values separately from the SQL command structure, rendering injection attempts harmless.

### B. Password Hashing (Werkzeug `scrypt`):
- Plain-text passwords are never written to the database.
- `generate_password_hash(password)` computes a one-way cryptographic hash with random salt.
- During login, `check_password_hash(stored_hash, submitted_password)` validates the password without ever needing to decrypt it.

### C. Session Management & Role-Based Access:
- Flask signs session cookies using `Config.SECRET_KEY` cryptographically.
- Custom decorators `@login_required` and `@admin_required` inspect `session['user_id']` and `session['user_role']`. Unauthorized access attempts are immediately aborted or redirected.

### D. Conflict-Free Table Reservation Logic:
```python
conflict = db.query_db("""
    SELECT id FROM reservations 
    WHERE table_id = %s 
      AND reservation_date = %s 
      AND reservation_time = %s 
      AND status IN ('pending', 'confirmed')
""", (table_id, reservation_date, reservation_time), one=True)

if conflict:
    # Reject booking and alert user
```

---

## 🗣️ 5. Top 25 Viva Questions & Examiner Answers

#### Q1: What is the main objective of this project?
**Answer**: To build an end-to-end, full-stack Restaurant and Café Management System that allows customers to browse categorized dishes, manage an interactive shopping cart, book dining tables without scheduling conflicts, and generate printable tax invoices. It simultaneously provides administrators with a secure panel for menu management, order fulfillment, and sales reports.

#### Q2: Why did you choose Python Flask instead of Django?
**Answer**: Flask is a lightweight micro-framework that provides explicit control over routes, sessions, and database connections. For a 1st Semester MCA project, Flask allows us to understand every fundamental layer of web development (routing, WSGI, templating, sessions) without the heavy hidden boilerplate of Django.

#### Q3: How does your application connect to MySQL?
**Answer**: We use the official `mysql-connector-python` library. A database helper module (`db.py`) manages connections, executes parameterized queries via dictionary cursors, and commits transactions.

#### Q4: What happens if MySQL is not running during the viva demonstration?
**Answer**: We engineered an automatic fallback mechanism in `db.py`. If MySQL is unreachable, the system detects this and smoothly switches to SQLite (`restaurant.db`) with identical schema, seed data, and feature parity, ensuring zero downtime.

#### Q5: How is user authentication maintained across different pages?
**Answer**: Using **Flask Sessions**. When a user logs in, their `user_id`, `user_name`, and `user_role` are stored in Flask's session object, which is encrypted and transmitted via secure HTTP cookies.

#### Q6: How do you prevent unauthorized users from opening admin pages?
**Answer**: We use a custom Python decorator `@admin_required`. Before any admin route executes, this decorator verifies that `session.get('user_role') == 'admin'`. If not, it redirects the user with an access denied message.

#### Q7: How does the shopping cart work without a database insert for every click?
**Answer**: The cart is stored in the user's **Flask Session** (`session['cart']`). This reduces database load while browsing. The database is only updated when the customer officially clicks "Confirm & Place Order", which writes the records to the `orders` and `order_items` tables.

#### Q8: How is the tax calculated in the billing module?
**Answer**: Tax is calculated dynamically in `app.py` based on `Config.TAX_RATE_PERCENTAGE` (default 5.0% for GST):
`tax_amount = round(subtotal * (TAX_RATE_PERCENTAGE / 100.0), 2)`.

#### Q9: How do you handle delivery fees?
**Answer**: Orders with order type `delivery` incur a standard delivery fee (e.g., ₹40). However, if `subtotal >= Config.FREE_DELIVERY_THRESHOLD` (₹500), the delivery fee is automatically set to ₹0.00 (FREE).

#### Q10: How do you prevent overlapping table reservations?
**Answer**: When a booking request is submitted, a SELECT query checks if a reservation already exists for the requested `table_id`, `reservation_date`, and `reservation_time` with status 'pending' or 'confirmed'. If a record exists, the reservation is rejected with an informative error message.

#### Q11: How do you generate unique order IDs?
**Answer**: We format the ID using the current date and a cryptographically pseudorandom suffix: `f"ORD-{YYYYMMDD}-{random_4_digits}"` (e.g. `ORD-20261102-4821`).

#### Q12: How is the printable invoice created?
**Answer**: In `invoice.html`, we use CSS `@media print` rules. When `window.print()` is called, the navigation bar, footer, and buttons are hidden (`display: none !important`), leaving only a clean, professional receipt.

#### Q13: What is the difference between GET and POST HTTP methods in your project?
**Answer**: 
- `GET` is used to retrieve and render data without modifying state (e.g., loading `/menu`, `/cart`, `/admin/sales`).
- `POST` is used to submit sensitive data or modify server state (e.g., `/login`, `/cart/add/<id>`, `/order/place`).

#### Q14: What is Jinja2 and how is it used here?
**Answer**: Jinja2 is Flask's built-in template engine. It allows dynamic data injection into HTML files using `{{ variable }}` syntax, conditionals (`{% if %}`), loops (`{% for %}`), and template inheritance (`{% extends 'base.html' %}`).

#### Q15: What is the purpose of `base.html`?
**Answer**: `base.html` implements the DRY (Don't Repeat Yourself) principle. It defines the master page skeleton (HTML head, navbar, flash alert container, footer) which child templates extend using `{% block content %}`.

#### Q16: How are flash messages handled?
**Answer**: Flask's `flash()` function stores a temporary message in the session. On the subsequent HTTP response, `get_flashed_messages(with_categories=True)` in `base.html` renders it as an alert, and `script.js` automatically dismisses it after 5 seconds.

#### Q17: What is an index in MySQL and where would you apply it in this project?
**Answer**: An index speeds up data retrieval on frequently queried columns. We indexed `orders(order_number)`, `users(email)`, and foreign key columns (`category_id`, `order_id`, `table_id`).

#### Q18: What is Referential Integrity?
**Answer**: Referential integrity ensures that relationships between tables remain consistent. For instance, in `order_items`, `FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE` ensures that if an order is deleted, all its line items are automatically removed.

#### Q19: What is `autocommit` in database transactions?
**Answer**: By default, transactions should be committed explicitly via `conn.commit()` so that if an error occurs while writing `order_items`, the transaction can be rolled back via `conn.rollback()`, ensuring atomicity.

#### Q20: How did you implement client-side live search on the menu?
**Answer**: In `script.js`, an `input` event listener reads the search input value and compares it against `data-name` and `data-desc` attributes of each dish element, toggling `item.style.display = 'block' | 'none'` in real time without refreshing the page.

#### Q21: What are the dietary indicators used in the menu?
**Answer**: We adhere to the standard green circle in a square for Vegetarian items and a red circle in a square for Non-Vegetarian items, styled with custom CSS (`.food-type-icon.veg` and `.food-type-icon.non-veg`).

#### Q22: What role does `config.py` play in this project?
**Answer**: It centralizes configuration parameters such as database credentials, secret keys, restaurant branding, tax percentages, and delivery fees. If the business changes its tax rate or email address, only `config.py` needs to be edited.

#### Q23: How are passwords stored and checked in your system?
**Answer**: We use Werkzeug's `generate_password_hash()` which generates a salted `scrypt` hash. During login, `check_password_hash()` compares the submitted string against the stored hash.

#### Q24: What is the difference between 404 and 500 error codes?
**Answer**: 
- `404 Not Found`: Client requested a non-existent URL (handled by `@app.errorhandler(404)`).
- `500 Internal Server Error`: Unhandled server-side exception occurred (handled by `@app.errorhandler(500)`).

#### Q25: What future enhancements could be added to this system?
**Answer**: 
1. Real-time kitchen display screen using WebSockets.
2. Integration with payment gateway APIs (Razorpay / Stripe).
3. SMS / WhatsApp notification alerts for order status.
4. AI-based dish recommendation based on previous customer orders.

