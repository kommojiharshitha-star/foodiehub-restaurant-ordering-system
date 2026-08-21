"""
recommendation.py
A real (non-hardcoded) content + collaborative-style recommendation engine.

Approach
--------
1. Build a profile of the user from their past orders:
     - favourite categories (by frequency)
     - favourite food_type (veg / non_veg / egg)
     - favourite restaurants
2. Score every food item NOT yet ordered by the user using a weighted
   formula that rewards:
     - category match with the user's top categories
     - food_type match
     - restaurant match
     - the item's own rating (quality signal)
3. Return the top-N scoring items as "Recommended For You".

If the user has no order history, fall back to a "Popular Near You"
style ranking purely on rating, so every user still gets a AI section.
"""

from collections import Counter
from database import get_db


def _get_user_order_history(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT f.id, f.category_id, f.food_type, f.restaurant_id, oi.quantity
           FROM order_items oi
           JOIN orders o ON oi.order_id = o.id
           JOIN food_items f ON oi.food_id = f.id
           WHERE o.user_id = ?""",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def _get_candidate_pool(exclude_food_ids):
    conn = get_db()
    if exclude_food_ids:
        placeholders = ",".join("?" for _ in exclude_food_ids)
        query = f"""SELECT f.*, r.name AS restaurant_name FROM food_items f
                    JOIN restaurants r ON f.restaurant_id = r.id
                    WHERE f.is_available = 1 AND f.id NOT IN ({placeholders})"""
        rows = conn.execute(query, exclude_food_ids).fetchall()
    else:
        rows = conn.execute(
            """SELECT f.*, r.name AS restaurant_name FROM food_items f
               JOIN restaurants r ON f.restaurant_id = r.id
               WHERE f.is_available = 1"""
        ).fetchall()
    conn.close()
    return rows


def build_user_profile(user_id):
    """Return dicts describing the user's category / type / restaurant weights."""
    history = _get_user_order_history(user_id)

    category_weight = Counter()
    type_weight = Counter()
    restaurant_weight = Counter()
    ordered_food_ids = set()

    for row in history:
        qty = row["quantity"] or 1
        category_weight[row["category_id"]] += qty
        type_weight[row["food_type"]] += qty
        restaurant_weight[row["restaurant_id"]] += qty
        ordered_food_ids.add(row["id"])

    return {
        "category_weight": category_weight,
        "type_weight": type_weight,
        "restaurant_weight": restaurant_weight,
        "ordered_food_ids": ordered_food_ids,
        "has_history": len(history) > 0,
    }


def recommend_for_user(user_id, limit=8):
    profile = build_user_profile(user_id)

    if not profile["has_history"]:
        # Cold start: no order history yet -> rating-based popular items.
        pool = _get_candidate_pool(exclude_food_ids=[])
        ranked = sorted(pool, key=lambda f: f["rating"], reverse=True)
        return ranked[:limit], "popular"

    pool = _get_candidate_pool(exclude_food_ids=list(profile["ordered_food_ids"]))

    max_cat = max(profile["category_weight"].values(), default=1)
    max_type = max(profile["type_weight"].values(), default=1)
    max_rest = max(profile["restaurant_weight"].values(), default=1)

    scored = []
    for food in pool:
        cat_score = profile["category_weight"].get(food["category_id"], 0) / max_cat
        type_score = profile["type_weight"].get(food["food_type"], 0) / max_type
        rest_score = profile["restaurant_weight"].get(food["restaurant_id"], 0) / max_rest
        rating_score = (food["rating"] or 0) / 5.0

        # Weighted blend: category preference matters most, then food type,
        # then restaurant loyalty, with item quality as a tie-breaker.
        total_score = (
            cat_score * 0.45
            + type_score * 0.25
            + rest_score * 0.15
            + rating_score * 0.15
        )
        scored.append((total_score, food))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = [food for score, food in scored[:limit] if score > 0]

    if len(top) < limit:
        # pad with top-rated items not already included
        seen_ids = {f["id"] for f in top}
        for score, food in scored:
            if food["id"] not in seen_ids:
                top.append(food)
                seen_ids.add(food["id"])
            if len(top) >= limit:
                break

    return top, "personalized"


def because_you_ordered(user_id, limit=6):
    """Pick the user's single most-ordered category and surface more of it."""
    profile = build_user_profile(user_id)
    if not profile["category_weight"]:
        return None, []

    top_category_id, _ = profile["category_weight"].most_common(1)[0]

    conn = get_db()
    category = conn.execute("SELECT * FROM categories WHERE id = ?", (top_category_id,)).fetchone()
    items = conn.execute(
        """SELECT f.*, r.name AS restaurant_name FROM food_items f
           JOIN restaurants r ON f.restaurant_id = r.id
           WHERE f.category_id = ? AND f.is_available = 1
           ORDER BY f.rating DESC LIMIT ?""",
        (top_category_id, limit),
    ).fetchall()
    conn.close()
    return category, items


def popular_near_you(limit=8):
    conn = get_db()
    rows = conn.execute(
        """SELECT f.*, r.name AS restaurant_name FROM food_items f
           JOIN restaurants r ON f.restaurant_id = r.id
           WHERE f.is_available = 1 ORDER BY f.rating DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return rows
