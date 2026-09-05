<img width="100%" src="https://raw.githubusercontent.com/layankhayyat04-ui/ecommerce-sql-python-analysis/main/assets/banner.svg" alt="banner"/>

<p align="center">
  <img src="https://img.shields.io/badge/status-complete-134E5E?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
</p>

Analysis of 12,000 e-commerce orders across 3,000 customers and 250 products, using SQL for data extraction and Python for statistical analysis and visualization. The project answers 8 core business questions covering revenue trends, regional performance, product profitability, customer retention, delivery performance, and payment behavior.

<p align="center">
  <a href="SQL/Ecommerce_Analysis_Report.pdf"><img src="https://img.shields.io/badge/📄_FULL_REPORT-134E5E?style=for-the-badge"/></a>
</p>

---

### 🔍 Key Findings

| Finding | Detail |
|---|---|
| 👥 **Repeat customers drive revenue** | Under a third of the customer base generates **~92% of total revenue** |
| ⏱️ **Delivery speed hurts reviews** | Orders delivered in 15+ days saw review scores drop over a full point (**4.46 → 3.09 / 5**) |
| 💻 **Electronics leads revenue** | Highest revenue category despite not having the highest unit volume |

### 🛠️ Tech Stack

<p align="center">
<code><img height="32" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/python/python.png"></code>&nbsp;
<code><img height="32" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/sqlite/sqlite.png"></code>&nbsp;
<code><img height="32" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/pandas/pandas.png"></code>
</p>

- **SQL (SQLite)** — joins, CTEs, conditional aggregation across a 6-table relational schema
- **Python (pandas, matplotlib)** — data pipeline from raw query output to styled visualizations

### 📁 Repository Contents

| File | Description |
|---|---|
| `SQL/Ecommerce_Analysis_Report.pdf` | Full business report with findings & recommendations |
| `SQL/analysis_queries.sql` | All 8 SQL analysis queries |
| `SQL/analysis.py` | Python pipeline: runs queries, generates charts |
| `SQL/generate_data.py` | Builds the synthetic dataset |
| `SQL/load_db.py` | Loads CSVs into SQLite |
| `SQL/*.csv` | Source data (customers, orders, products, payments, reviews) |

### 🧬 Data Model

Six linked tables — `customers`, `orders`, `order_items`, `products`, `payments`, `reviews` — joined primarily through `order_id` and `customer_id`.

### ▶️ Running Locally

```bash
cd SQL
python load_db.py      # loads CSVs into SQLite
python analysis.py      # runs the 8 queries and generates charts
```
