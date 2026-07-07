# Olist E-Commerce Analytics Dashboard

Interactive business analytics dashboard built on the Brazilian Olist e-commerce dataset (100K+ orders, 2016-2018) using SQL, Plotly, and Streamlit.

## Key metrics
- Total Revenue: R$ 15,375,875
- Total Orders: 96,211
- Avg Order Value: R$ 153.25
- Customer Retention Rate: 3.0%

## What it does
- Revenue and order trend analysis with dual-axis time series
- Customer cohort retention analysis and order frequency distribution
- Top seller performance ranking with review score vs volume scatter
- Product category revenue treemap with review score coloring

## Tech stack
| Component | Tool |
|---|---|
| Database | SQLite via SQLAlchemy |
| Queries | SQL (JOINs, CTEs, window aggregations) |
| Analysis | Pandas |
| Visualization | Plotly Express + Graph Objects |
| Dashboard | Streamlit |
| Dataset | Olist Brazilian E-Commerce (9 tables, 100K+ rows) |

## Setup

    git clone https://github.com/adityabandal21/olist-dashboard.git
    cd olist-dashboard
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    kaggle datasets download -d olistbr/brazilian-ecommerce -p data/ --unzip

## Run

    python -m streamlit run app.py

## Key findings
- Revenue grew 3x from Jan 2017 to Nov 2017 before seasonal dip
- Only 3% of customers make repeat purchases — typical for marketplace model
- Sao Paulo sellers generate 40%+ of total platform revenue
- Health & beauty and watches are top revenue categories
- Higher priced categories tend to have lower review scores

## Skills demonstrated
SQL joins and aggregations, SQLite, Pandas, Plotly, Streamlit, business KPI design, cohort analysis, data storytelling
