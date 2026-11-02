"""
============================================================
RESTAURANT & CAFÉ MANAGEMENT SYSTEM
Configuration Settings File (config.py)
MCA 1st Semester Mini Project
============================================================
"""
import os

class Config:
    # Flask Application Secret Key for Sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cafe_delizioso_secret_key_mca_2026_xyz987')
    
    # Restaurant Branding & Information
    RESTAURANT_NAME = "Caffè Delizioso & Bistro"
    RESTAURANT_TAGLINE = "Artisanal Coffee, Gourmet Bites & Unforgettable Moments"
    RESTAURANT_PHONE = "+91 98765 43210"
    RESTAURANT_EMAIL = "contact@caffedelizioso.com"
    RESTAURANT_ADDRESS = "Plot 42, Connaught Promenade, Inner Circle, New Delhi - 110001"
    RESTAURANT_TIMINGS = "Mon - Sun: 8:00 AM - 11:30 PM"
    
    # Billing & Financial Settings
    CURRENCY_SYMBOL = "₹"
    TAX_RATE_PERCENTAGE = 5.0  # 5% GST (Configurable sample tax)
    DELIVERY_FEE = 40.00       # Standard delivery fee in INR
    FREE_DELIVERY_THRESHOLD = 500.00  # Orders above this amount get free delivery
    
    # MySQL Database Connection Settings
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')  # Default XAMPP has empty password; change if set
    DB_NAME = os.environ.get('DB_NAME', 'restaurant_db')
    
    # Auto Fallback to SQLite
    # If set to True, the system will seamlessly use a local SQLite database (restaurant.db)
    # when MySQL is not running or accessible. This guarantees smooth viva demos on any machine!
    USE_SQLITE_FALLBACK = True
    SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurant.db')

