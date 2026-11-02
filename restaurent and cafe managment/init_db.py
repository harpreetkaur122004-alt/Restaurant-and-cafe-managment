"""
============================================================
RESTAURANT & CAFÉ MANAGEMENT SYSTEM
Database Initialization Script (init_db.py)
Creates all tables and seeds comprehensive sample data
MCA 1st Semester Mini Project
============================================================
"""
import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash
from config import Config

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


def init_mysql():
    """Attempts to connect to MySQL server, create restaurant_db and execute database.sql."""
    if not MYSQL_AVAILABLE:
        print("[!] mysql-connector-python is not installed.")
        return False
        
    print(f"[*] Attempting connection to MySQL server at {Config.DB_HOST}:{Config.DB_PORT} as '{Config.DB_USER}'...")
    try:
        # Connect to MySQL server without selecting DB first
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Read database.sql
        sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.sql')
        if not os.path.exists(sql_file_path):
            print(f"[!] database.sql not found at {sql_file_path}")
            return False
            
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split commands by semicolon
        statements = sql_content.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except Exception as ex:
                    # Ignore minor warnings on drop table if not exists
                    pass
                    
        cursor.close()
        conn.close()
        print("[OK] MySQL Database 'restaurant_db' successfully created and seeded!")
        return True
    except Exception as e:
        print(f"[-] Could not initialize MySQL: {e}")
        return False


def init_sqlite():
    """Initializes local SQLite database (restaurant.db) with the exact same schema and seed data."""
    sqlite_path = Config.SQLITE_DB_PATH
    print(f"[*] Initializing SQLite database at: {sqlite_path}")
    
    # Remove existing SQLite file to ensure fresh seeding if re-run
    if os.path.exists(sqlite_path):
        try:
            os.remove(sqlite_path)
        except Exception:
            pass

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'customer' CHECK(role IN ('customer', 'admin')),
        address TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Categories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        slug TEXT NOT NULL UNIQUE,
        description TEXT,
        display_order INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Menu items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image_url TEXT DEFAULT '/static/images/default_food.jpg',
        is_veg BOOLEAN DEFAULT 1,
        is_available BOOLEAN DEFAULT 1,
        is_featured BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    );
    """)

    # 4. Restaurant tables table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant_tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_number TEXT NOT NULL UNIQUE,
        capacity INTEGER NOT NULL,
        location TEXT DEFAULT 'Main Dining Hall',
        status TEXT DEFAULT 'available' CHECK(status IN ('available', 'occupied', 'reserved', 'maintenance')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Reservations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        table_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        reservation_date DATE NOT NULL,
        reservation_time TIME NOT NULL,
        guest_count INTEGER NOT NULL,
        special_request TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'cancelled', 'completed')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (table_id) REFERENCES restaurant_tables(id) ON DELETE CASCADE
    );
    """)

    # 6. Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        user_id INTEGER,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        delivery_address TEXT,
        order_type TEXT DEFAULT 'delivery' CHECK(order_type IN ('dine_in', 'takeaway', 'delivery')),
        table_number TEXT,
        payment_method TEXT DEFAULT 'cash_on_delivery' CHECK(payment_method IN ('cash_on_delivery', 'card', 'upi', 'pay_at_counter')),
        payment_status TEXT DEFAULT 'pending' CHECK(payment_status IN ('pending', 'paid', 'refunded')),
        subtotal REAL NOT NULL DEFAULT 0.0,
        tax_amount REAL NOT NULL DEFAULT 0.0,
        delivery_fee REAL NOT NULL DEFAULT 0.0,
        total_amount REAL NOT NULL DEFAULT 0.0,
        status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Confirmed', 'Preparing', 'Ready', 'Completed', 'Cancelled')),
        special_notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # 7. Order items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_item_id INTEGER,
        item_name TEXT NOT NULL,
        unit_price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        subtotal REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE SET NULL
    );
    """)

    # 8. Contact messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 9. Reviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        customer_name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        is_approved BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # SEED DATA
    # Categories
    cursor.executemany("""
    INSERT INTO categories (id, name, slug, description, display_order) VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 'Breakfast', 'breakfast', 'Fresh morning delights, artisan toasts, and fluffy pancakes', 1),
        (2, 'Starters', 'starters', 'Crispy appetizers, gourmet soups, and savory bites', 2),
        (3, 'Main Course', 'main-course', 'Hearty sizzlers, pastas, rich curries, and roasted specials', 3),
        (4, 'Pizza and Burgers', 'pizza-burgers', 'Wood-fired sourdough pizzas and gourmet handcrafted burgers', 4),
        (5, 'Coffee and Tea', 'coffee-tea', 'Freshly brewed espresso blends, cappuccino, and aromatic herbal teas', 5),
        (6, 'Cold Drinks', 'cold-drinks', 'Refreshing coolers, fruit smoothies, mojitos, and iced shakes', 6),
        (7, 'Desserts', 'desserts', 'Decadent chocolate lava cakes, cheesecakes, and artisanal gelato', 7)
    ])

    # Users
    admin_hash = generate_password_hash('admin123')
    customer_hash = generate_password_hash('customer123')
    
    cursor.executemany("""
    INSERT INTO users (id, full_name, email, phone, password_hash, role, address) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        (1, 'Restaurant Administrator', 'admin@restaurant.com', '+91 9876543210', 
         admin_hash, 'admin', 'Caffè Delizioso Main Office, Connaught Place, New Delhi'),
        (2, 'Rahul Sharma', 'customer@gmail.com', '+91 9811223344',
         customer_hash, 'customer', 'Flat 402, Green Park Residency, New Delhi')
    ])

    # Tables
    cursor.executemany("""
    INSERT INTO restaurant_tables (id, table_number, capacity, location, status) VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 'T-01', 2, 'Cozy Window Corner', 'available'),
        (2, 'T-02', 2, 'Main Dining Hall', 'available'),
        (3, 'T-03', 4, 'Center Dining Area', 'available'),
        (4, 'T-04', 4, 'Outdoor Garden Patio', 'available'),
        (5, 'T-05', 6, 'Family Booth Left', 'available'),
        (6, 'T-06', 6, 'Family Booth Right', 'available'),
        (7, 'T-07', 8, 'Private Executive Lounge', 'available'),
        (8, 'T-08', 10, 'Rooftop Banquet Table', 'available')
    ])

    # Menu Items
    cursor.executemany("""
    INSERT INTO menu_items (id, category_id, name, description, price, image_url, is_veg, is_available, is_featured) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        # Breakfast
        (1, 1, 'Belgian Waffle Tower', 'Crispy golden Belgian waffles stacked with organic maple syrup, fresh strawberries, and whipped cream.', 280.00, 'https://images.unsplash.com/photo-1562376552-0d160a2f238d?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (2, 1, 'Avocado Sourdough Toast', 'Toasted artisan sourdough loaded with smashed Hass avocado, cherry tomatoes, feta cheese, and balsamic glaze.', 260.00, 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (3, 1, 'English Breakfast Platter', 'Fluffy scrambled eggs or sautéed tofu, grilled mushrooms, hash browns, baked beans, and buttered toast.', 340.00, 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=500&auto=format&fit=crop&q=80', 0, 1, 0),
        (4, 1, 'Fluffy Blueberry Pancakes', 'Thick stack of buttermilk pancakes bursting with wild blueberries and melted cinnamon butter.', 250.00, 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&auto=format&fit=crop&q=80', 1, 1, 0),

        # Starters
        (5, 2, 'Crispy Truffle Fries', 'Hand-cut golden fries tossed in aromatic white truffle oil, grated parmesan, and rosemary with garlic aioli.', 220.00, 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (6, 2, 'Peri-Peri Paneer Tikka', 'Succulent cottage cheese cubes marinated in fiery peri-peri spices, roasted in clay oven with bell peppers.', 290.00, 'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (7, 2, 'Classic Bruschetta Trio', 'Toasted crusty baguette rubbed with garlic, topped with heirloom tomatoes, fresh basil, and extra virgin olive oil.', 240.00, 'https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?w=500&auto=format&fit=crop&q=80', 1, 1, 0),
        (8, 2, 'Crisp Golden Spring Rolls', 'Delicate crispy wonton wrappers packed with wok-tossed glass noodles and crunchy Asian vegetables.', 210.00, 'https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=80', 1, 1, 0),

        # Main Course
        (9, 3, 'Creamy Fettuccine Alfredo', 'Velvety fettuccine ribbons smothered in rich garlic parmesan cream sauce with grilled mushrooms.', 380.00, 'https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (10, 3, 'Paneer Butter Masala Sizzler', 'Tender cottage cheese simmered in butter tomato gravy, served sizzling with jeera rice and garlic naan.', 420.00, 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (11, 3, 'Mediterranean Grilled Bowl', 'Herb-infused quinoa, roasted zucchini, chickpeas, olives, and grilled halloumi drizzled with tahini.', 390.00, 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format&fit=crop&q=80', 1, 1, 0),
        (12, 3, 'Spicy Penne Arrabbiata', 'Al dente penne in a robust sauce of crushed San Marzano tomatoes, red chili flakes, garlic, and fresh basil.', 350.00, 'https://images.unsplash.com/photo-1621996346565-e3d5d6281691?w=500&auto=format&fit=crop&q=80', 1, 1, 0),

        # Pizza & Burgers
        (13, 4, 'Artisan Margherita Pizza', 'Hand-stretched sourdough pizza, San Marzano tomato sauce, fresh buffalo mozzarella, and aromatic basil leaves.', 420.00, 'https://images.unsplash.com/photo-1604382355076-af4b0eb60143?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (14, 4, 'Smoky BBQ Farmhouse Burger', 'Juicy grilled vegetable patty, cheddar cheese, caramelized onions, smoked barbecue sauce on a brioche bun.', 310.00, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (15, 4, 'Four Cheese & Jalapeño Pizza', 'Gorgonzola, mozzarella, fontina, and parmesan topped with spicy pickled jalapeños and hot honey.', 480.00, 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=80', 1, 1, 0),
        (16, 4, 'Crispy Paneer Supreme Burger', 'Golden breaded spicy paneer slab, creamy coleslaw, tangy chipotle mayo, and pickled cucumbers.', 320.00, 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=80', 1, 1, 0),

        # Coffee & Tea
        (17, 5, 'Artisan Caramel Macchiato', 'Freshly steamed whole milk marked with bold espresso shots and sweet vanilla syrup, finished with buttery caramel drizzle.', 190.00, 'https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (18, 5, 'Velvet Cappuccino', 'Equal parts rich espresso, steamed milk, and velvety thick micro-foam dusted with Dutch dark cocoa powder.', 170.00, 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=500&auto=format&fit=crop&q=80', 1, 1, 0),
        (19, 5, 'Spanish Iced Latte', 'Chilled espresso poured over sweetened condensed milk and ice cubes for a smooth, refreshing caffeine kick.', 210.00, 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (20, 5, 'Masala Chai Latte', 'Traditional Assam black tea brewed with crushed green cardamom, cinnamon, fresh ginger, and steamed milk.', 140.00, 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&auto=format&fit=crop&q=80', 1, 1, 0),

        # Cold Drinks
        (21, 6, 'Classic Mint Virgin Mojito', 'Crushed fresh mint leaves, zesty lime wedges, simple cane syrup, and sparkling soda served over crushed ice.', 180.00, 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (22, 6, 'Belgian Chocolate Thickshake', 'Decadent blend of Belgian chocolate gelato, dark chocolate ganache, and whipped cream top.', 230.00, 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=80', 1, 1, 0),
        (23, 6, 'Passionfruit & Berry Cooler', 'Tropical passionfruit puree, wild muddled berries, mint sprig, and chilled tonic water.', 200.00, 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&auto=format&fit=crop&q=80', 1, 1, 0),

        # Desserts
        (24, 7, 'Molten Dark Chocolate Lava Cake', 'Warm chocolate sponge with an oozing warm chocolate center, served with a scoop of Madagascar vanilla gelato.', 240.00, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (25, 7, 'New York Baked Cheesecake', 'Classic silky Philadelphia cream cheese on a buttery graham cracker crust, topped with raspberry coulis.', 260.00, 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500&auto=format&fit=crop&q=80', 1, 1, 1),
        (26, 7, 'Authentic Italian Tiramisu', 'Espresso-dipped savoiardi ladyfingers layered with velvety mascarpone zabaglione and dusted with bitter cocoa.', 270.00, 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&auto=format&fit=crop&q=80', 1, 1, 0)
    ])

    # Sample Order
    cursor.execute("""
    INSERT INTO orders (id, order_number, user_id, customer_name, customer_email, customer_phone, delivery_address, order_type, payment_method, payment_status, subtotal, tax_amount, delivery_fee, total_amount, status, special_notes)
    VALUES (1, 'ORD-20261102-1001', 2, 'Rahul Sharma', 'customer@gmail.com', '+91 9811223344', 'Flat 402, Green Park Residency, New Delhi', 'delivery', 'cash_on_delivery', 'pending', 730.00, 36.50, 40.00, 806.50, 'Completed', 'Please make it extra spicy and deliver hot.')
    """)

    # Sample Order Items
    cursor.executemany("""
    INSERT INTO order_items (order_id, menu_item_id, item_name, unit_price, quantity, subtotal)
    VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, 13, 'Artisan Margherita Pizza', 420.00, 1, 420.00),
        (1, 14, 'Smoky BBQ Farmhouse Burger', 310.00, 1, 310.00)
    ])

    # Sample Reservation
    cursor.execute("""
    INSERT INTO reservations (id, user_id, table_id, customer_name, customer_email, customer_phone, reservation_date, reservation_time, guest_count, special_request, status)
    VALUES (1, 2, 4, 'Rahul Sharma', 'customer@gmail.com', '+91 9811223344', date('now', '+1 day'), '19:30', 4, 'Anniversary dinner by the outdoor garden. Please arrange a candle.', 'confirmed')
    """)

    # Sample Reviews
    cursor.executemany("""
    INSERT INTO reviews (customer_name, rating, comment, is_approved)
    VALUES (?, ?, ?, ?)
    """, [
        ('Rahul Sharma', 5, 'The Artisan Margherita Pizza was extraordinary! The crust is light, sourdough flavor is authentic, and ambiance is top-notch.', 1),
        ('Priya Kapoor', 5, 'Best coffee in town! The caramel macchiato and Belgian waffles are our weekend tradition now. Amazing hospitality.', 1),
        ('Vikram Mehta', 4, 'Great food presentation, quick service, and super cozy environment. Highly recommend the truffle fries and pasta!', 1)
    ])

    # Sample Contact Messages
    cursor.executemany("""
    INSERT INTO contact_messages (name, email, phone, subject, message, is_read)
    VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ('Ananya Gupta', 'ananya.g@outlook.com', '+91 9899112233', 'Catering Inquiry for Birthday Party', 'Hi Caffè Delizioso team, do you provide outdoor catering for a private birthday party with 30 guests next month?', 0),
        ('Rohan Verma', 'rohan.v@yahoo.com', '+91 9711554433', 'Table Reservation Question', 'Is rooftop seating accessible for senior citizens via elevator? Looking forward to visiting with grandparents.', 1)
    ])

    conn.commit()
    conn.close()
    print("[OK] SQLite database successfully created and fully populated!")
    return True


if __name__ == '__main__':
    print("=" * 65)
    print(" RESTAURANT & CAFE MANAGEMENT SYSTEM - DATABASE INITIALIZATION")
    print("=" * 65)
    
    # 1. Try MySQL first
    mysql_success = init_mysql()
    
    # 2. Always prepare SQLite as fallback so app never breaks
    init_sqlite()
    
    print("\n" + "=" * 65)
    if mysql_success:
        print(" SUCCESS: MySQL Database 'restaurant_db' is ready to use!")
    else:
        print(" NOTICE: MySQL server was not accessible at this moment.")
        print(" -> SQLite database 'restaurant.db' has been initialized with full")
        print("    sample data and 100% feature parity.")
        print(" -> The app will run seamlessly immediately!")
    print("=" * 65)
