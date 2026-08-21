"""
app.py
FoodieHub - Restaurant Food Ordering System
Main Flask application: routes, session auth, cart/checkout logic.
"""

import os
import random
import string
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

import models
from database import init_db, DB_PATH
from recommendation import recommend_for_user, because_you_ordered, popular_near_you

app = Flask(__name__)
app.secret_key = os.environ.get("FOODIEHUB_SECRET_KEY", "dev-secret-key-change-in-production")

DELIVERY_FEE = 40.0
TAX_RATE = 0.05  # 5% GST-style tax on subtotal


# ---------------------------------------------------------------------------
# Helpers / auth
# ---------------------------------------------------------------------------

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


def current_user():
    if "user_id" in session:
        return models.get_user_by_id(session["user_id"])
    return None


@app.context_processor
def inject_globals():
    """Make cart count and current user available in every template."""
    cart_count = 0
    if "user_id" in session:
        cart_count = models.get_cart_count(session["user_id"])
    return {"cart_count": cart_count, "logged_in_user": current_user()}


def calc_totals(items):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax = round(subtotal * TAX_RATE, 2)
    delivery_fee = DELIVERY_FEE if subtotal > 0 else 0
    discount = 50.0 if subtotal >= 500 else 0.0
    grand_total = round(subtotal + tax + delivery_fee - discount, 2)
    return {
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "delivery_fee": delivery_fee,
        "discount": discount,
        "grand_total": grand_total,
    }


# ---------------------------------------------------------------------------
# Landing / Auth (Mobile + OTP)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/generate-otp", methods=["POST"])
def generate_otp():
    phone = request.form.get("phone", "").strip()

    if not phone.isdigit() or len(phone) != 10:
        flash("Please enter a valid 10-digit mobile number.", "error")
        return redirect(url_for("login"))

    otp = "".join(random.choices(string.digits, k=6))
    models.store_otp(phone, otp)
    session["pending_phone"] = phone

    # DEMO ONLY: in production this would be sent via SMS gateway, never shown in UI.
    flash(f"Demo OTP for {phone}: {otp}", "info")
    return redirect(url_for("otp_page"))


@app.route("/otp")
def otp_page():
    if "pending_phone" not in session:
        return redirect(url_for("login"))
    return render_template("otp.html", phone=session["pending_phone"])


@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    phone = session.get("pending_phone")
    if not phone:
        return redirect(url_for("login"))

    entered_otp = request.form.get("otp", "").strip()
    success, message = models.verify_otp(phone, entered_otp)

    if not success:
        flash(message, "error")
        return redirect(url_for("otp_page"))

    user = models.get_user_by_phone(phone)
    if not user:
        user_id = models.create_user(phone)
    else:
        user_id = user["id"]

    session.pop("pending_phone", None)
    session["user_id"] = user_id
    flash("Welcome to FoodieHub! 🎉", "success")
    return redirect(url_for("home"))


@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    phone = session.get("pending_phone")
    if not phone:
        return redirect(url_for("login"))
    otp = "".join(random.choices(string.digits, k=6))
    models.store_otp(phone, otp)
    flash(f"Demo OTP resent for {phone}: {otp}", "info")
    return redirect(url_for("otp_page"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out. See you soon! 👋", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Home / Restaurants / Categories
# ---------------------------------------------------------------------------

@app.route("/home")
@login_required
def home():
    restaurants = models.get_all_restaurants()
    categories = models.get_all_categories()
    popular = models.get_popular_food(limit=8)
    recommended, rec_type = recommend_for_user(session["user_id"], limit=8)
    return render_template(
        "home.html",
        restaurants=restaurants[:6],
        categories=categories[:8],
        popular=popular,
        recommended=recommended,
        rec_type=rec_type,
    )


@app.route("/restaurants")
@login_required
def restaurants():
    all_restaurants = models.get_all_restaurants()
    return render_template("restaurants.html", restaurants=all_restaurants)


@app.route("/restaurant/<int:restaurant_id>")
@login_required
def restaurant_detail(restaurant_id):
    restaurant = models.get_restaurant(restaurant_id)
    if not restaurant:
        flash("Restaurant not found.", "error")
        return redirect(url_for("restaurants"))
    menu = models.get_menu_for_restaurant(restaurant_id)

    # group menu by category for a clean UI
    grouped = {}
    for item in menu:
        grouped.setdefault(item["category_name"], []).append(item)

    food_type_filter = request.args.get("type", "all")
    if food_type_filter != "all":
        grouped = {
            cat: [f for f in items if f["food_type"] == food_type_filter]
            for cat, items in grouped.items()
        }
        grouped = {cat: items for cat, items in grouped.items() if items}

    return render_template(
        "restaurant.html", restaurant=restaurant, grouped_menu=grouped, active_filter=food_type_filter
    )


@app.route("/categories")
@login_required
def categories():
    all_categories = models.get_all_categories()
    return render_template("categories.html", categories=all_categories)


@app.route("/category/<int:category_id>")
@login_required
def category_detail(category_id):
    category = models.get_category(category_id)
    if not category:
        flash("Category not found.", "error")
        return redirect(url_for("categories"))
    items = models.get_food_by_category(category_id)

    food_type_filter = request.args.get("type", "all")
    if food_type_filter != "all":
        items = [f for f in items if f["food_type"] == food_type_filter]

    return render_template("category.html", category=category, items=items, active_filter=food_type_filter)


# ---------------------------------------------------------------------------
# Food details
# ---------------------------------------------------------------------------

@app.route("/food/<int:food_id>")
@login_required
def food_details(food_id):
    food = models.get_food(food_id)
    if not food:
        flash("This food item is not available.", "error")
        return redirect(url_for("home"))
    return render_template("food_details.html", food=food)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@app.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    foods, restaurants_result = ([], [])
    if query:
        foods, restaurants_result = models.search_everything(query)
    return render_template("search.html", query=query, foods=foods, restaurants=restaurants_result)


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

@app.route("/cart")
@login_required
def cart():
    items = models.get_cart_items(session["user_id"])
    totals = calc_totals(items)
    restaurant_ids = {item["restaurant_id"] for item in items}
    multi_restaurant_warning = len(restaurant_ids) > 1
    return render_template("cart.html", items=items, totals=totals, multi_restaurant_warning=multi_restaurant_warning)


@app.route("/cart/add", methods=["POST"])
@login_required
def cart_add():
    food_id = request.form.get("food_id", type=int)
    quantity = request.form.get("quantity", default=1, type=int)

    food = models.get_food(food_id) if food_id else None
    if not food:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": "Invalid food item."}), 400
        flash("Invalid food item.", "error")
        return redirect(url_for("home"))

    if not food["is_available"]:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": "This item is currently unavailable."}), 400
        flash("This item is currently unavailable.", "error")
        return redirect(request.referrer or url_for("home"))

    quantity = max(1, quantity)
    models.add_to_cart(session["user_id"], food_id, quantity)
    cart_count = models.get_cart_count(session["user_id"])

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "message": f"{food['name']} added to cart!", "cart_count": cart_count})

    flash(f"{food['name']} added to cart!", "success")
    return redirect(request.referrer or url_for("home"))


@app.route("/cart/update", methods=["POST"])
@login_required
def cart_update():
    cart_id = request.form.get("cart_id", type=int)
    quantity = request.form.get("quantity", type=int)

    if cart_id is None or quantity is None:
        return jsonify({"success": False, "message": "Invalid request."}), 400

    models.update_cart_quantity(session["user_id"], cart_id, quantity)
    items = models.get_cart_items(session["user_id"])
    totals = calc_totals(items)
    cart_count = models.get_cart_count(session["user_id"])

    return jsonify({"success": True, "totals": totals, "cart_count": cart_count, "item_count": len(items)})


@app.route("/cart/remove", methods=["POST"])
@login_required
def cart_remove():
    cart_id = request.form.get("cart_id", type=int)
    models.remove_from_cart(session["user_id"], cart_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        items = models.get_cart_items(session["user_id"])
        totals = calc_totals(items)
        cart_count = models.get_cart_count(session["user_id"])
        return jsonify({"success": True, "totals": totals, "cart_count": cart_count, "item_count": len(items)})

    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))


# ---------------------------------------------------------------------------
# Checkout / Orders
# ---------------------------------------------------------------------------

@app.route("/checkout")
@login_required
def checkout():
    items = models.get_cart_items(session["user_id"])
    if not items:
        flash("Your cart is empty. Add some delicious food first!", "error")
        return redirect(url_for("home"))

    restaurant_ids = {item["restaurant_id"] for item in items}
    if len(restaurant_ids) > 1:
        flash("Your cart has items from multiple restaurants. Please checkout one restaurant at a time.", "error")
        return redirect(url_for("cart"))

    totals = calc_totals(items)
    user = current_user()
    return render_template("checkout.html", items=items, totals=totals, user=user)


@app.route("/place-order", methods=["POST"])
@login_required
def place_order():
    items = models.get_cart_items(session["user_id"])
    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("home"))

    restaurant_ids = {item["restaurant_id"] for item in items}
    if len(restaurant_ids) > 1:
        flash("Please checkout one restaurant at a time.", "error")
        return redirect(url_for("cart"))

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    pincode = request.form.get("pincode", "").strip()
    payment_method = request.form.get("payment_method", "cod")

    if not all([name, phone, address, city, pincode]):
        flash("Please fill in all delivery details.", "error")
        return redirect(url_for("checkout"))

    full_address = f"{address}, {city} - {pincode}"
    totals = calc_totals(items)
    restaurant_id = items[0]["restaurant_id"]

    order_items = [
        {"food_id": item["id"], "quantity": item["quantity"], "price": item["price"]} for item in items
    ]

    order_id = models.create_order(
        user_id=session["user_id"],
        restaurant_id=restaurant_id,
        total_amount=totals["grand_total"],
        delivery_address=full_address,
        payment_method=payment_method,
        items=order_items,
    )

    # persist delivery details onto the profile for convenience next time
    models.update_user_profile(session["user_id"], name, None, address, city, pincode)

    models.clear_cart(session["user_id"])
    return redirect(url_for("order_success", order_id=order_id))


@app.route("/order-success/<int:order_id>")
@login_required
def order_success(order_id):
    order, items = models.get_order_detail(order_id, session["user_id"])
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("home"))
    return render_template("order_success.html", order=order, items=items)


@app.route("/orders")
@login_required
def orders():
    all_orders = models.get_orders_for_user(session["user_id"])
    return render_template("orders.html", orders=all_orders)


@app.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    order, items = models.get_order_detail(order_id, session["user_id"])
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders"))
    return render_template("order_detail.html", order=order, items=items)


@app.route("/order/<int:order_id>/reorder", methods=["POST"])
@login_required
def reorder(order_id):
    order, items = models.get_order_detail(order_id, session["user_id"])
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders"))

    for item in items:
        food = models.get_food(item["food_id"])
        if food and food["is_available"]:
            models.add_to_cart(session["user_id"], item["food_id"], item["quantity"])

    flash("Items from your previous order have been added to the cart!", "success")
    return redirect(url_for("cart"))


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@app.route("/profile")
@login_required
def profile():
    user = current_user()
    favorites = models.get_favorites(session["user_id"])
    order_count = len(models.get_orders_for_user(session["user_id"]))
    return render_template("profile.html", user=user, favorites=favorites, order_count=order_count)


@app.route("/profile/update", methods=["POST"])
@login_required
def profile_update():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    pincode = request.form.get("pincode", "").strip()

    if not name:
        flash("Name cannot be empty.", "error")
        return redirect(url_for("profile"))

    models.update_user_profile(session["user_id"], name, email, address, city, pincode)
    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile"))


@app.route("/favorite/toggle", methods=["POST"])
@login_required
def favorite_toggle():
    food_id = request.form.get("food_id", type=int)
    is_favorite = models.toggle_favorite(session["user_id"], food_id)
    return jsonify({"success": True, "is_favorite": is_favorite})


# ---------------------------------------------------------------------------
# AI Recommendations (standalone page)
# ---------------------------------------------------------------------------

@app.route("/recommendations")
@login_required
def recommendations():
    recommended, rec_type = recommend_for_user(session["user_id"], limit=12)
    category, because_items = because_you_ordered(session["user_id"], limit=8)
    popular = popular_near_you(limit=8)
    return render_template(
        "recommendations.html",
        recommended=recommended,
        rec_type=rec_type,
        because_category=category,
        because_items=because_items,
        popular=popular,
    )


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Something went wrong on our end."), 500


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
