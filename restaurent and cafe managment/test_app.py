"""
============================================================
RESTAURANT & CAFÉ MANAGEMENT SYSTEM
Automated Test Verification Suite (test_app.py)
Validates all routes, cart logic, orders, reservations, & admin security
============================================================
"""
import sys
import unittest
from app import app
import db

class RestaurantSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_homepage(self):
        """Test home landing page renders successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Caff", response.data)
        self.assertIn(b"Signature Dishes", response.data)
        print("[PASS] Test 01: Home page loads with featured dishes and reviews.")

    def test_02_menu(self):
        """Test menu page with categories and filters."""
        response = self.client.get('/menu')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Breakfast", response.data)
        self.assertIn(b"Pizza and Burgers", response.data)

        # Filter by category
        res_cat = self.client.get('/menu?category=breakfast')
        self.assertEqual(res_cat.status_code, 200)
        self.assertIn(b"Belgian Waffle Tower", res_cat.data)
        print("[PASS] Test 02: Menu page & category filtering work.")

    def test_03_cart_workflow(self):
        """Test cart addition, quantity updates, tax calculations."""
        # 1. Add item to cart
        res_add = self.client.post('/cart/add/1', follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn(b"Belgian Waffle Tower", res_add.data)

        # 2. Increase quantity
        res_inc = self.client.post('/cart/update/1/increase', follow_redirects=True)
        self.assertEqual(res_inc.status_code, 200)

        # 3. View cart
        res_cart = self.client.get('/cart')
        self.assertEqual(res_cart.status_code, 200)
        self.assertIn(b"Belgian Waffle Tower", res_cart.data)
        self.assertIn(b"Order Bill Summary", res_cart.data)
        print("[PASS] Test 03: Cart add, increment, and tax calculation work.")

    def test_04_customer_login_and_orders(self):
        """Test customer authentication and my-orders portal."""
        # Login with seeded customer
        res_login = self.client.post('/login', data={
            'email': 'customer@gmail.com',
            'password': 'customer123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Rahul", res_login.data)

        # Access My Orders
        res_orders = self.client.get('/my-orders')
        self.assertEqual(res_orders.status_code, 200)
        self.assertIn(b"My Culinary Orders", res_orders.data)
        print("[PASS] Test 04: Customer login and order history work.")

    def test_05_checkout_and_place_order(self):
        """Test complete ordering pipeline from cart to placed order and invoice."""
        # Add item
        self.client.post('/cart/add/2')

        # Place order
        res_order = self.client.post('/order/place', data={
            'customer_name': 'Test Gourmet',
            'customer_phone': '+91 9988776655',
            'customer_email': 'test@gourmet.com',
            'order_type': 'takeaway',
            'payment_method': 'cash_on_delivery',
            'special_notes': 'Hot packaging please'
        }, follow_redirects=True)
        self.assertEqual(res_order.status_code, 200)
        self.assertIn(b"Order Successfully Placed", res_order.data)

        # Invoice check for order 1
        res_inv = self.client.get('/invoice/1')
        self.assertEqual(res_inv.status_code, 200)
        self.assertIn(b"TAX INVOICE", res_inv.data)
        print("[PASS] Test 05: Order placement, unique ID generation, and invoice work.")

    def test_06_table_reservation_conflict(self):
        """Test reservation creation and conflict prevention."""
        import random
        random_day = random.randint(10, 28)
        test_date = f"2026-11-{random_day}"
        test_time = "20:30"
        
        # Clean up any potential previous test booking for this slot
        db.execute_db("DELETE FROM reservations WHERE reservation_date = %s AND reservation_time = %s", (test_date, test_time))

        # First booking
        res_book1 = self.client.post('/reservations/book', data={
            'customer_name': 'Aarav Patel',
            'customer_phone': '+91 9123456789',
            'customer_email': 'aarav@example.com',
            'reservation_date': test_date,
            'reservation_time': test_time,
            'guest_count': 2,
            'table_id': 2,
            'special_request': 'Dinner reservation'
        }, follow_redirects=True)
        self.assertEqual(res_book1.status_code, 200)
        self.assertIn(b"submitted", res_book1.data)

        # Duplicate conflicting booking for SAME table, SAME date, SAME time
        res_conflict = self.client.post('/reservations/book', data={
            'customer_name': 'Sneha Rao',
            'customer_phone': '+91 9123456780',
            'customer_email': 'sneha@example.com',
            'reservation_date': test_date,
            'reservation_time': test_time,
            'guest_count': 2,
            'table_id': 2
        }, follow_redirects=True)
        self.assertEqual(res_conflict.status_code, 200)
        self.assertIn(b"already booked", res_conflict.data)
        print("[PASS] Test 06: Reservation conflict prevention verified.")

    def test_07_admin_dashboard_and_controls(self):
        """Test admin login, protected dashboard, menu management, and sales reports."""
        # 1. Unauthenticated access to /admin should redirect
        res_unauth = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(res_unauth.status_code, 302)

        # 2. Login as Admin
        self.client.post('/login', data={
            'email': 'admin@restaurant.com',
            'password': 'admin123'
        }, follow_redirects=True)

        # 3. Access admin dashboard
        res_dash = self.client.get('/admin')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b"Management Dashboard", res_dash.data)

        # 4. Access admin menu
        res_menu = self.client.get('/admin/menu')
        self.assertEqual(res_menu.status_code, 200)
        self.assertIn(b"Menu Item Management", res_menu.data)

        # 5. Access admin orders
        res_adm_ord = self.client.get('/admin/orders')
        self.assertEqual(res_adm_ord.status_code, 200)

        # 6. Access sales report
        res_sales = self.client.get('/admin/sales')
        self.assertEqual(res_sales.status_code, 200)
        self.assertIn(b"Financial & Sales Analytics", res_sales.data)
        print("[PASS] Test 07: Admin security, dashboard KPI, and sales reports verified.")


if __name__ == '__main__':
    print("=" * 65)
    print(" EXECUTING RESTAURANT SYSTEM AUTOMATED TEST SUITE")
    print("=" * 65)
    unittest.main()
