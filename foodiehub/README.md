# 🍽️ FoodieHub — Restaurant Food Ordering System

A complete, working full-stack food ordering web application built with **Flask + SQLite**,
with a Python-based AI recommendation engine and a modern, responsive UI.

> **Note:** This is a demo/college project. Restaurant names, menus, and prices are fictional.
> OTP login is simulated (no real SMS is sent — the OTP is shown directly in the UI for demo purposes).

---

## ✨ Features

- 📱 Mobile number + OTP login (with expiry, resend, and demo OTP display)
- 🏠 Animated landing page and dashboard with category & restaurant browsing
- 🏪 6 demo restaurants, each with its own realistic menu subset
- 🍕 16 food categories, 100+ dishes with real food photography
- 🔎 Real-time search across food, restaurants, and cuisines
- 🥗 Veg / Non-Veg / Egg filters with clear visual indicators
- ⭐ Ratings for restaurants and dishes
- 🛒 Fully functional cart with live quantity controls and totals
- 💳 Checkout with delivery details and Cash on Delivery / demo UPI / demo Card options
- 📦 Order history with statuses and one-click reorder
- 🤖 **A real AI recommendation engine** (not hardcoded) that learns from order history —
  "Recommended For You", "Popular Near You", and "Because You Ordered..." sections
- 👤 Editable user profile with favorites
- 📱 Fully responsive: desktop, tablet, and mobile (with bottom nav on mobile)

---

## 🧱 Tech Stack

| Layer          | Technology              |
|----------------|--------------------------|
| Backend        | Python 3, Flask          |
| Database       | SQLite (raw `sqlite3`, parameterized queries) |
| Frontend       | HTML5, CSS3, Vanilla JavaScript |
| Recommendations| Python (weighted scoring engine in `recommendation.py`) |
| Auth           | Session-based, Mobile + OTP (no passwords stored) |

---

## 📁 Project Structure

```
foodiehub/
│
├── app.py                 # Flask app: all routes
├── database.py             # SQLite connection + schema
├── models.py                # Data access layer (queries)
├── recommendation.py         # AI recommendation engine
├── seed_data.py                # Populates demo data
├── requirements.txt
├── README.md
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html               # Shared layout, nav, footer
│   ├── login.html / otp.html    # Auth screens
│   ├── home.html
│   ├── restaurants.html / restaurant.html
│   ├── categories.html / category.html
│   ├── food_details.html
│   ├── search.html
│   ├── cart.html / checkout.html / order_success.html
│   ├── orders.html / order_detail.html
│   ├── profile.html / recommendations.html
│   ├── error.html
│   └── _food_card.html / _restaurant_card.html   # reusable partials
│
├── static/
│   ├── css/style.css          # Full design system
│   ├── js/main.js               # Add-to-cart, toasts, favorites
│   ├── js/cart.js                # Cart quantity + totals logic
│   └── images/
│
└── instance/
    └── restaurant.db            # SQLite database (auto-created)
```

---

## 🗄️ Database Schema

- **users** — id, name, phone, email, address, city, pincode, created_at
- **otp_store** — phone, otp, expires_at, verified
- **restaurants** — id, name, location, cuisine, rating, delivery_time, image, veg_only
- **categories** — id, name, icon
- **food_items** — id, restaurant_id (FK), category_id (FK), name, description, price, rating, food_type, image_url, is_available
- **cart_items** — id, user_id (FK), food_id (FK), quantity
- **orders** — id, user_id (FK), restaurant_id (FK), total_amount, delivery_address, payment_method, status, order_date
- **order_items** — id, order_id (FK), food_id (FK), quantity, price
- **favorites** — id, user_id (FK), food_id (FK)

All foreign keys enforced with `PRAGMA foreign_keys = ON`.

---

## 🚀 Setup Instructions

### 1. Requirements
- Python 3.10+

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize & seed the database

```bash
python seed_data.py
```

This creates `instance/restaurant.db` and populates it with categories, restaurants, and food items.
(Safe to re-run any time — it resets demo data back to a clean state.)

### 5. Run the app

```bash
python app.py
```

### 6. Open the website

Visit **http://127.0.0.1:5000** in your browser.

---

## 🧪 Testing the Flow

1. Enter any 10-digit mobile number on the login screen → click **Generate OTP**
2. The demo OTP appears in a notification banner at the top right — copy it
3. Enter the OTP on the verification screen → you're logged in
4. Browse restaurants/categories, use the search bar, add items to your cart
5. Adjust quantities in the cart, proceed to checkout, fill in delivery details
6. Place the order → see the success screen → check **Order History**
7. Visit **"For You"** in the nav to see AI recommendations improve as you order more
8. Use **Reorder** on a past order, and try the ♡ favorite button on a food details page

---

## 🤖 How the AI Recommendation Engine Works

Implemented entirely in `recommendation.py` (not hardcoded frontend text):

1. Builds a profile from the user's **order history**: favourite categories, food types (veg/non-veg/egg), and restaurants — each weighted by how often they were ordered.
2. Scores every dish the user *hasn't* ordered yet using a weighted formula:
   `0.45 × category match + 0.25 × food-type match + 0.15 × restaurant match + 0.15 × dish rating`
3. Returns the top-scoring dishes as **"Recommended For You"**.
4. A **cold-start fallback** (rating-based "Popular") kicks in for brand-new users with no order history.
5. **"Because You Ordered..."** highlights more dishes from the user's single most-ordered category.

---

## 🔒 Security Notes

- No passwords are stored — authentication is OTP-based only.
- OTPs expire after 5 minutes and are single-use.
- All SQL queries are parameterized (no string-concatenated SQL).
- Every cart/order/profile route is protected by a `login_required` decorator and scoped to `session['user_id']` — users cannot view or modify another user's cart, orders, or profile.
- Server-side validation on cart quantities, checkout fields, and order totals (totals are recalculated server-side, never trusted from the client).

---

## 🔮 Future Enhancements

- Real SMS OTP gateway integration (Twilio / MSG91)
- Live order tracking with real-time status updates (WebSockets)
- Restaurant-side dashboard for managing menus and incoming orders
- Real payment gateway integration (Razorpay / Stripe)
- Ratings & reviews submitted by users after delivery
- Coupon codes and loyalty points
- Admin panel for managing restaurants, categories, and food items

---

## 📸 Screenshots

_Add screenshots here after running the app locally — e.g. login, home, cart, checkout, and recommendations screens._

---

Built as a full-stack demo project. Not affiliated with any real food-delivery service.
