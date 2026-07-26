"""
E-Commerce Sales & Customer Analysis
Runs the SQL queries against ecommerce.db, then uses pandas/matplotlib
for further analysis and chart generation.
"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

conn = sqlite3.connect("ecommerce.db")
plt.rcParams["font.family"] = "DejaVu Sans"

# Brand palette
NAVY = "#1B2A4A"
TEAL = "#2E8B8B"
GOLD = "#C9A24B"
GRAY = "#8A8F98"
LIGHT_BG = "#F4F5F7"
PALETTE = [NAVY, TEAL, GOLD, "#6B8CAE", "#A85751", GRAY, "#5C7A5C", "#B08968", "#7C6A9C", "#4A6670"]

def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.tick_params(colors="#444444")
    ax.grid(axis="y", color="#E5E5E5", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

# ============================================================
# Q1: Monthly revenue trend
# ============================================================
q1 = pd.read_sql_query("""
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        ROUND(SUM(p.payment_value), 2) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(p.payment_value) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.status = 'delivered'
    GROUP BY month
    ORDER BY month
""", conn)
q1.to_csv("outputs/q1_monthly_revenue.csv", index=False)

fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.bar(q1["month"], q1["total_revenue"], color=TEAL, alpha=0.85, zorder=3, label="Revenue")
ax1.set_ylabel("Total Revenue (JOD)", color=NAVY, fontsize=11)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
style_ax(ax1)
plt.xticks(rotation=45, ha="right", fontsize=9)
ax2 = ax1.twinx()
ax2.plot(q1["month"], q1["order_count"], color=GOLD, marker="o", linewidth=2.2, zorder=4, label="Order Count")
ax2.set_ylabel("Order Count", color=GOLD, fontsize=11)
ax2.spines["top"].set_visible(False)
fig.suptitle("Monthly Revenue and Order Volume Trend", fontsize=13, fontweight="bold", color=NAVY, y=0.98)
ax1.set_title("Delivered orders, Jan 2023 – Dec 2024", fontsize=9.5, color=GRAY, loc="left", pad=8)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False, fontsize=9)
plt.tight_layout()
plt.savefig("outputs/chart_01_monthly_revenue.png", dpi=200, facecolor="white")
plt.close()

# ============================================================
# Q2: Revenue by city
# ============================================================
q2 = pd.read_sql_query("""
    SELECT
        c.customer_city,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(p.payment_value), 2) AS total_revenue,
        ROUND(AVG(p.payment_value), 2) AS avg_order_value
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.status = 'delivered'
    GROUP BY c.customer_city
    ORDER BY total_revenue DESC
""", conn)
q2.to_csv("outputs/q2_revenue_by_city.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5.5))
q2_sorted = q2.sort_values("total_revenue")
bars = ax.barh(q2_sorted["customer_city"], q2_sorted["total_revenue"], color=NAVY, zorder=3)
bars[len(bars)-1].set_color(GOLD)
ax.set_xlabel("Total Revenue (JOD)", fontsize=11)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
style_ax(ax)
ax.spines["left"].set_visible(False)
ax.grid(axis="x", color="#E5E5E5", linewidth=0.8, zorder=0)
fig.suptitle("Revenue by City", fontsize=13, fontweight="bold", color=NAVY, y=0.98)
ax.set_title("Delivered orders, all-time", fontsize=9.5, color=GRAY, loc="left", pad=8)
plt.tight_layout()
plt.savefig("outputs/chart_02_revenue_by_city.png", dpi=200, facecolor="white")
plt.close()

# ============================================================
# Q3: Category revenue
# ============================================================
q3 = pd.read_sql_query("""
    SELECT
        pr.category,
        COUNT(oi.order_item_id) AS units_sold,
        ROUND(SUM(oi.price * oi.quantity), 2) AS category_revenue,
        ROUND(AVG(oi.price), 2) AS avg_unit_price
    FROM order_items oi
    JOIN products pr ON oi.product_id = pr.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'delivered'
    GROUP BY pr.category
    ORDER BY category_revenue DESC
""", conn)
q3.to_csv("outputs/q3_category_revenue.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5.5))
colors = [PALETTE[i % len(PALETTE)] for i in range(len(q3))]
ax.bar(q3["category"], q3["category_revenue"], color=colors, zorder=3)
ax.set_ylabel("Revenue (JOD)", fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
style_ax(ax)
plt.xticks(rotation=40, ha="right", fontsize=9)
fig.suptitle("Revenue by Product Category", fontsize=13, fontweight="bold", color=NAVY, y=0.98)
ax.set_title("Delivered orders, all-time", fontsize=9.5, color=GRAY, loc="left", pad=8)
plt.tight_layout()
plt.savefig("outputs/chart_03_category_revenue.png", dpi=200, facecolor="white")
plt.close()

# ============================================================
# Q4: Repeat vs one-time customers
# ============================================================
q4 = pd.read_sql_query("""
    WITH customer_orders AS (
        SELECT
            o.customer_id,
            COUNT(DISTINCT o.order_id) AS n_orders,
            SUM(p.payment_value) AS total_spent
        FROM orders o
        JOIN payments p ON o.order_id = p.order_id
        WHERE o.status = 'delivered'
        GROUP BY o.customer_id
    )
    SELECT
        CASE WHEN n_orders > 1 THEN 'Repeat Customer' ELSE 'One-Time Customer' END AS customer_type,
        COUNT(*) AS num_customers,
        ROUND(AVG(total_spent), 2) AS avg_lifetime_spend,
        ROUND(SUM(total_spent), 2) AS total_revenue_contribution
    FROM customer_orders
    GROUP BY customer_type
""", conn)
q4.to_csv("outputs/q4_repeat_customers.csv", index=False)

fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
colors4 = [TEAL, GRAY]
axes[0].pie(q4["num_customers"], labels=q4["customer_type"], autopct="%1.0f%%",
            colors=colors4, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 9.5})
axes[0].set_title("Share of Customers", fontsize=10.5, color=NAVY, pad=10)

axes[1].pie(q4["total_revenue_contribution"], labels=q4["customer_type"], autopct="%1.0f%%",
            colors=colors4, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 9.5})
axes[1].set_title("Share of Revenue", fontsize=10.5, color=NAVY, pad=10)

fig.suptitle("Repeat vs. One-Time Customers", fontsize=13, fontweight="bold", color=NAVY, y=1.02)
plt.tight_layout()
plt.savefig("outputs/chart_04_repeat_customers.png", dpi=200, facecolor="white", bbox_inches="tight")
plt.close()

# ============================================================
# Q5: Delivery speed vs review score
# ============================================================
q5 = pd.read_sql_query("""
    SELECT
        CASE
            WHEN o.delivery_days <= 3 THEN '1-3 days'
            WHEN o.delivery_days <= 7 THEN '4-7 days'
            WHEN o.delivery_days <= 14 THEN '8-14 days'
            ELSE '15+ days'
        END AS delivery_bucket,
        COUNT(*) AS num_orders,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        MIN(o.delivery_days) as sort_key
    FROM orders o
    JOIN reviews r ON o.order_id = r.order_id
    WHERE o.status = 'delivered' AND o.delivery_days IS NOT NULL
    GROUP BY delivery_bucket
    ORDER BY sort_key
""", conn)
q5 = q5.drop(columns=["sort_key"])
q5.to_csv("outputs/q5_delivery_vs_reviews.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(q5["delivery_bucket"], q5["avg_review_score"], color=[TEAL, NAVY, GOLD, "#A85751"], zorder=3, width=0.6)
for bar, val in zip(bars, q5["avg_review_score"]):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.05, f"{val}", ha="center", fontsize=10, fontweight="bold", color=NAVY)
ax.set_ylabel("Average Review Score (1-5)", fontsize=11)
ax.set_ylim(0, 5.5)
style_ax(ax)
fig.suptitle("Delivery Speed vs. Customer Satisfaction", fontsize=13, fontweight="bold", color=NAVY, y=0.98)
ax.set_title("Average review score by delivery time bucket", fontsize=9.5, color=GRAY, loc="left", pad=8)
plt.tight_layout()
plt.savefig("outputs/chart_05_delivery_vs_reviews.png", dpi=200, facecolor="white")
plt.close()

# ============================================================
# Q6: Payment method preferences
# ============================================================
q6 = pd.read_sql_query("""
    SELECT
        payment_type,
        COUNT(*) AS num_orders,
        ROUND(AVG(payment_value), 2) AS avg_order_value,
        ROUND(SUM(payment_value), 2) AS total_value
    FROM payments
    GROUP BY payment_type
    ORDER BY total_value DESC
""", conn)
q6.to_csv("outputs/q6_payment_methods.csv", index=False)

fig, ax = plt.subplots(figsize=(8.5, 5))
x = np.arange(len(q6))
width = 0.38
ax2 = ax.twinx()
b1 = ax.bar(x - width/2, q6["num_orders"], width, color=NAVY, zorder=3, label="Order Count")
b2 = ax2.bar(x + width/2, q6["avg_order_value"], width, color=GOLD, zorder=3, label="Avg Order Value")
ax.set_xticks(x)
ax.set_xticklabels([p.replace("_", " ").title() for p in q6["payment_type"]], fontsize=9.5)
ax.set_ylabel("Order Count", color=NAVY, fontsize=11)
ax2.set_ylabel("Avg Order Value (JOD)", color=GOLD, fontsize=11)
style_ax(ax)
ax2.spines["top"].set_visible(False)
fig.suptitle("Payment Method Usage and Order Value", fontsize=13, fontweight="bold", color=NAVY, y=0.98)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=False, fontsize=9)
plt.tight_layout()
plt.savefig("outputs/chart_06_payment_methods.png", dpi=200, facecolor="white")
plt.close()

# ============================================================
# Q7: Top 10 products
# ============================================================
q7 = pd.read_sql_query("""
    SELECT
        oi.product_id,
        pr.category,
        ROUND(SUM(oi.price * oi.quantity), 2) AS product_revenue,
        SUM(oi.quantity) AS units_sold
    FROM order_items oi
    JOIN products pr ON oi.product_id = pr.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'delivered'
    GROUP BY oi.product_id
    ORDER BY product_revenue DESC
    LIMIT 10
""", conn)
q7.to_csv("outputs/q7_top_products.csv", index=False)

# ============================================================
# Q8: Cancellation rate by city
# ============================================================
q8 = pd.read_sql_query("""
    SELECT
        c.customer_city,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN o.status = 'canceled' THEN 1 ELSE 0 END) AS canceled_orders,
        ROUND(100.0 * SUM(CASE WHEN o.status = 'canceled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate_pct
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.customer_city
    ORDER BY cancellation_rate_pct DESC
""", conn)
q8.to_csv("outputs/q8_cancellation_by_city.csv", index=False)

fig, ax = plt.subplots(figsize=(8.5, 5))
q8_sorted = q8.sort_values("cancellation_rate_pct")
colors8 = [GOLD if v == q8["cancellation_rate_pct"].max() else GRAY for v in q8_sorted["cancellation_rate_pct"]]
ax.barh(q8_sorted["customer_city"], q8_sorted["cancellation_rate_pct"], color=colors8, zorder=3)
ax.set_xlabel("Cancellation Rate (%)", fontsize=11)
style_ax(ax)
ax.spines["left"].set_visible(False)
ax.grid(axis="x", color="#E5E5E5", linewidth=0.8, zorder=0)
fig.suptitle("Order Cancellation Rate by City", fontsize=13, fontweight="bold", color=NAVY, y=0.98)
plt.tight_layout()
plt.savefig("outputs/chart_08_cancellation_by_city.png", dpi=200, facecolor="white")
plt.close()

conn.close()

print("=== Q1: Monthly Revenue (head) ===")
print(q1.head())
print("\n=== Q2: Revenue by City ===")
print(q2)
print("\n=== Q3: Category Revenue ===")
print(q3)
print("\n=== Q4: Repeat Customers ===")
print(q4)
print("\n=== Q5: Delivery vs Reviews ===")
print(q5)
print("\n=== Q6: Payment Methods ===")
print(q6)
print("\n=== Q7: Top 10 Products ===")
print(q7)
print("\n=== Q8: Cancellation by City ===")
print(q8)
print("\nAll charts and CSVs saved to outputs/")
