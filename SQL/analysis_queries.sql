-- ============================================================
-- E-COMMERCE SALES & CUSTOMER ANALYSIS
-- SQL Analysis Queries
-- Database: ecommerce.db (SQLite)
-- ============================================================

-- Q1: Monthly revenue trend (delivered orders only)
-- Business question: How has revenue evolved month over month?
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    ROUND(SUM(p.payment_value), 2) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(SUM(p.payment_value) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.status = 'delivered'
GROUP BY month
ORDER BY month;


-- Q2: Revenue and order volume by city
-- Business question: Which regions drive the most revenue?
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
ORDER BY total_revenue DESC;


-- Q3: Top-performing product categories by revenue
-- Business question: What should the business push more of?
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
ORDER BY category_revenue DESC;


-- Q4: Customer repeat-purchase rate
-- Business question: What share of customers are repeat buyers, and how much
-- more do they spend than one-time buyers?
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
GROUP BY customer_type;


-- Q5: Delivery performance vs customer satisfaction
-- Business question: Does slower delivery hurt review scores?
SELECT
    CASE
        WHEN o.delivery_days <= 3 THEN '1-3 days'
        WHEN o.delivery_days <= 7 THEN '4-7 days'
        WHEN o.delivery_days <= 14 THEN '8-14 days'
        ELSE '15+ days'
    END AS delivery_bucket,
    COUNT(*) AS num_orders,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM orders o
JOIN reviews r ON o.order_id = r.order_id
WHERE o.status = 'delivered' AND o.delivery_days IS NOT NULL
GROUP BY delivery_bucket
ORDER BY MIN(o.delivery_days);


-- Q6: Payment method preferences and average order value
-- Business question: How do customers prefer to pay, and does payment
-- method correlate with order size?
SELECT
    payment_type,
    COUNT(*) AS num_orders,
    ROUND(AVG(payment_value), 2) AS avg_order_value,
    ROUND(SUM(payment_value), 2) AS total_value
FROM payments
GROUP BY payment_type
ORDER BY total_value DESC;


-- Q7: Top 10 products by revenue (with category context)
-- Business question: Which individual SKUs are the biggest revenue drivers?
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
LIMIT 10;


-- Q8: Order cancellation rate by city
-- Business question: Are cancellations concentrated in specific regions?
SELECT
    c.customer_city,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN o.status = 'canceled' THEN 1 ELSE 0 END) AS canceled_orders,
    ROUND(100.0 * SUM(CASE WHEN o.status = 'canceled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_city
ORDER BY cancellation_rate_pct DESC;
