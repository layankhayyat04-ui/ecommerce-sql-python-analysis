"""
Generate a realistic synthetic e-commerce dataset modeled on the structure
of the Olist Brazilian E-Commerce dataset: customers, orders, order_items,
products, payments, reviews. Used for a SQL + Python analysis project.
"""
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

random.seed(42)
np.random.seed(42)
fake = Faker()
Faker.seed(42)

N_CUSTOMERS = 3000
N_PRODUCTS = 250
N_ORDERS = 12000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

STATES = ["Amman", "Irbid", "Zarqa", "Aqaba", "Madaba", "Karak", "Salt", "Mafraq"]
STATE_WEIGHTS = [0.42, 0.14, 0.13, 0.09, 0.06, 0.06, 0.05, 0.05]

CATEGORIES = {
    "Electronics": (40, 900),
    "Home & Kitchen": (10, 250),
    "Fashion": (8, 180),
    "Beauty & Personal Care": (5, 90),
    "Sports & Outdoors": (12, 300),
    "Books & Stationery": (3, 60),
    "Toys & Games": (6, 150),
    "Groceries": (2, 40),
    "Furniture": (60, 1200),
    "Mobile Accessories": (4, 120),
}

PAYMENT_TYPES = ["credit_card", "cash_on_delivery", "wallet", "bank_transfer"]
PAYMENT_WEIGHTS = [0.45, 0.35, 0.13, 0.07]

ORDER_STATUS = ["delivered", "delivered", "delivered", "delivered", "shipped", "canceled"]

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days), seconds=random.randint(0, 86399))

# ---------- customers ----------
customers = []
for i in range(1, N_CUSTOMERS + 1):
    signup = random_date(START_DATE, END_DATE - timedelta(days=1))
    state = np.random.choice(STATES, p=STATE_WEIGHTS)
    customers.append({
        "customer_id": i,
        "customer_city": state,
        "signup_date": signup.date().isoformat(),
    })
customers_df = pd.DataFrame(customers)

# ---------- products ----------
products = []
cat_list = list(CATEGORIES.keys())
for i in range(1, N_PRODUCTS + 1):
    cat = random.choice(cat_list)
    lo, hi = CATEGORIES[cat]
    price = round(np.random.uniform(lo, hi), 2)
    weight_g = random.randint(100, 8000)
    products.append({
        "product_id": i,
        "category": cat,
        "unit_price": price,
        "weight_g": weight_g,
    })
products_df = pd.DataFrame(products)

# category popularity skew (some categories sell far more)
cat_pop = {
    "Electronics": 0.18, "Home & Kitchen": 0.15, "Fashion": 0.14,
    "Beauty & Personal Care": 0.10, "Sports & Outdoors": 0.09,
    "Books & Stationery": 0.06, "Toys & Games": 0.07, "Groceries": 0.09,
    "Furniture": 0.05, "Mobile Accessories": 0.07,
}
products_df["_pop"] = products_df["category"].map(cat_pop)
products_df["_pop"] = products_df["_pop"] / products_df.groupby("category")["_pop"].transform("count")

# ---------- orders, order_items, payments, reviews ----------
orders, order_items, payments, reviews = [], [], [], []
item_id_counter = 1

# give customers repeat-purchase tendency: 30% are "loyal" (3-8 orders), rest 1-2
customer_ids = customers_df["customer_id"].tolist()
loyal_customers = set(np.random.choice(customer_ids, size=int(N_CUSTOMERS * 0.3), replace=False))

order_id = 1
orders_needed = N_ORDERS
# assign order counts per customer
order_counts = {}
remaining = orders_needed
for cid in customer_ids:
    if remaining <= 0:
        order_counts[cid] = 0
        continue
    if cid in loyal_customers:
        c = min(random.randint(3, 8), remaining)
    else:
        c = min(random.choice([1, 1, 1, 2]), remaining)
    order_counts[cid] = c
    remaining -= c

# distribute leftover orders randomly among customers
leftover = remaining
while leftover > 0:
    cid = random.choice(customer_ids)
    order_counts[cid] += 1
    leftover -= 1

for cid in customer_ids:
    n_orders_for_cust = order_counts[cid]
    signup = datetime.fromisoformat(customers_df.loc[customers_df.customer_id == cid, "signup_date"].values[0])
    for _ in range(n_orders_for_cust):
        order_date = random_date(max(signup, START_DATE), END_DATE)
        status = random.choice(ORDER_STATUS)
        delivery_days = np.random.gamma(shape=2.2, scale=2.3)  # right-skewed, realistic
        delivery_days = max(1, round(delivery_days))
        delivered_date = order_date + timedelta(days=delivery_days) if status == "delivered" else None

        orders.append({
            "order_id": order_id,
            "customer_id": cid,
            "order_date": order_date.isoformat(),
            "status": status,
            "delivery_days": delivery_days if status == "delivered" else None,
        })

        # 1-4 items per order
        n_items = np.random.choice([1, 2, 3, 4], p=[0.55, 0.27, 0.12, 0.06])
        chosen_products = products_df.sample(n=n_items, weights=products_df["_pop"], replace=False)
        order_total = 0
        for _, prod in chosen_products.iterrows():
            qty = np.random.choice([1, 1, 1, 2, 3], p=[0.6, 0.15, 0.15, 0.06, 0.04])
            item_price = prod["unit_price"]
            freight = round(item_price * random.uniform(0.03, 0.12), 2)
            order_items.append({
                "order_item_id": item_id_counter,
                "order_id": order_id,
                "product_id": int(prod["product_id"]),
                "quantity": int(qty),
                "price": item_price,
                "freight_value": freight,
            })
            order_total += item_price * qty + freight
            item_id_counter += 1

        # payment
        p_type = np.random.choice(PAYMENT_TYPES, p=PAYMENT_WEIGHTS)
        installments = 1
        if p_type == "credit_card":
            installments = np.random.choice([1, 2, 3, 6, 12], p=[0.4, 0.2, 0.15, 0.15, 0.1])
        payments.append({
            "order_id": order_id,
            "payment_type": p_type,
            "installments": int(installments),
            "payment_value": round(order_total, 2),
        })

        # review (only for delivered/shipped, not all orders reviewed)
        if status in ("delivered", "shipped") and random.random() < 0.72:
            if status == "delivered" and delivery_days is not None:
                # later delivery -> lower review score tendency
                base = 5 - (delivery_days / 10)
                score = int(np.clip(round(np.random.normal(base, 1.1)), 1, 5))
            else:
                score = int(np.clip(round(np.random.normal(3.5, 1.3)), 1, 5))
            reviews.append({
                "order_id": order_id,
                "review_score": score,
            })

        order_id += 1

orders_df = pd.DataFrame(orders)
order_items_df = pd.DataFrame(order_items)
payments_df = pd.DataFrame(payments)
reviews_df = pd.DataFrame(reviews)
products_df = products_df.drop(columns=["_pop"])

# save
customers_df.to_csv("data/customers.csv", index=False)
products_df.to_csv("data/products.csv", index=False)
orders_df.to_csv("data/orders.csv", index=False)
order_items_df.to_csv("data/order_items.csv", index=False)
payments_df.to_csv("data/payments.csv", index=False)
reviews_df.to_csv("data/reviews.csv", index=False)

print("customers:", customers_df.shape)
print("products:", products_df.shape)
print("orders:", orders_df.shape)
print("order_items:", order_items_df.shape)
print("payments:", payments_df.shape)
print("reviews:", reviews_df.shape)
