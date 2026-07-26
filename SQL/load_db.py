import sqlite3
import pandas as pd

conn = sqlite3.connect("ecommerce.db")

tables = ["customers", "products", "orders", "order_items", "payments", "reviews"]
for t in tables:
    df = pd.read_csv(f"data/{t}.csv")
    df.to_sql(t, conn, if_exists="replace", index=False)
    print(f"Loaded {t}: {len(df)} rows")

# indexes for join performance
cur = conn.cursor()
cur.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
cur.execute("CREATE INDEX idx_items_order ON order_items(order_id)")
cur.execute("CREATE INDEX idx_items_product ON order_items(product_id)")
cur.execute("CREATE INDEX idx_payments_order ON payments(order_id)")
cur.execute("CREATE INDEX idx_reviews_order ON reviews(order_id)")
conn.commit()
conn.close()
print("Database built: ecommerce.db")
