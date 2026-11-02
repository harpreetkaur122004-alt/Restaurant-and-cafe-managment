"""
============================================================
RESTAURANT & CAFÉ MANAGEMENT SYSTEM
Database Helper Module (db.py)
Supports MySQL (Primary) with Automatic SQLite Graceful Fallback
MCA 1st Semester Mini Project
============================================================
"""
import sqlite3
import re
from config import Config

# Check if mysql.connector is available
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

# Global state to record current active DB backend
_ACTIVE_BACKEND = None  # 'mysql' or 'sqlite'


def get_connection():
    """
    Attempts to establish a connection to MySQL first.
    If MySQL is unavailable or Config.USE_SQLITE_FALLBACK is enabled,
    falls back cleanly to SQLite so the project runs reliably on any machine.
    """
    global _ACTIVE_BACKEND
    
    # 1. Try MySQL if available
    if MYSQL_AVAILABLE:
        try:
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            if conn.is_connected():
                _ACTIVE_BACKEND = 'mysql'
                return conn
        except MySQLError:
            pass  # Fall through to SQLite fallback if configured
            
    # 2. SQLite Fallback
    if Config.USE_SQLITE_FALLBACK:
        _ACTIVE_BACKEND = 'sqlite'
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row  # Access columns by name like dict
        # Enable foreign keys in SQLite
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    raise Exception(
        "Could not connect to MySQL database 'restaurant_db'. "
        "Please make sure MySQL / XAMPP is running, or set USE_SQLITE_FALLBACK = True in config.py"
    )


def get_active_backend():
    """Returns 'mysql' or 'sqlite'."""
    global _ACTIVE_BACKEND
    if _ACTIVE_BACKEND is None:
        conn = get_connection()
        conn.close()
    return _ACTIVE_BACKEND


def query_db(query, args=(), one=False):
    """
    Executes a SELECT query and returns results as dictionaries.
    Automatically handles placeholder differences between MySQL (%s) and SQLite (?).
    """
    conn = get_connection()
    backend = get_active_backend()
    
    try:
        if backend == 'mysql':
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, args)
            results = cursor.fetchall()
            cursor.close()
            return (results[0] if results else None) if one else results
        else:
            # SQLite backend: replace %s with ? safely
            sqlite_query = _convert_placeholders_to_sqlite(query)
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            cursor.close()
            return (results[0] if results else None) if one else results
    finally:
        conn.close()


def execute_db(query, args=(), commit=True):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    Returns the lastrowid (for INSERT) or rowcount (for UPDATE/DELETE).
    """
    conn = get_connection()
    backend = get_active_backend()
    last_id = None
    row_count = 0
    
    try:
        if backend == 'mysql':
            cursor = conn.cursor()
            cursor.execute(query, args)
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            if commit:
                conn.commit()
            cursor.close()
        else:
            sqlite_query = _convert_placeholders_to_sqlite(query)
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            if commit:
                conn.commit()
            cursor.close()
            
        return last_id if last_id else row_count
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def _convert_placeholders_to_sqlite(query):
    """
    Converts MySQL-style %s placeholders to SQLite ? placeholders.
    Also replaces MySQL-specific date functions (like CURDATE() + INTERVAL 1 DAY) if needed.
    """
    # Replace CURDATE() + INTERVAL 1 DAY with date('now', '+1 day')
    q = re.sub(r'CURDATE\(\)\s*\+\s*INTERVAL\s*1\s*DAY', "date('now', '+1 day')", query, flags=re.IGNORECASE)
    q = re.sub(r'CURDATE\(\)', "date('now')", q, flags=re.IGNORECASE)
    q = re.sub(r'NOW\(\)', "datetime('now', 'localtime')", q, flags=re.IGNORECASE)
    
    # Replace %s with ? for parameterized queries
    # Be careful not to replace % inside string literals or LIKE '%something%'
    parts = []
    in_single_quote = False
    i = 0
    while i < len(q):
        ch = q[i]
        if ch == "'" and (i == 0 or q[i - 1] != '\\'):
            in_single_quote = not in_single_quote
            parts.append(ch)
        elif not in_single_quote and ch == '%' and i + 1 < len(q) and q[i + 1] == 's':
            parts.append('?')
            i += 1  # Skip the 's'
        else:
            parts.append(ch)
        i += 1
    return "".join(parts)

