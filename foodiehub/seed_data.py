"""
seed_data.py
Populates the SQLite database with demo categories, restaurants and
food items so the app has real content to browse out of the box.

This is DEMO data for a college project. Restaurant names, menus and
prices are fictional and not sourced from any real business.

Run with:  python seed_data.py
"""

from database import init_db, get_db


def img(keyword):
    """Real food-photo URL keyed by search term (works out of the box,
    no API key required). A fallback image is applied client-side in
    the templates/JS if a particular photo ever fails to load."""
    safe = keyword.replace(" ", ",")
    return f"https://loremflickr.com/480/360/{safe},food"


CATEGORIES = [
    ("Pizza", "🍕"),
    ("Burgers", "🍔"),
    ("Chicken Starters", "🍗"),
    ("Veg Starters", "🥗"),
    ("Biryani", "🍛"),
    ("Rice", "🍚"),
    ("Noodles", "🍜"),
    ("Indian Curries", "🍲"),
    ("Indian Breads", "🫓"),
    ("South Indian", "🥞"),
    ("Chinese", "🥡"),
    ("Desserts", "🍰"),
    ("Cold Drinks", "🥤"),
    ("Milkshakes", "🥛"),
    ("Tea & Coffee", "☕"),
    ("Healthy Food", "🥙"),
]

# name, location, cuisine, rating, delivery_time, image, veg_only, category_names_served
RESTAURANTS = [
    ("Udupi Grand", "MG Road, Kurnool", "South Indian, Biryani", 4.5, "30-35 min", img("south indian thali"), 0,
     ["South Indian", "Biryani", "Rice"]),
    ("Pizza Junction", "Silicon Valley Rd", "Pizza, Fast Food", 4.3, "25-30 min", img("pizza restaurant"), 0,
     ["Pizza", "Burgers", "Cold Drinks"]),
    ("Dragon Wok", "China Town Street", "Chinese, Asian", 4.2, "35-40 min", img("chinese wok"), 0,
     ["Chinese", "Noodles", "Rice"]),
    ("Spice Route Kitchen", "Old City Road", "North Indian, Mughlai", 4.6, "40-45 min", img("indian curry"), 0,
     ["Indian Curries", "Indian Breads", "Chicken Starters"]),
    ("Green Bowl Cafe", "Park View Lane", "Healthy, Continental", 4.4, "20-25 min", img("healthy salad bowl"), 1,
     ["Healthy Food", "Veg Starters"]),
    ("Sweet Treats Dessert Parlour", "Central Mall", "Desserts, Beverages", 4.7, "15-20 min", img("dessert cake shop"), 1,
     ["Desserts", "Milkshakes", "Tea & Coffee", "Cold Drinks"]),
]

# category_name -> list of (name, description, price, food_type)
FOOD_BY_CATEGORY = {
    "Pizza": [
        ("Margherita Pizza", "Classic cheese and tomato pizza on a hand-tossed base", 199, "veg"),
        ("Farmhouse Pizza", "Loaded with capsicum, onion, tomato and mushroom", 249, "veg"),
        ("Paneer Tikka Pizza", "Spicy paneer tikka chunks with onion and capsicum", 269, "veg"),
        ("Cheese Burst Pizza", "Extra cheesy pizza with a molten cheese core", 279, "veg"),
        ("Chicken Tikka Pizza", "Smoky chicken tikka pieces with peppers and onion", 299, "non_veg"),
        ("BBQ Chicken Pizza", "Grilled chicken tossed in tangy BBQ sauce", 319, "non_veg"),
        ("Pepperoni Pizza", "Loaded with spiced pepperoni and mozzarella", 329, "non_veg"),
        ("Peri Peri Chicken Pizza", "Fiery peri peri chicken with bell peppers", 309, "non_veg"),
    ],
    "Burgers": [
        ("Veg Burger", "Crispy veg patty with lettuce, tomato and mayo", 89, "veg"),
        ("Cheese Burger", "Veg patty topped with a melted cheese slice", 109, "veg"),
        ("Paneer Burger", "Grilled paneer patty with tangy sauces", 119, "veg"),
        ("Aloo Tikki Burger", "Spiced potato patty, an Indian classic", 79, "veg"),
        ("Chicken Burger", "Juicy chicken patty with fresh veggies", 139, "non_veg"),
        ("Crispy Chicken Burger", "Crunchy fried chicken fillet burger", 149, "non_veg"),
        ("Peri Peri Chicken Burger", "Spicy peri peri marinated chicken patty", 159, "non_veg"),
        ("Double Chicken Burger", "Two chicken patties stacked with cheese", 189, "non_veg"),
    ],
    "Chicken Starters": [
        ("Chicken 65", "Deep fried spicy South Indian chicken bites", 219, "non_veg"),
        ("Chilli Chicken", "Indo-Chinese chicken tossed in chilli garlic sauce", 229, "non_veg"),
        ("Chicken Lollipop", "Frenched chicken wings, deep fried and spiced", 249, "non_veg"),
        ("Chicken Manchurian", "Chicken balls tossed in Manchurian sauce", 229, "non_veg"),
        ("Tandoori Chicken (Half)", "Char-grilled chicken marinated in yogurt spices", 259, "non_veg"),
        ("Chicken Seekh Kebab", "Minced chicken skewers grilled to perfection", 239, "non_veg"),
        ("Chicken Malai Tikka", "Creamy, mildly spiced chicken tikka", 259, "non_veg"),
        ("Pepper Chicken", "Chicken tossed with crushed black pepper", 229, "non_veg"),
    ],
    "Veg Starters": [
        ("Paneer Tikka", "Char-grilled marinated cottage cheese cubes", 219, "veg"),
        ("Chilli Paneer", "Paneer tossed in Indo-Chinese chilli sauce", 219, "veg"),
        ("Gobi Manchurian", "Crispy cauliflower florets in tangy sauce", 179, "veg"),
        ("Baby Corn 65", "Deep fried spiced baby corn", 189, "veg"),
        ("Mushroom 65", "Crispy fried mushrooms with spice coating", 199, "veg"),
        ("Veg Spring Rolls", "Crunchy rolls stuffed with mixed vegetables", 159, "veg"),
        ("French Fries", "Golden and crispy salted potato fries", 99, "veg"),
        ("Peri Peri Fries", "Fries tossed in peri peri seasoning", 119, "veg"),
    ],
    "Biryani": [
        ("Veg Biryani", "Fragrant basmati rice cooked with mixed vegetables", 169, "veg"),
        ("Paneer Biryani", "Basmati rice layered with spiced paneer", 189, "veg"),
        ("Egg Biryani", "Dum biryani topped with boiled eggs", 169, "egg"),
        ("Chicken Dum Biryani", "Slow-cooked chicken biryani, Hyderabadi style", 229, "non_veg"),
        ("Chicken 65 Biryani", "Biryani topped with crispy chicken 65", 249, "non_veg"),
        ("Mutton Dum Biryani", "Rich, aromatic mutton biryani cooked on dum", 289, "non_veg"),
        ("Special Family Biryani", "Large-portion biryani for sharing", 599, "non_veg"),
    ],
    "Rice": [
        ("Jeera Rice", "Basmati rice tempered with cumin", 129, "veg"),
        ("Veg Fried Rice", "Wok-tossed rice with mixed vegetables", 149, "veg"),
        ("Egg Fried Rice", "Fried rice tossed with scrambled egg", 159, "egg"),
        ("Chicken Fried Rice", "Wok-tossed rice with diced chicken", 189, "non_veg"),
        ("Schezwan Fried Rice", "Spicy Schezwan sauce tossed fried rice", 169, "veg"),
        ("Prawn Fried Rice", "Fried rice loaded with succulent prawns", 229, "non_veg"),
    ],
    "Noodles": [
        ("Veg Hakka Noodles", "Classic stir-fried noodles with vegetables", 149, "veg"),
        ("Egg Noodles", "Hakka noodles tossed with scrambled egg", 159, "egg"),
        ("Chicken Hakka Noodles", "Stir-fried noodles with tender chicken", 189, "non_veg"),
        ("Schezwan Noodles", "Fiery Schezwan sauce tossed noodles", 169, "veg"),
        ("Chicken Schezwan Noodles", "Schezwan noodles loaded with chicken", 199, "non_veg"),
        ("Garlic Noodles", "Noodles tossed in aromatic garlic sauce", 159, "veg"),
    ],
    "Indian Curries": [
        ("Paneer Butter Masala", "Cottage cheese in a rich buttery tomato gravy", 219, "veg"),
        ("Kadai Paneer", "Paneer cooked with capsicum in kadai masala", 219, "veg"),
        ("Dal Makhani", "Slow-cooked black lentils in a creamy gravy", 179, "veg"),
        ("Malai Kofta", "Fried veg-paneer dumplings in creamy gravy", 229, "veg"),
        ("Butter Chicken", "Classic chicken curry in a rich tomato-butter gravy", 279, "non_veg"),
        ("Chicken Tikka Masala", "Grilled chicken tikka in a spiced curry", 279, "non_veg"),
        ("Kadai Chicken", "Chicken cooked with capsicum in kadai masala", 269, "non_veg"),
        ("Mutton Rogan Josh", "Aromatic Kashmiri-style mutton curry", 329, "non_veg"),
    ],
    "Indian Breads": [
        ("Plain Naan", "Soft leavened bread baked in the tandoor", 39, "veg"),
        ("Butter Naan", "Tandoori naan brushed with butter", 49, "veg"),
        ("Garlic Naan", "Naan topped with garlic and coriander", 59, "veg"),
        ("Tandoori Roti", "Whole wheat bread baked in the tandoor", 29, "veg"),
        ("Laccha Paratha", "Multi-layered crispy whole wheat paratha", 49, "veg"),
        ("Aloo Paratha", "Stuffed potato paratha served with curd", 79, "veg"),
    ],
    "South Indian": [
        ("Idli (4 pcs)", "Steamed rice cakes served with chutney and sambar", 79, "veg"),
        ("Medu Vada (3 pcs)", "Crispy fried lentil doughnuts", 89, "veg"),
        ("Plain Dosa", "Crispy rice-and-lentil crepe", 89, "veg"),
        ("Masala Dosa", "Crispy dosa stuffed with spiced potato filling", 119, "veg"),
        ("Onion Rava Dosa", "Crispy semolina dosa loaded with onions", 139, "veg"),
        ("Mysore Masala Dosa", "Spicy red chutney dosa with potato filling", 139, "veg"),
        ("Pesarattu", "Green gram dosa, a healthy Andhra breakfast", 99, "veg"),
        ("Curd Rice", "Comforting rice tempered and mixed with curd", 99, "veg"),
    ],
    "Chinese": [
        ("Veg Manchurian", "Fried veg balls tossed in Manchurian sauce", 179, "veg"),
        ("Chilli Mushroom", "Mushrooms tossed in spicy chilli sauce", 199, "veg"),
        ("Sweet Corn Soup", "Comforting sweet corn and vegetable soup", 99, "veg"),
        ("Hot & Sour Soup", "Tangy and spicy vegetable soup", 109, "veg"),
        ("Chicken Manchow Soup", "Spicy chicken soup with crispy noodles", 139, "non_veg"),
        ("Chicken Hot & Sour Soup", "Tangy chicken soup with a spicy kick", 139, "non_veg"),
    ],
    "Desserts": [
        ("Chocolate Brownie", "Warm fudgy brownie with a chocolate drizzle", 129, "veg"),
        ("Chocolate Lava Cake", "Molten chocolate cake served warm", 149, "veg"),
        ("Red Velvet Cake Slice", "Classic red velvet with cream cheese frosting", 139, "veg"),
        ("Gulab Jamun (2 pcs)", "Soft milk-solid dumplings in sugar syrup", 79, "veg"),
        ("Rasmalai (2 pcs)", "Soft paneer discs in saffron milk", 99, "veg"),
        ("Kulfi Stick", "Traditional Indian frozen milk dessert", 69, "veg"),
        ("Falooda", "Rose-flavoured dessert drink with vermicelli and ice cream", 129, "veg"),
    ],
    "Cold Drinks": [
        ("Coke", "Chilled 300ml soft drink", 49, "veg"),
        ("Sprite", "Chilled 300ml lemon soft drink", 49, "veg"),
        ("Fresh Lime Soda", "Refreshing lime soda, sweet or salted", 59, "veg"),
        ("Mineral Water", "500ml packaged drinking water", 29, "veg"),
        ("Mango Juice", "Fresh seasonal mango juice", 79, "veg"),
    ],
    "Milkshakes": [
        ("Vanilla Milkshake", "Creamy classic vanilla milkshake", 99, "veg"),
        ("Chocolate Milkshake", "Rich chocolate milkshake", 109, "veg"),
        ("Oreo Milkshake", "Milkshake blended with Oreo cookies", 129, "veg"),
        ("Mango Milkshake", "Seasonal mango blended with milk", 119, "veg"),
        ("Brownie Milkshake", "Chocolate milkshake topped with brownie bits", 149, "veg"),
    ],
    "Tea & Coffee": [
        ("Masala Tea", "Spiced Indian milk tea", 39, "veg"),
        ("Filter Coffee", "South Indian style strong filter coffee", 49, "veg"),
        ("Cold Coffee", "Chilled blended coffee with ice cream", 99, "veg"),
        ("Cappuccino", "Espresso topped with steamed milk foam", 109, "veg"),
        ("Green Tea", "Light and refreshing antioxidant-rich tea", 49, "veg"),
    ],
    "Healthy Food": [
        ("Greek Salad", "Fresh cucumber, tomato, olives and feta", 179, "veg"),
        ("Fruit Bowl", "Assorted seasonal fresh cut fruits", 129, "veg"),
        ("Sprouts Salad", "Protein-rich mixed sprouts salad", 119, "veg"),
        ("Grilled Paneer Salad", "Grilled paneer over fresh mixed greens", 199, "veg"),
        ("Grilled Chicken Salad", "Grilled chicken breast over mixed greens", 229, "non_veg"),
        ("Quinoa Protein Bowl", "Quinoa, chickpeas and roasted vegetables", 219, "veg"),
        ("Oats Smoothie Bowl", "Oats blended with banana and berries", 159, "veg"),
    ],
}


def seed():
    init_db()
    conn = get_db()

    # Wipe existing data so the script is safely re-runnable.
    for table in ["order_items", "orders", "cart_items", "favorites", "food_items", "categories", "restaurants"]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()

    category_ids = {}
    for name, icon in CATEGORIES:
        cur = conn.execute("INSERT INTO categories (name, icon) VALUES (?, ?)", (name, icon))
        category_ids[name] = cur.lastrowid

    for name, location, cuisine, rating, delivery_time, image, veg_only, served_categories in RESTAURANTS:
        cur = conn.execute(
            """INSERT INTO restaurants (name, location, cuisine, rating, delivery_time, image, veg_only)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, location, cuisine, rating, delivery_time, image, veg_only),
        )
        restaurant_id = cur.lastrowid

        for cat_name in served_categories:
            category_id = category_ids[cat_name]
            for item_name, description, price, food_type in FOOD_BY_CATEGORY.get(cat_name, []):
                if veg_only and food_type == "non_veg":
                    continue
                rating_val = round(3.8 + (hash(item_name + name) % 12) / 10, 1)  # 3.8 - 4.9 deterministic spread
                conn.execute(
                    """INSERT INTO food_items
                       (restaurant_id, category_id, name, description, price, rating, food_type, image_url, is_available)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                    (restaurant_id, category_id, item_name, description, price, rating_val, food_type, img(item_name)),
                )

    conn.commit()

    food_count = conn.execute("SELECT COUNT(*) AS c FROM food_items").fetchone()["c"]
    rest_count = conn.execute("SELECT COUNT(*) AS c FROM restaurants").fetchone()["c"]
    cat_count = conn.execute("SELECT COUNT(*) AS c FROM categories").fetchone()["c"]
    conn.close()

    print(f"Seeded {cat_count} categories, {rest_count} restaurants, {food_count} food items.")


if __name__ == "__main__":
    seed()
