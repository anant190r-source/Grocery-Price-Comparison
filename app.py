import streamlit as st
import pandas as pd
from datetime import date

# 1. Page Configuration and Titles
st.set_page_config(page_title="My Grocery Price Comparison", layout="wide")
st.title("My Grocery Price Comparison")
st.caption(f"Today's Date: {date.today().strftime('%B %d, %Y')}")

# 2. Data Source URLs
zepto_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDAetLFaeTn1trZbsLPN-wqn9byblmXLo_iHS597RWqsPO1N_qLGwNLVXWoPPNvqYDe9_zXtCo-PRn/pub?gid=270544794&single=true&output=csv"
blinkit_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDAetLFaeTn1trZbsLPN-wqn9byblmXLo_iHS597RWqsPO1N_qLGwNLVXWoPPNvqYDe9_zXtCo-PRn/pub?gid=471874080&single=true&output=csv"

try:
    # 3. Load Data Freshly
    zepto_cols = ['name', 'brand', 'price', 'mrp', 'formatted_packsize']
    blinkit_cols = ['name', 'brand', 'price', 'mrp', 'quantity']

    zepto_df = pd.read_csv(zepto_url, usecols=zepto_cols)
    blinkit_df = pd.read_csv(blinkit_url, usecols=blinkit_cols)

    # 4. Standardize Column Names
    zepto_df = zepto_df.rename(columns={
        'name': 'Name', 'brand': 'Brand', 'price': 'Price',
        'mrp': 'MRP', 'formatted_packsize': 'Pack Size'
    })

    blinkit_df = blinkit_df.rename(columns={
        'name': 'Name', 'brand': 'Brand', 'price': 'Price',
        'mrp': 'MRP', 'quantity': 'Pack Size'
    })

    # Order the columns nicely for the table view
    column_order = ['Name', 'Brand', 'Pack Size', 'Price', 'MRP']
    zepto_df = zepto_df[column_order]
    blinkit_df = blinkit_df[column_order]

    # 4b. Remove duplicate products (same item can appear under multiple search terms)
    zepto_df = zepto_df.drop_duplicates(subset=['Name', 'Pack Size', 'Price']).reset_index(drop=True)
    blinkit_df = blinkit_df.drop_duplicates(subset=['Name', 'Pack Size', 'Price']).reset_index(drop=True)

    # 5. Sort by Price (Lowest to Highest)
    zepto_df = zepto_df.sort_values(by='Price', ascending=True).reset_index(drop=True)
    blinkit_df = blinkit_df.sort_values(by='Price', ascending=True).reset_index(drop=True)

    # 6. Find the Absolute Cheapest Item
    cheapest_zepto = zepto_df.iloc[0]
    cheapest_blinkit = blinkit_df.iloc[0]

    if cheapest_zepto['Price'] <= cheapest_blinkit['Price']:
        best_item = cheapest_zepto
        platform = "Zepto"
    else:
        best_item = cheapest_blinkit
        platform = "Blinkit"

    st.success(f"**Cheapest Ghee:** {best_item['Name']} on **{platform}** - Rs.{best_item['Price']} for {best_item['Pack Size']}")

    # 7. Display Side-by-Side Tables
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Zepto - Ghee")
        st.dataframe(zepto_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Blinkit - Ghee")
        st.dataframe(blinkit_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Oops! We couldn't load the live data. Please check your internet connection or verify that the Google Sheets links are still active.")
    st.info(f"Technical details: {e}")
