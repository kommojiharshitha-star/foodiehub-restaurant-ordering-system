"""
models.py
Lightweight data-access helper functions on top of raw SQLite.
Every function opens its own short-lived connection, which is safe
for a small Flask demo app running with the built-in dev server.
"""

import datetime
from database import get_db

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_user_by_phone(phone):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def create_user(phone, name=None):
    conn = get_db()
    name = name or f"Foodie{phone[-4:]}"
    cur = conn.execute(
        "INSERT INTO users (name, phone) VALUES (?, ?)", (name, phone)
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def update_user_profile(user_id, name, email, address, city, pincode):
    conn = get_db()
    conn.execute(
        """UPDATE users SET name=?, email=?, address=?, city=?, pincode=?
           WHERE id=?""",
        (name, email, address, city, pincode, user_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# OTP
# ---------------------------------------------------------------------------

OTP_VALID_MINUTES = 5


def store_otp(phone, otp):
    conn = get_db()
    expires_at = (datetime.datetime.now() + datetime.timedelta(minutes=OTP_VALID_MINUTES)).isoformat()
    # invalidate previous otps for this phone
    conn.execute("DELETE FROM otp_store WHERE phone = ?", (phone,))
    conn.execute(
        "INSERT INTO otp_store (phone, otp, expires_at) VALUES (?, ?, ?)",
        (phone, otp, expires_at),
    )
    conn.commit()
    conn.close()


def verify_otp(phone, otp):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM otp_store WHERE phone = ? ORDER BY id DESC LIMIT 1", (phone,)
    ).fetchone()
    if not row:
        conn.close()
        return False, "No OTP was generated for this number. Please request a new OTP."
    if row["verified"]:
        conn.close()
        return False, "This OTP has already been used. Please request a new OTP."
    if datetime.datetime.now() > datetime.datetime.fromisoformat(row["expires_at"]):
        conn.close()
        return False, "OTP has expired. Please request a new OTP."
    if row["otp"] != otp:
        conn.close()
        return False, "Incorrect OTP. Please try again."
    conn.execute("UPDATE otp_store SET verified = 1 WHERE id = ?", (row["id"],))
    conn.commit()
    conn.close()
    return True, "OTP verified successfully."


# ---------------------------------------------------------------------------
# Restaurants / Categories / Food
# ---------------------------------------------------------------------------

def get_all_restaurants():
    conn = get_db()
    rows = conn.execute("SELECT * FROM restaurants ORDER BY rating DESC").fetchall()
    conn.close()
    return rows


def get_restaurant(restaurant_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM restaurants WHERE id = ?", (restaurant_id,)).fetchone()
    conn.close()
    return row


def get_menu_for_restaurant(restaurant_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT f.*, c.name AS category_name FROM food_items f
           JOIN categories c ON f.category_id = c.id
           WHERE f.restaurant_id = ? AND f.is_available = 1
           ORDER BY c.name, f.name""",
        (restaurant_id,),
    ).fetchall()
    conn.close()
    return rows


def get_all_categories():
    conn = get_db()
    rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return rows


def get_category(category_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
    conn.close()
    return row


def get_food_by_category(category_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT f.*, r.name AS restaurant_name FROM food_items f
           JOIN restaurants r ON f.restaurant_id = r.id
           WHERE f.category_id = ? AND f.is_available = 1
           ORDER BY f.rating DESC""",
        (category_id,),
    ).fetchall()
    conn.close()
    return rows


def get_food(food_id):
    conn = get_db()
    row = conn.execute(
        """SELECT f.*, r.name AS restaurant_name, r.id AS restaurant_id_ref
           FROM food_items f JOIN restaurants r ON f.restaurant_id = r.id
           WHERE f.id = ?""",
        (food_id,),
    ).fetchone()
    conn.close()
    return row


def search_everything(query):
    conn = get_db()
    like = f"%{query}%"
    foods = conn.execute(
        """SELECT f.*, r.name AS restaurant_name FROM food_items f
           JOIN restaurants r ON f.restaurant_id = r.id
           JOIN categories c ON f.category_id = c.id
           WHERE f.is_available = 1 AND (
               f.name LIKE ? OR r.name LIKE ? OR c.name LIKE ? OR r.cuisine LIKE ?
           )
           ORDER BY f.rating DESC""",
        (like, like, like, like),
    ).fetchall()
    restaurants = conn.execute(
        """SELECT * FROM restaurants WHERE name LIKE ? OR cuisine LIKE ? OR location LIKE ?""",
        (like, like, like),
    ).fetchall()
    conn.close()
    return foods, restaurants


def get_popular_food(limit=8):
    conn = get_db()
    rows = conn.execute(
        """SELECT f.*, r.name AS restaurant_name FROM food_items f
           JOIN restaurants r ON f.restaurant_id = r.id
           WHERE f.is_available = 1 ORDER BY f.rating DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def get_cart_items(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT ci.id AS cart_id, ci.quantity, f.*, r.name AS restaurant_name, r.id AS restaurant_id
           FROM cart_items ci
           JOIN food_items f ON ci.food_id = f.id
           JOIN restaurants r ON f.restaurant_id = r.id
           WHERE ci.user_id = ?
           ORDER BY ci.id""",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def get_cart_count(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS cnt FROM cart_items WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["cnt"]


def add_to_cart(user_id, food_id, quantity=1):
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM cart_items WHERE user_id = ? AND food_id = ?", (user_id, food_id)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE cart_items SET quantity = quantity + ? WHERE id = ?",
            (quantity, existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO cart_items (user_id, food_id, quantity) VALUES (?, ?, ?)",
            (user_id, food_id, quantity),
        )
    conn.commit()
    conn.close()


def update_cart_quantity(user_id, cart_id, quantity):
    conn = get_db()
    if quantity <= 0:
        conn.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?", (cart_id, user_id))
    else:
        conn.execute(
            "UPDATE cart_items SET quantity = ? WHERE id = ? AND user_id = ?",
            (quantity, cart_id, user_id),
        )
    conn.commit()
    conn.close()


def remove_from_cart(user_id, cart_id):
    conn = get_db()
    conn.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?", (cart_id, user_id))
    conn.commit()
    conn.close()


def clear_cart(user_id):
    conn = get_db()
    conn.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def create_order(user_id, restaurant_id, total_amount, delivery_address, payment_method, items):
    """items: list of dicts with food_id, quantity, price"""
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO orders (user_id, restaurant_id, total_amount, delivery_address, payment_method, status)
           VALUES (?, ?, ?, ?, ?, 'Order Placed')""",
        (user_id, restaurant_id, total_amount, delivery_address, payment_method),
    )
    order_id = cur.lastrowid
    for item in items:
        conn.execute(
            "INSERT INTO order_items (order_id, food_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, item["food_id"], item["quantity"], item["price"]),
        )
    conn.commit()
    conn.close()
    return order_id


def get_orders_for_user(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT o.*, r.name AS restaurant_name, r.image AS restaurant_image
           FROM orders o JOIN restaurants r ON o.restaurant_id = r.id
           WHERE o.user_id = ? ORDER BY o.order_date DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def get_order_detail(order_id, user_id):
    conn = get_db()
    order = conn.execute(
        """SELECT o.*, r.name AS restaurant_name, r.image AS restaurant_image
           FROM orders o JOIN restaurants r ON o.restaurant_id = r.id
           WHERE o.id = ? AND o.user_id = ?""",
        (order_id, user_id),
    ).fetchone()
    if not order:
        conn.close()
        return None, []
    items = conn.execute(
        """SELECT oi.*, f.name, f.image_url, f.food_type FROM order_items oi
           JOIN food_items f ON oi.food_id = f.id
           WHERE oi.order_id = ?""",
        (order_id,),
    ).fetchall()
    conn.close()
    return order, items


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------

def toggle_favorite(user_id, food_id):
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM favorites WHERE user_id = ? AND food_id = ?", (user_id, food_id)
    ).fetchone()
    if existing:
        conn.execute("DELETE FROM favorites WHERE id = ?", (existing["id"],))
        conn.commit()
        conn.close()
        return False
    conn.execute("INSERT INTO favorites (user_id, food_id) VALUES (?, ?)", (user_id, food_id))
    conn.commit()
    conn.close()
    return True


def get_favorites(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT f.*, r.name AS restaurant_name FROM favorites fav
           JOIN food_items f ON fav.food_id = f.id
           JOIN restaurants r ON f.restaurant_id = r.id
           WHERE fav.user_id = ?""",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows
