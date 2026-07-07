import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from load_data import load_database, query

st.set_page_config(page_title="Olist Analytics", page_icon="📊", layout="wide")

# Load DB on startup
@st.cache_resource
def init_db():
    return load_database()

init_db()

st.title("📊 Olist E-Commerce Analytics Dashboard")
st.caption("Brazilian e-commerce platform — 100K+ orders, 2016–2018")

tabs = st.tabs(["💰 Revenue & Orders", "👥 Customer Retention", "🏪 Seller Performance", "📦 Product Categories"])

# ── Tab 1: Revenue & Orders ──────────────────────────────────
with tabs[0]:
    st.subheader("Revenue & Order Trends")

    rev_df = query("""
        SELECT 
            strftime('%Y-%m', o.order_purchase_timestamp) AS month,
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(SUM(p.payment_value), 2) AS total_revenue,
            ROUND(AVG(p.payment_value), 2) AS avg_order_value
        FROM orders o
        JOIN order_payments p ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
          AND o.order_purchase_timestamp >= '2017-01-01'
        GROUP BY month
        ORDER BY month
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"R$ {rev_df['total_revenue'].sum():,.0f}")
    col2.metric("Total Orders", f"{rev_df['total_orders'].sum():,}")
    col3.metric("Avg Order Value", f"R$ {rev_df['avg_order_value'].mean():.2f}")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=rev_df['month'], y=rev_df['total_revenue'],
                         name='Revenue', marker_color='#378ADD'))
    fig.add_trace(go.Scatter(x=rev_df['month'], y=rev_df['total_orders'],
                              name='Orders', yaxis='y2', line=dict(color='#E24B4A', width=2)))
    fig.update_layout(
        title='Monthly Revenue and Order Volume',
        yaxis=dict(title='Revenue (R$)'),
        yaxis2=dict(title='Orders', overlaying='y', side='right'),
        legend=dict(x=0, y=1),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Order status breakdown
    status_df = query("""
        SELECT order_status, COUNT(*) as count
        FROM orders
        GROUP BY order_status
        ORDER BY count DESC
    """)
    fig2 = px.pie(status_df, values='count', names='order_status',
                  title='Order Status Distribution', hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 2: Customer Retention ────────────────────────────────
with tabs[1]:
    st.subheader("Customer Cohort Analysis")

    cohort_df = query("""
        SELECT
            c.customer_unique_id,
            strftime('%Y-%m', MIN(o.order_purchase_timestamp)) AS cohort_month,
            COUNT(DISTINCT o.order_id) AS total_orders
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id
    """)

    repeat_customers = (cohort_df['total_orders'] > 1).sum()
    total_customers = len(cohort_df)
    retention_rate = repeat_customers / total_customers * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Repeat Customers", f"{repeat_customers:,}")
    col3.metric("Retention Rate", f"{retention_rate:.1f}%")

    order_dist = cohort_df['total_orders'].value_counts().reset_index()
    order_dist.columns = ['orders_count', 'customers']
    order_dist = order_dist[order_dist['orders_count'] <= 5].sort_values('orders_count')
    fig = px.bar(order_dist, x='orders_count', y='customers',
                 title='Customer Order Frequency Distribution',
                 labels={'orders_count': 'Number of Orders', 'customers': 'Number of Customers'},
                 color='customers', color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

    monthly_new = cohort_df.groupby('cohort_month').size().reset_index(name='new_customers')
    monthly_new = monthly_new[monthly_new['cohort_month'] >= '2017-01']
    fig2 = px.bar(monthly_new, x='cohort_month', y='new_customers',
                  title='New Customers per Month',
                  color='new_customers', color_continuous_scale='Greens')
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 3: Seller Performance ────────────────────────────────
with tabs[2]:
    st.subheader("Top Seller Performance")

    seller_df = query("""
        SELECT
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(r.review_score), 2) AS avg_review,
            ROUND(AVG(oi.price), 2) AS avg_item_price
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY s.seller_id
        HAVING total_orders >= 50
        ORDER BY total_revenue DESC
        LIMIT 20
    """)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(seller_df.head(10), x='total_revenue', y='seller_id',
                     orientation='h', title='Top 10 Sellers by Revenue',
                     color='total_revenue', color_continuous_scale='Blues',
                     labels={'total_revenue': 'Revenue (R$)', 'seller_id': 'Seller ID'})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.scatter(seller_df, x='total_orders', y='avg_review',
                          size='total_revenue', color='avg_item_price',
                          title='Orders vs Review Score (size = revenue)',
                          labels={'total_orders': 'Total Orders', 'avg_review': 'Avg Review Score'},
                          color_continuous_scale='RdYlGn')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Seller State Distribution")
    state_df = query("""
        SELECT seller_state, COUNT(*) as seller_count,
               ROUND(SUM(oi.price), 2) as total_revenue
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        GROUP BY seller_state
        ORDER BY total_revenue DESC
    """)
    fig3 = px.bar(state_df.head(10), x='seller_state', y='total_revenue',
                  title='Revenue by Seller State',
                  color='total_revenue', color_continuous_scale='Blues')
    st.plotly_chart(fig3, use_container_width=True)

# ── Tab 4: Product Categories ────────────────────────────────
with tabs[3]:
    st.subheader("Product Category Analysis")

    cat_df = query("""
        SELECT
            COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(oi.price), 2) AS avg_price,
            ROUND(AVG(r.review_score), 2) AS avg_review
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN category_translation t ON p.product_category_name = t.product_category_name
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY category
        HAVING total_orders >= 100
        ORDER BY total_revenue DESC
        LIMIT 15
    """)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(cat_df, x='total_revenue', y='category',
                     orientation='h', title='Top Categories by Revenue',
                     color='total_revenue', color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.scatter(cat_df, x='avg_price', y='avg_review',
                          size='total_orders', color='total_revenue',
                          hover_name='category',
                          title='Price vs Review Score by Category',
                          color_continuous_scale='RdYlGn')
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.treemap(cat_df, path=['category'], values='total_revenue',
                      color='avg_review', color_continuous_scale='RdYlGn',
                      title='Revenue Treemap by Category (color = avg review score)')
    st.plotly_chart(fig3, use_container_width=True)
