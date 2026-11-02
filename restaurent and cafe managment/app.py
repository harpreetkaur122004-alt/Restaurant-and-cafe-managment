"""
============================================================
RESTAURANT & CAFÉ MANAGEMENT SYSTEM
Main Flask Application Controller (app.py)
Developed for MCA 1st Semester Mini Project
============================================================
"""
from flask import (
    Flask, render_template, request, redirect, 
    url_for, session, flash, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import random
import os

from config import Config
import db

app = Flask(__name__)
app.config.from_object(Config)


# ============================================================
# CONTEXT PROCESSORS & TEMPLATE HELPERS
# ============================================================
@app.context_processor
def inject_global_data():
    """Injects configuration and cart count into all Jinja templates."""
    cart = session.get('cart', {})
    cart_count = sum(item.get('quantity', 1) for item in cart.values())
    session['cart_count'] = cart_count
    return {
        'config': Config,
        'cart_count': cart_count,
        'current_year': datetime.datetime.now().year
    }


# ============================================================
# AUTHENTICATION DECORATORS
# ============================================================
def login_required(f):
    """Ensures user is logged in before accessing protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Ensures user is an authenticated administrator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Admin authentication required. Please log in.', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# PUBLIC & CUSTOMER ROUTES
# ============================================================

@app.route('/')
def index():
    """Home landing page with hero banner, about, featured dishes, and customer reviews."""
    try:
        # Fetch featured menu items
        featured_items = db.query_db("""
            SELECT m.*, c.name AS category_name 
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            WHERE m.is_featured = 1 AND m.is_available = 1
            LIMIT 4
        """)
        
        # If no featured items marked, fallback to first 4 available items
        if not featured_items:
            featured_items = db.query_db("""
                SELECT m.*, c.name AS category_name 
                FROM menu_items m
                JOIN categories c ON m.category_id = c.id
                WHERE m.is_available = 1
                LIMIT 4
            """)

        # Fetch approved reviews
        reviews = db.query_db("""
            SELECT customer_name, rating, comment 
            FROM reviews 
            WHERE is_approved = 1 
            ORDER BY id DESC LIMIT 3
        """)
        
        return render_template('index.html', featured_items=featured_items, reviews=reviews)
    except Exception as e:
        flash(f"Error loading homepage content: {e}", "danger")
        return render_template('index.html', featured_items=[], reviews=[])


@app.route('/menu')
def menu():
    """Menu display page with categories, dietary filters, and live search."""
    category_slug = request.args.get('category')
    
    categories = db.query_db("SELECT * FROM categories ORDER BY display_order ASC")
    
    if category_slug:
        items = db.query_db("""
            SELECT m.*, c.name AS category_name, c.slug AS category_slug
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            WHERE c.slug = %s
            ORDER BY m.id ASC
        """, (category_slug,))
    else:
        items = db.query_db("""
            SELECT m.*, c.name AS category_name, c.slug AS category_slug
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            ORDER BY m.category_id ASC, m.id ASC
        """)
        
    return render_template(
        'menu.html', 
        categories=categories, 
        items=items, 
        selected_category=category_slug
    )


# ============================================================
# SHOPPING CART CONTROLLER
# ============================================================

@app.route('/cart')
def view_cart():
    """Displays cart items, subtotal, configurable tax, delivery fee, and grand total."""
    cart = session.get('cart', {})
    cart_items = []
    subtotal = 0.0

    for item_id_str, details in cart.items():
        qty = details.get('quantity', 1)
        price = float(details.get('price', 0.0))
        item_total = price * qty
        subtotal += item_total
        cart_items.append({
            'id': int(item_id_str),
            'name': details.get('name'),
            'price': price,
            'quantity': qty,
            'category_name': details.get('category_name', ''),
            'image_url': details.get('image_url', '/static/images/default_food.svg'),
            'total_price': item_total
        })

    # Tax & delivery calculation
    tax_amount = round(subtotal * (Config.TAX_RATE_PERCENTAGE / 100.0), 2)
    delivery_fee = 0.0 if (subtotal >= Config.FREE_DELIVERY_THRESHOLD or subtotal == 0) else Config.DELIVERY_FEE
    grand_total = round(subtotal + tax_amount + delivery_fee, 2)

    return render_template(
        'cart.html',
        cart_items=cart_items,
        subtotal=subtotal,
        tax_amount=tax_amount,
        delivery_fee=delivery_fee,
        grand_total=grand_total
    )


@app.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    """Adds a dish to the customer session cart."""
    item = db.query_db("""
        SELECT m.*, c.name AS category_name 
        FROM menu_items m
        JOIN categories c ON m.category_id = c.id
        WHERE m.id = %s
    """, (item_id,), one=True)

    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for('menu'))

    if not item['is_available']:
        flash(f"Sorry, {item['name']} is currently out of stock.", "warning")
        return redirect(url_for('menu'))

    cart = session.get('cart', {})
    item_key = str(item_id)

    if item_key in cart:
        cart[item_key]['quantity'] += 1
    else:
        cart[item_key] = {
            'name': item['name'],
            'price': float(item['price']),
            'quantity': 1,
            'category_name': item['category_name'],
            'image_url': item['image_url']
        }

    session['cart'] = cart
    session.modified = True
    flash(f"Added {item['name']} to your cart!", "success")

    # Return to previous page or cart
    return_url = request.form.get('return_url')
    if return_url:
        return redirect(return_url)
    return redirect(url_for('view_cart'))


@app.route('/cart/update/<int:item_id>/<action>', methods=['POST'])
def update_cart_quantity(item_id, action):
    """Increments or decrements item quantity in cart."""
    cart = session.get('cart', {})
    item_key = str(item_id)

    if item_key in cart:
        if action == 'increase':
            cart[item_key]['quantity'] += 1
        elif action == 'decrease':
            cart[item_key]['quantity'] -= 1
            if cart[item_key]['quantity'] <= 0:
                del cart[item_key]

        session['cart'] = cart
        session.modified = True

    return redirect(url_for('view_cart'))


@app.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    """Removes an item completely from cart."""
    cart = session.get('cart', {})
    item_key = str(item_id)

    if item_key in cart:
        name = cart[item_key]['name']
        del cart[item_key]
        session['cart'] = cart
        session.modified = True
        flash(f"Removed {name} from your cart.", "info")

    return redirect(url_for('view_cart'))


@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Clears all items from cart."""
    session['cart'] = {}
    session.modified = True
    flash("Your cart has been cleared.", "info")
    return redirect(url_for('view_cart'))


# ============================================================
# CHECKOUT & ORDER PLACEMENT
# ============================================================

@app.route('/checkout')
def checkout():
    """Checkout page to enter delivery/dine-in details and payment choice."""
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty. Please add items before checking out.", "warning")
        return redirect(url_for('menu'))

    cart_items = []
    subtotal = 0.0
    for item_id_str, details in cart.items():
        qty = details.get('quantity', 1)
        price = float(details.get('price', 0.0))
        item_total = price * qty
        subtotal += item_total
        cart_items.append({
            'name': details.get('name'),
            'quantity': qty,
            'total_price': item_total
        })

    tax_amount = round(subtotal * (Config.TAX_RATE_PERCENTAGE / 100.0), 2)
    delivery_fee = 0.0 if (subtotal >= Config.FREE_DELIVERY_THRESHOLD or subtotal == 0) else Config.DELIVERY_FEE
    grand_total = round(subtotal + tax_amount + delivery_fee, 2)

    # Fetch user info if logged in
    user = None
    if session.get('user_id'):
        user = db.query_db("SELECT * FROM users WHERE id = %s", (session['user_id'],), one=True)

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        tax_amount=tax_amount,
        delivery_fee=delivery_fee,
        grand_total=grand_total,
        user=user
    )


@app.route('/order/place', methods=['POST'])
def place_order():
    """Processes customer checkout, writes to MySQL orders & order_items tables."""
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('menu'))

    customer_name = request.form.get('customer_name', '').strip()
    customer_phone = request.form.get('customer_phone', '').strip()
    customer_email = request.form.get('customer_email', '').strip()
    order_type = request.form.get('order_type', 'delivery')
    delivery_address = request.form.get('delivery_address', '').strip()
    table_number = request.form.get('table_number', '').strip()
    payment_method = request.form.get('payment_method', 'cash_on_delivery')
    special_notes = request.form.get('special_notes', '').strip()

    if not customer_name or not customer_phone or not customer_email:
        flash("Please provide your name, phone number, and email.", "danger")
        return redirect(url_for('checkout'))

    if order_type == 'delivery' and not delivery_address:
        flash("Please provide a valid delivery address.", "danger")
        return redirect(url_for('checkout'))

    # Calculate financial totals securely on the server
    subtotal = 0.0
    for item_id_str, details in cart.items():
        subtotal += float(details.get('price', 0.0)) * details.get('quantity', 1)

    tax_amount = round(subtotal * (Config.TAX_RATE_PERCENTAGE / 100.0), 2)
    delivery_fee = 0.0 if (subtotal >= Config.FREE_DELIVERY_THRESHOLD or order_type != 'delivery') else Config.DELIVERY_FEE
    grand_total = round(subtotal + tax_amount + delivery_fee, 2)

    # Generate Unique Order Number: ORD-YYYYMMDD-XXXX
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    random_suffix = random.randint(1000, 9999)
    order_number = f"ORD-{date_str}-{random_suffix}"

    user_id = session.get('user_id')

    try:
        # Insert into orders table
        order_insert_sql = """
            INSERT INTO orders (
                order_number, user_id, customer_name, customer_email, customer_phone,
                delivery_address, order_type, table_number, payment_method, payment_status,
                subtotal, tax_amount, delivery_fee, total_amount, status, special_notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        order_id = db.execute_db(order_insert_sql, (
            order_number, user_id, customer_name, customer_email, customer_phone,
            delivery_address, order_type, table_number, payment_method, 'pending',
            subtotal, tax_amount, delivery_fee, grand_total, 'Pending', special_notes
        ))

        # Insert item lines into order_items table
        for item_id_str, details in cart.items():
            menu_item_id = int(item_id_str)
            item_name = details.get('name')
            unit_price = float(details.get('price'))
            qty = int(details.get('quantity', 1))
            line_subtotal = round(unit_price * qty, 2)

            item_sql = """
                INSERT INTO order_items (
                    order_id, menu_item_id, item_name, unit_price, quantity, subtotal
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_db(item_sql, (order_id, menu_item_id, item_name, unit_price, qty, line_subtotal))

        # Clear cart upon success
        session['cart'] = {}
        session.modified = True

        flash("Your order has been placed successfully!", "success")
        return redirect(url_for('order_confirmation', order_id=order_id))

    except Exception as e:
        flash(f"Error processing order: {e}", "danger")
        return redirect(url_for('checkout'))


@app.route('/order/confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Displays order placed banner and breakdown."""
    order = db.query_db("SELECT * FROM orders WHERE id = %s", (order_id,), one=True)
    if not order:
        flash("Order record not found.", "danger")
        return redirect(url_for('index'))

    items = db.query_db("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
    return render_template('order_confirmation.html', order=order, items=items)


@app.route('/invoice/<int:order_id>')
def view_invoice(order_id):
    """Generates official itemized bill / printable invoice."""
    order = db.query_db("SELECT * FROM orders WHERE id = %s", (order_id,), one=True)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('index'))

    # Security check: If logged in as customer, ensure customer owns this order (admins can view all)
    if session.get('user_role') != 'admin' and session.get('user_id'):
        if order.get('user_id') and order['user_id'] != session['user_id']:
            flash("You do not have permission to view this invoice.", "danger")
            return redirect(url_for('my_orders'))

    items = db.query_db("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
    return render_template('invoice.html', order=order, items=items)


# ============================================================
# TABLE RESERVATION SYSTEM
# ============================================================

@app.route('/reservations')
def reservations():
    """Table reservation booking page with table options and user's history."""
    tables = db.query_db("SELECT * FROM restaurant_tables ORDER BY capacity ASC")
    
    user = None
    user_reservations = []
    if session.get('user_id'):
        user = db.query_db("SELECT * FROM users WHERE id = %s", (session['user_id'],), one=True)
        user_reservations = db.query_db("""
            SELECT r.*, t.table_number, t.location, t.capacity 
            FROM reservations r
            JOIN restaurant_tables t ON r.table_id = t.id
            WHERE r.user_id = %s
            ORDER BY r.reservation_date DESC, r.reservation_time DESC
        """, (session['user_id'],))

    return render_template(
        'reservations.html', 
        tables=tables, 
        user=user, 
        user_reservations=user_reservations
    )


@app.route('/reservations/book', methods=['POST'])
def book_table():
    """Handles table reservation requests and prevents overlapping conflicts."""
    customer_name = request.form.get('customer_name', '').strip()
    customer_phone = request.form.get('customer_phone', '').strip()
    customer_email = request.form.get('customer_email', '').strip()
    reservation_date = request.form.get('reservation_date')
    reservation_time = request.form.get('reservation_time')
    guest_count = int(request.form.get('guest_count', 2))
    table_id = int(request.form.get('table_id'))
    special_request = request.form.get('special_request', '').strip()

    if not customer_name or not customer_phone or not customer_email or not reservation_date or not reservation_time or not table_id:
        flash("All fields marked with * are required.", "danger")
        return redirect(url_for('reservations'))

    # CONFLICT PREVENTION:
    # Check if this table is already booked on the same date and time slot with status != 'cancelled'
    conflict_check = db.query_db("""
        SELECT * FROM reservations 
        WHERE table_id = %s 
          AND reservation_date = %s 
          AND reservation_time = %s 
          AND status IN ('pending', 'confirmed')
    """, (table_id, reservation_date, reservation_time), one=True)

    if conflict_check:
        flash(
            f"Sorry! Table is already booked for {reservation_date} at {reservation_time}. "
            "Please select a different time slot or choose another table.", 
            "danger"
        )
        return redirect(url_for('reservations'))

    user_id = session.get('user_id')

    try:
        insert_sql = """
            INSERT INTO reservations (
                user_id, table_id, customer_name, customer_email, customer_phone,
                reservation_date, reservation_time, guest_count, special_request, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_db(insert_sql, (
            user_id, table_id, customer_name, customer_email, customer_phone,
            reservation_date, reservation_time, guest_count, special_request, 'pending'
        ))

        flash("Your table reservation request has been submitted! Our host will confirm shortly.", "success")
        return redirect(url_for('reservations'))
    except Exception as e:
        flash(f"Error booking table: {e}", "danger")
        return redirect(url_for('reservations'))


# ============================================================
# CUSTOMER PORTAL & ORDERS
# ============================================================

@app.route('/my-orders')
@login_required
def my_orders():
    """Displays all past orders placed by the currently logged-in customer."""
    user_id = session['user_id']
    
    orders = db.query_db("""
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (user_id,))

    # Attach item details for each order
    for ord in orders:
        ord['order_items'] = db.query_db("SELECT * FROM order_items WHERE order_id = %s", (ord['id'],))

    return render_template('my_orders.html', orders=orders)


# ============================================================
# CONTACT PAGE & INQUIRIES
# ============================================================

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with restaurant details and inquiry submission form."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not subject or not message:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for('contact'))

        try:
            sql = """
                INSERT INTO contact_messages (name, email, phone, subject, message)
                VALUES (%s, %s, %s, %s, %s)
            """
            db.execute_db(sql, (name, email, phone, subject, message))
            flash("Thank you! Your message has been sent to our café managers.", "success")
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f"Failed to submit message: {e}", "danger")
            return redirect(url_for('contact'))

    return render_template('contact.html')


# ============================================================
# AUTHENTICATION: LOGIN, REGISTER & LOGOUT
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User and Administrator Login controller."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html')

        user = db.query_db("SELECT * FROM users WHERE LOWER(email) = %s", (email,), one=True)

        if user and check_password_hash(user['password_hash'], password):
            # Save session
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            session.permanent = True

            flash(f"Welcome back, {user['full_name']}!", "success")

            # Route redirect depending on role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))

            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('menu'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration form handler."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validation
        if not full_name or not email or not phone or not password:
            flash("All fields marked with * are required.", "danger")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html')

        # Check existing user
        existing_user = db.query_db("SELECT id FROM users WHERE LOWER(email) = %s", (email,), one=True)
        if existing_user:
            flash("An account with this email address already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        # Hash password securely using Werkzeug
        hashed_password = generate_password_hash(password)

        try:
            sql = """
                INSERT INTO users (full_name, email, phone, password_hash, role, address)
                VALUES (%s, %s, %s, %s, 'customer', %s)
            """
            user_id = db.execute_db(sql, (full_name, email, phone, hashed_password, address))

            # Auto log in the new customer
            session['user_id'] = user_id
            session['user_name'] = full_name
            session['user_email'] = email
            session['user_role'] = 'customer'
            session.permanent = True

            flash("Registration successful! Welcome to Caffè Delizioso.", "success")
            return redirect(url_for('menu'))
        except Exception as e:
            flash(f"Registration failed: {e}", "danger")
            return render_template('register.html')

    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logs out user and clears session."""
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('index'))


# ============================================================
# ADMIN PANEL CONTROLLERS
# ============================================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard overview with KPI statistics and recent items."""
    # 1. KPI Counts
    cust_row = db.query_db("SELECT COUNT(*) AS total FROM users WHERE role = 'customer'", one=True)
    items_row = db.query_db("SELECT COUNT(*) AS total FROM menu_items", one=True)
    orders_row = db.query_db("SELECT COUNT(*) AS total FROM orders", one=True)
    reservations_row = db.query_db("SELECT COUNT(*) AS total FROM reservations", one=True)
    sales_row = db.query_db("SELECT SUM(total_amount) AS total FROM orders WHERE status != 'Cancelled'", one=True)

    stats = {
        'total_customers': cust_row['total'] if cust_row else 0,
        'total_items': items_row['total'] if items_row else 0,
        'total_orders': orders_row['total'] if orders_row else 0,
        'total_reservations': reservations_row['total'] if reservations_row else 0,
        'total_sales': sales_row['total'] if sales_row and sales_row['total'] else 0.0
    }

    # 2. Recent Orders
    recent_orders = db.query_db("""
        SELECT * FROM orders 
        ORDER BY created_at DESC LIMIT 6
    """)

    # 3. Recent Reservations
    recent_reservations = db.query_db("""
        SELECT r.*, t.table_number 
        FROM reservations r
        JOIN restaurant_tables t ON r.table_id = t.id
        ORDER BY r.created_at DESC LIMIT 5
    """)

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_orders=recent_orders,
        recent_reservations=recent_reservations
    )


@app.route('/admin/menu')
@admin_required
def admin_menu():
    """Admin food items table with Add / Edit modals."""
    items = db.query_db("""
        SELECT m.*, c.name AS category_name 
        FROM menu_items m
        JOIN categories c ON m.category_id = c.id
        ORDER BY m.id DESC
    """)
    categories = db.query_db("SELECT * FROM categories ORDER BY display_order ASC")
    return render_template('admin/menu_management.html', items=items, categories=categories)


@app.route('/admin/menu/add', methods=['POST'])
@admin_required
def admin_add_item():
    """Adds a new dish to menu."""
    name = request.form.get('name', '').strip()
    category_id = int(request.form.get('category_id'))
    price = float(request.form.get('price', 0.0))
    image_url = request.form.get('image_url', '').strip()
    description = request.form.get('description', '').strip()
    is_veg = 1 if request.form.get('is_veg') else 0
    is_available = 1 if request.form.get('is_available') else 0
    is_featured = 1 if request.form.get('is_featured') else 0

    if not image_url:
        image_url = '/static/images/default_food.svg'

    try:
        sql = """
            INSERT INTO menu_items (
                name, category_id, price, image_url, description, 
                is_veg, is_available, is_featured
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_db(sql, (name, category_id, price, image_url, description, is_veg, is_available, is_featured))
        flash(f"Successfully added '{name}' to menu!", "success")
    except Exception as e:
        flash(f"Error adding item: {e}", "danger")

    return redirect(url_for('admin_menu'))


@app.route('/admin/menu/edit/<int:item_id>', methods=['POST'])
@admin_required
def admin_edit_item(item_id):
    """Edits an existing menu item."""
    name = request.form.get('name', '').strip()
    category_id = int(request.form.get('category_id'))
    price = float(request.form.get('price', 0.0))
    image_url = request.form.get('image_url', '').strip()
    description = request.form.get('description', '').strip()
    is_veg = 1 if request.form.get('is_veg') else 0
    is_available = 1 if request.form.get('is_available') else 0
    is_featured = 1 if request.form.get('is_featured') else 0

    if not image_url:
        image_url = '/static/images/default_food.svg'

    try:
        sql = """
            UPDATE menu_items 
            SET name = %s, category_id = %s, price = %s, image_url = %s, 
                description = %s, is_veg = %s, is_available = %s, is_featured = %s
            WHERE id = %s
        """
        db.execute_db(sql, (name, category_id, price, image_url, description, is_veg, is_available, is_featured, item_id))
        flash(f"Updated '{name}' successfully!", "success")
    except Exception as e:
        flash(f"Error updating item: {e}", "danger")

    return redirect(url_for('admin_menu'))


@app.route('/admin/menu/delete/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_item(item_id):
    """Deletes a menu item."""
    try:
        db.execute_db("DELETE FROM menu_items WHERE id = %s", (item_id,))
        flash("Item deleted from menu.", "info")
    except Exception as e:
        flash(f"Error deleting item: {e}", "danger")
    return redirect(url_for('admin_menu'))


@app.route('/admin/menu/toggle/<int:item_id>', methods=['POST'])
@admin_required
def admin_toggle_item(item_id):
    """Toggles stock availability between available and out-of-stock."""
    try:
        item = db.query_db("SELECT is_available FROM menu_items WHERE id = %s", (item_id,), one=True)
        if item:
            new_status = 0 if item['is_available'] else 1
            db.execute_db("UPDATE menu_items SET is_available = %s WHERE id = %s", (new_status, item_id))
            flash("Item availability updated.", "success")
    except Exception as e:
        flash(f"Error updating availability: {e}", "danger")
    return redirect(url_for('admin_menu'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Admin view for all customer orders with status filtering."""
    status_filter = request.args.get('status')
    
    if status_filter:
        orders = db.query_db("SELECT * FROM orders WHERE status = %s ORDER BY created_at DESC", (status_filter,))
    else:
        orders = db.query_db("SELECT * FROM orders ORDER BY created_at DESC")

    for ord in orders:
        ord['order_items'] = db.query_db("SELECT * FROM order_items WHERE order_id = %s", (ord['id'],))

    return render_template('admin/orders.html', orders=orders, current_status=status_filter)


@app.route('/admin/orders/status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Updates order fulfillment status."""
    new_status = request.form.get('status')
    valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Completed', 'Cancelled']

    if new_status in valid_statuses:
        try:
            db.execute_db("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
            flash(f"Order #{order_id} status updated to {new_status}.", "success")
        except Exception as e:
            flash(f"Error updating order status: {e}", "danger")

    return redirect(request.referrer or url_for('admin_orders'))


@app.route('/admin/reservations')
@admin_required
def admin_reservations():
    """Admin view for table reservations."""
    reservations = db.query_db("""
        SELECT r.*, t.table_number, t.capacity, t.location 
        FROM reservations r
        JOIN restaurant_tables t ON r.table_id = t.id
        ORDER BY r.reservation_date DESC, r.reservation_time DESC
    """)
    return render_template('admin/reservations.html', reservations=reservations)


@app.route('/admin/reservations/status/<int:res_id>/<status>', methods=['POST'])
@admin_required
def update_reservation_status(res_id, status):
    """Confirms or cancels a table reservation."""
    if status in ['confirmed', 'cancelled', 'completed', 'pending']:
        try:
            db.execute_db("UPDATE reservations SET status = %s WHERE id = %s", (status, res_id))
            flash(f"Reservation #{res_id} marked as {status.capitalize()}.", "success")
        except Exception as e:
            flash(f"Error updating reservation: {e}", "danger")
    return redirect(request.referrer or url_for('admin_reservations'))


@app.route('/admin/customers')
@admin_required
def admin_customers():
    """Lists all registered customer profiles and their order metrics."""
    customers = db.query_db("""
        SELECT u.*, 
               COUNT(o.id) AS total_orders, 
               SUM(CASE WHEN o.status != 'Cancelled' THEN o.total_amount ELSE 0 END) AS total_spent
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.role = 'customer'
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    return render_template('admin/customers.html', customers=customers)


@app.route('/admin/sales')
@admin_required
def admin_sales():
    """Financial sales reports, category breakdowns, and top-selling dishes."""
    # Summary
    gross_sales_row = db.query_db("SELECT SUM(total_amount) as s, COUNT(id) as c, AVG(total_amount) as a, SUM(tax_amount) as t FROM orders WHERE status != 'Cancelled'", one=True)
    
    sales_summary = {
        'gross_sales': gross_sales_row['s'] if gross_sales_row and gross_sales_row['s'] else 0.0,
        'total_orders': gross_sales_row['c'] if gross_sales_row else 0,
        'avg_order_value': gross_sales_row['a'] if gross_sales_row and gross_sales_row['a'] else 0.0,
        'total_tax': gross_sales_row['t'] if gross_sales_row and gross_sales_row['t'] else 0.0,
    }

    # Top 5 items
    top_items = db.query_db("""
        SELECT oi.item_name, SUM(oi.quantity) AS total_qty, SUM(oi.subtotal) AS total_sales
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'Cancelled'
        GROUP BY oi.item_name
        ORDER BY total_qty DESC
        LIMIT 5
    """)

    # Category revenue
    category_sales = db.query_db("""
        SELECT c.name AS category_name, 
               COUNT(oi.id) AS items_sold, 
               SUM(oi.subtotal) AS category_revenue
        FROM order_items oi
        JOIN menu_items m ON oi.menu_item_id = m.id
        JOIN categories c ON m.category_id = c.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'Cancelled'
        GROUP BY c.name
        ORDER BY category_revenue DESC
    """)

    return render_template(
        'admin/sales_reports.html',
        sales_summary=sales_summary,
        top_items=top_items,
        category_sales=category_sales
    )


@app.route('/admin/messages')
@admin_required
def admin_messages():
    """Views contact form messages submitted by visitors."""
    messages = db.query_db("SELECT * FROM contact_messages ORDER BY created_at DESC")
    return render_template('admin/messages.html', messages=messages)


@app.route('/admin/messages/read/<int:msg_id>', methods=['POST'])
@admin_required
def admin_mark_message_read(msg_id):
    """Marks message as read."""
    db.execute_db("UPDATE contact_messages SET is_read = 1 WHERE id = %s", (msg_id,))
    flash("Message marked as read.", "success")
    return redirect(url_for('admin_messages'))


@app.route('/admin/messages/delete/<int:msg_id>', methods=['POST'])
@admin_required
def admin_delete_message(msg_id):
    """Deletes message inquiry."""
    db.execute_db("DELETE FROM contact_messages WHERE id = %s", (msg_id,))
    flash("Message deleted.", "info")
    return redirect(url_for('admin_messages'))


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', error_title="404 - Page Not Found", 
                           error_msg="The page you are looking for does not exist."), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base.html', error_title="500 - Server Error", 
                           error_msg="An unexpected error occurred. Please try again."), 500


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================
if __name__ == '__main__':
    print("=" * 65)
    print("  RESTAURANT & CAFE MANAGEMENT SYSTEM")
    print(f"  Active Database Backend: {db.get_active_backend().upper()}")
    print("  Serving at: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(debug=True, host='127.0.0.1', port=5000)
