-- ============================================================
-- RESTAURANT & CAFÉ MANAGEMENT SYSTEM
-- Database Schema: restaurant_db
-- Developed for MCA 1st Semester Mini Project
-- ============================================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS restaurant_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE restaurant_db;

-- Disable foreign key checks while creating/dropping tables
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. USERS TABLE (Customers & Staff)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer', 'admin') DEFAULT 'customer',
    address TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 2. CATEGORIES TABLE
-- ------------------------------------------------------------
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    slug VARCHAR(80) NOT NULL UNIQUE,
    description VARCHAR(255) NULL,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 3. MENU ITEMS TABLE
-- ------------------------------------------------------------
DROP TABLE IF EXISTS menu_items;
CREATE TABLE menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT NULL,
    price DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(350) DEFAULT '/static/images/default_food.jpg',
    is_veg BOOLEAN DEFAULT TRUE,
    is_available BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 4. RESTAURANT TABLES (For Reservations & Dine-in)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS restaurant_tables;
CREATE TABLE restaurant_tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_number VARCHAR(20) NOT NULL UNIQUE,
    capacity INT NOT NULL,
    location VARCHAR(50) DEFAULT 'Main Dining Hall', -- e.g. Indoor, Patio, Window, Rooftop
    status ENUM('available', 'occupied', 'reserved', 'maintenance') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 5. RESERVATIONS TABLE
-- ------------------------------------------------------------
DROP TABLE IF EXISTS reservations;
CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    table_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(120) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    guest_count INT NOT NULL,
    special_request TEXT NULL,
    status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (table_id) REFERENCES restaurant_tables(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 6. ORDERS TABLE
-- ------------------------------------------------------------
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(120) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    delivery_address TEXT NULL,
    order_type ENUM('dine_in', 'takeaway', 'delivery') DEFAULT 'delivery',
    table_number VARCHAR(20) NULL,
    payment_method ENUM('cash_on_delivery', 'card', 'upi', 'pay_at_counter') DEFAULT 'cash_on_delivery',
    payment_status ENUM('pending', 'paid', 'refunded') DEFAULT 'pending',
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    delivery_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status ENUM('Pending', 'Confirmed', 'Preparing', 'Ready', 'Completed', 'Cancelled') DEFAULT 'Pending',
    special_notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 7. ORDER ITEMS TABLE
-- ------------------------------------------------------------
DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NULL,
    item_name VARCHAR(150) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 8. CONTACT MESSAGES TABLE
-- ------------------------------------------------------------
DROP TABLE IF EXISTS contact_messages;
CREATE TABLE contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 9. REVIEWS TABLE (Customer Testimonials)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    customer_name VARCHAR(100) NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- SAMPLE DATA INSERTION
-- ============================================================

-- 1. Insert Categories
INSERT INTO categories (name, slug, description, display_order) VALUES
('Breakfast', 'breakfast', 'Fresh morning delights, artisan toasts, and fluffy pancakes', 1),
('Starters', 'starters', 'Crispy appetizers, gourmet soups, and savory bites', 2),
('Main Course', 'main-course', 'Hearty sizzlers, pastas, rich curries, and roasted specials', 3),
('Pizza and Burgers', 'pizza-burgers', 'Wood-fired sourdough pizzas and gourmet handcrafted burgers', 4),
('Coffee and Tea', 'coffee-tea', 'Freshly brewed espresso blends, cappuccino, and aromatic herbal teas', 5),
('Cold Drinks', 'cold-drinks', 'Refreshing coolers, fruit smoothies, mojitos, and iced shakes', 6),
('Desserts', 'desserts', 'Decadent chocolate lava cakes, cheesecakes, and artisanal gelato', 7);

-- 2. Insert Users (Password is 'admin123' for admin, and 'customer123' for customer)
-- Note: Werkzeug scrypt/pbkdf2 hash generated for security
INSERT INTO users (full_name, email, phone, password_hash, role, address) VALUES
('Restaurant Administrator', 'admin@restaurant.com', '+91 9876543210', 'scrypt:32768:8:1$is7wsUoterO3L3Tr$173c462faaf5b9208e7fb5a1176e6392d4c2362a7f5e695f35fe20f976964b5c0470fa3ecef14b21322967414a35dbb240f5555d8ff12648d72d41268934b856', 'admin', 'Caffè Delizioso Main Office, Connaught Place, New Delhi'),
('Rahul Sharma', 'customer@gmail.com', '+91 9811223344', 'scrypt:32768:8:1$zH520QNU6V8GK53o$f4c2f809850b3838f52e25e12f48f1e7a184ca512b237555490a84f0e38435abd8793fa4738f6b89c912d5124f2121e92a957396c8f05767487ff59cadd32956', 'customer', 'Flat 402, Green Park Residency, New Delhi');

-- 3. Insert Restaurant Tables
INSERT INTO restaurant_tables (table_number, capacity, location, status) VALUES
('T-01', 2, 'Cozy Window Corner', 'available'),
('T-02', 2, 'Main Dining Hall', 'available'),
('T-03', 4, 'Center Dining Area', 'available'),
('T-04', 4, 'Outdoor Garden Patio', 'available'),
('T-05', 6, 'Family Booth Left', 'available'),
('T-06', 6, 'Family Booth Right', 'available'),
('T-07', 8, 'Private Executive Lounge', 'available'),
('T-08', 10, 'Rooftop Banquet Table', 'available');

-- 4. Insert Menu Items
INSERT INTO menu_items (category_id, name, description, price, image_url, is_veg, is_available, is_featured) VALUES
-- Breakfast (category 1)
(1, 'Belgian Waffle Tower', 'Crispy golden Belgian waffles stacked with organic maple syrup, fresh strawberries, and whipped cream.', 280.00, 'https://images.unsplash.com/photo-1562376552-0d160a2f238d?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(1, 'Avocado Sourdough Toast', 'Toasted artisan sourdough loaded with smashed Hass avocado, cherry tomatoes, feta cheese, and balsamic glaze.', 260.00, 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(1, 'English Breakfast Platter', 'Fluffy scrambled eggs or sautéed tofu, grilled mushrooms, hash browns, baked beans, and buttered toast.', 340.00, 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=500&auto=format&fit=crop&q=80', FALSE, TRUE, FALSE),
(1, 'Fluffy Blueberry Pancakes', 'Thick stack of buttermilk pancakes bursting with wild blueberries and melted cinnamon butter.', 250.00, 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),

-- Starters (category 2)
(2, 'Crispy Truffle Fries', 'Hand-cut golden fries tossed in aromatic white truffle oil, grated parmesan, and rosemary with garlic aioli.', 220.00, 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(2, 'Peri-Peri Paneer Tikka', 'Succulent cottage cheese cubes marinated in fiery peri-peri spices, roasted in clay oven with bell peppers.', 290.00, 'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(2, 'Classic Bruschetta Trio', 'Toasted crusty baguette rubbed with garlic, topped with heirloom tomatoes, fresh basil, and extra virgin olive oil.', 240.00, 'https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),
(2, 'Crisp Golden Spring Rolls', 'Delicate crispy wonton wrappers packed with wok-tossed glass noodles and crunchy Asian vegetables.', 210.00, 'https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),

-- Main Course (category 3)
(3, 'Creamy Fettuccine Alfredo', 'Velvety fettuccine ribbons smothered in rich garlic parmesan cream sauce with grilled mushrooms.', 380.00, 'https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(3, 'Paneer Butter Masala Sizzler', 'Tender cottage cheese simmered in butter tomato gravy, served sizzling with jeera rice and garlic naan.', 420.00, 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(3, 'Mediterranean Grilled Bowl', 'Herb-infused quinoa, roasted zucchini, chickpeas, olives, and grilled halloumi drizzled with tahini.', 390.00, 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),
(3, 'Spicy Penne Arrabbiata', 'Al dente penne in a robust sauce of crushed San Marzano tomatoes, red chili flakes, garlic, and fresh basil.', 350.00, 'https://images.unsplash.com/photo-1621996346565-e3d5d6281691?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),

-- Pizza & Burgers (category 4)
(4, 'Artisan Margherita Pizza', 'Hand-stretched sourdough pizza, San Marzano tomato sauce, fresh buffalo mozzarella, and aromatic basil leaves.', 420.00, 'https://images.unsplash.com/photo-1604382355076-af4b0eb60143?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(4, 'Smoky BBQ Farmhouse Burger', 'Juicy grilled vegetable patty, cheddar cheese, caramelized onions, smoked barbecue sauce on a brioche bun.', 310.00, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(4, 'Four Cheese & Jalapeño Pizza', 'Gorgonzola, mozzarella, fontina, and parmesan topped with spicy pickled jalapeños and hot honey.', 480.00, 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),
(4, 'Crispy Paneer Supreme Burger', 'Golden breaded spicy paneer slab, creamy coleslaw, tangy chipotle mayo, and pickled cucumbers.', 320.00, 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),

-- Coffee and Tea (category 5)
(5, 'Artisan Caramel Macchiato', 'Freshly steamed whole milk marked with bold espresso shots and sweet vanilla syrup, finished with buttery caramel drizzle.', 190.00, 'https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(5, 'Velvet Cappuccino', 'Equal parts rich espresso, steamed milk, and velvety thick micro-foam dusted with Dutch dark cocoa powder.', 170.00, 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),
(5, 'Spanish Iced Latte', 'Chilled espresso poured over sweetened condensed milk and ice cubes for a smooth, refreshing caffeine kick.', 210.00, 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(5, 'Masala Chai Latte', 'Traditional Assam black tea brewed with crushed green cardamom, cinnamon, fresh ginger, and steamed milk.', 140.00, 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),

-- Cold Drinks (category 6)
(6, 'Classic Mint Virgin Mojito', 'Crushed fresh mint leaves, zesty lime wedges, simple cane syrup, and sparkling soda served over crushed ice.', 180.00, 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(6, 'Belgian Chocolate Thickshake', 'Decadent blend of Belgian chocolate gelato, dark chocolate ganache, and whipped cream top.', 230.00, 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),
(6, 'Passionfruit & Berry Cooler', 'Tropical passionfruit puree, wild muddled berries, mint sprig, and chilled tonic water.', 200.00, 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE),

-- Desserts (category 7)
(7, 'Molten Dark Chocolate Lava Cake', 'Warm chocolate sponge with an oozing warm chocolate center, served with a scoop of Madagascar vanilla gelato.', 240.00, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(7, 'New York Baked Cheesecake', 'Classic silky Philadelphia cream cheese on a buttery graham cracker crust, topped with raspberry coulis.', 260.00, 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, TRUE),
(7, 'Authentic Italian Tiramisu', 'Espresso-dipped savoiardi ladyfingers layered with velvety mascarpone zabaglione and dusted with bitter cocoa.', 270.00, 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&auto=format&fit=crop&q=80', TRUE, TRUE, FALSE);

-- 5. Insert Sample Order
INSERT INTO orders (order_number, user_id, customer_name, customer_email, customer_phone, delivery_address, order_type, payment_method, payment_status, subtotal, tax_amount, delivery_fee, total_amount, status, special_notes) VALUES
('ORD-20261102-1001', 2, 'Rahul Sharma', 'customer@gmail.com', '+91 9811223344', 'Flat 402, Green Park Residency, New Delhi', 'delivery', 'cash_on_delivery', 'pending', 730.00, 36.50, 40.00, 806.50, 'Completed', 'Please make it extra spicy and deliver hot.');

-- 6. Insert Order Items for the sample order
INSERT INTO order_items (order_id, menu_item_id, item_name, unit_price, quantity, subtotal) VALUES
(1, 9, 'Artisan Margherita Pizza', 420.00, 1, 420.00),
(1, 10, 'Smoky BBQ Farmhouse Burger', 310.00, 1, 310.00);

-- 7. Insert Sample Reservation
INSERT INTO reservations (user_id, table_id, customer_name, customer_email, customer_phone, reservation_date, reservation_time, guest_count, special_request, status) VALUES
(2, 4, 'Rahul Sharma', 'customer@gmail.com', '+91 9811223344', CURDATE() + INTERVAL 1 DAY, '19:30:00', 4, 'Anniversary dinner by the outdoor garden. Please arrange a candle.', 'confirmed');

-- 8. Insert Sample Reviews
INSERT INTO reviews (user_id, customer_name, rating, comment, is_approved) VALUES
(2, 'Rahul Sharma', 5, 'The Artisan Margherita Pizza was extraordinary! The crust is light, sourdough flavor is authentic, and ambiance is top-notch.', TRUE),
(NULL, 'Priya Kapoor', 5, 'Best coffee in town! The caramel macchiato and Belgian waffles are our weekend tradition now. Amazing hospitality.', TRUE),
(NULL, 'Vikram Mehta', 4, 'Great food presentation, quick service, and super cozy environment. Highly recommend the truffle fries and pasta!', TRUE);

-- 9. Insert Sample Contact Messages
INSERT INTO contact_messages (name, email, phone, subject, message, is_read) VALUES
('Ananya Gupta', 'ananya.g@outlook.com', '+91 9899112233', 'Catering Inquiry for Birthday Party', 'Hi Caffè Delizioso team, do you provide outdoor catering for a private birthday party with 30 guests next month?', FALSE),
('Rohan Verma', 'rohan.v@yahoo.com', '+91 9711554433', 'Table Reservation Question', 'Is rooftop seating accessible for senior citizens via elevator? Looking forward to visiting with grandparents.', TRUE);
