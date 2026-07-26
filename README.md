SQL & Python: E-Commerce Sales Analysis

Analysis of 12,000 e-commerce orders across 3,000 customers and 250 products, using SQL for data extraction and Python for statistical analysis and visualization. The project answers 8 core business questions covering revenue trends, regional performance, product profitability, customer retention, delivery performance, and payment behavior.

📄 Full Report (PDF)

Key Findings
Repeat customers — under a third of the customer base — generate ~92% of total revenue
Orders delivered in 15+ days saw review scores drop over a full point (4.46 → 3.09 / 5)
Electronics led all categories in revenue despite not having the highest unit volume
Tech Stack
SQL (SQLite) — joins, CTEs, conditional aggregation across a 6-table relational schema
Python (pandas, matplotlib) — data pipeline from raw query output to styled visualizations
Repository Contents
File	Description
Ecommerce_Analysis_Report.pdf	Full business report with findings & recommendations
analysis_queries.sql	All 8 SQL analysis queries
analysis.py	Python pipeline: runs queries, generates charts
generate_data.py	Builds the synthetic dataset
load_db.py	Loads CSVs into SQLite
data/	Source CSVs (customers, orders, products, payments, reviews)
Data Model

Six linked tables: customers, orders, order_items, products, payments, reviews — joined primarily through order_id and customer_id.

Author: Layan Khayyat — BIT Student, Princess Sumaya University for Technology
