import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="My Grocery Price Comparison", layout="wide")
st.title("🛒 My Grocery Price Comparison")
st.caption(f"Today's Date: {date.today().strftime('%B %d, %Y')}  |  📍 Pitampura, Delhi")

# ── Data Sources ──────────────────────────────────────────────
ZEPTO_AMUL_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDAetLFaeTn1trZbsLPN-wqn9byblmXLo_iHS597RWqsPO1N_qLGwNLVXWoPPNvqYDe9_zXtCo-PRn/pub?gid=1642078610&single=true&output=csv"
ZEPTO_PATANJALI_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDAetLFaeTn1trZbsLPN-wqn9byblmXLo_iHS597RWqsPO1N_qLGwNLVXWoPPNvqYDe9_zXtCo-PRn/pub?gid=270544794&single=true&output=csv"
ZEPTO_MOTHERDAIRY_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDAetLFaeTn1trZbsLPN-wqn9byblmXLo_iHS597RWqsPO1N_qLGwNLVXWoPPNvqYDe9_zXtCo-PRn/pub?gid=1208748990&single=true&output=csv"
BLINKIT_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDAetLFaeTn1trZbsLPN-wqn9byblmXLo_iHS597RWqsPO1N_qLGwNLVXWoPPNvqYDe9_zXtCo-PRn/pub?gid=471874080&single=true&output=csv"

# ── Product Map ───────────────────────────────────────────────
PRODUCTS = [
    {
        "label": "Amul Pure Ghee",
        "pack": "1L",
        "zepto_url": ZEPTO_AMUL_URL,
        "zepto_name": "Amul Pure Ghee",
        "zepto_unit": "LITER",
        "blinkit_name": "Amul Pure Ghee",
    },
    {
        "label": "Amul Cow Ghee",
        "pack": "1L",
        "zepto_url": ZEPTO_AMUL_URL,
        "zepto_name": "Amul Cow Ghee",
        "zepto_unit": "LITER",
        "blinkit_name": "Amul Cow Ghee",
    },
    {
        "label": "Patanjali Cow Ghee",
        "pack": "1L",
        "zepto_url": ZEPTO_PATANJALI_URL,
        "zepto_name": "Patanjali Cow Ghee",
        "zepto_unit": "LITER",
        "blinkit_name": "Patanjali Cow Ghee (1 l)",
    },
    {
        "label": "Mother Dairy Cow Ghee",
        "pack": "1L",
        "zepto_url": ZEPTO_MOTHERDAIRY_URL,
        "zepto_name": "Mother Dairy Cow Ghee",
        "zepto_unit": "LITER",
        "blinkit_name": "Mother Dairy Cow Ghee",
    },
]

def get_zepto_data(df, search_name, unit):
    """Get price and stock status from Zepto regardless of stock"""
    if search_name is None:
        return None, None
    match = df[
        df['name'].str.contains(search_name, case=False, na=False, regex=False) &
        df['unit_of_measure'].str.upper().eq(unit.upper())
    ]
    if match.empty:
        return None, None
    row = match.iloc[0]
    price = row['price']
    in_stock = not row['out_of_stock']
    return price, in_stock

def get_blinkit_data(df, search_name):
    """Get price and stock status from Blinkit regardless of stock"""
    if search_name is None:
        return None, None
    match = df[
        df['name'].str.contains(search_name, case=False, na=False, regex=False)
    ]
    if match.empty:
        return None, None
    row = match.iloc[0]
    price = row['price']
    in_stock = bool(row['in_stock'])
    return price, in_stock

try:
    # Load all sheets
    blinkit_df = pd.read_csv(BLINKIT_URL)
    zepto_amul_df = pd.read_csv(ZEPTO_AMUL_URL)
    zepto_patanjali_df = pd.read_csv(ZEPTO_PATANJALI_URL)
    zepto_motherdairy_df = pd.read_csv(ZEPTO_MOTHERDAIRY_URL)

    zepto_df_map = {
        ZEPTO_AMUL_URL: zepto_amul_df,
        ZEPTO_PATANJALI_URL: zepto_patanjali_df,
        ZEPTO_MOTHERDAIRY_URL: zepto_motherdairy_df,
    }

    # Build comparison rows
    rows = []
    for p in PRODUCTS:
        zepto_df = zepto_df_map[p["zepto_url"]]
        zepto_price, zepto_in_stock = get_zepto_data(zepto_df, p["zepto_name"], p["zepto_unit"])
        blinkit_price, blinkit_in_stock = get_blinkit_data(blinkit_df, p["blinkit_name"])

        # Best deal based on price regardless of stock
        if zepto_price is None and blinkit_price is None:
            best_deal = "—"
        elif zepto_price is None:
            best_deal = "🟡 Blinkit"
        elif blinkit_price is None:
            best_deal = "🟣 Zepto"
        elif zepto_price < blinkit_price:
            best_deal = "🟣 Zepto"
        elif blinkit_price < zepto_price:
            best_deal = "🟡 Blinkit"
        else:
            best_deal = "🟰 Same price"

        rows.append({
            "Product": p["label"],
            "Pack Size": p["pack"],
            "Zepto (₹)": f"₹{int(zepto_price)}" if zepto_price is not None else "—",
            "Zepto Stock": "✅ In Stock" if zepto_in_stock else "❌ Out of Stock",
            "Blinkit (₹)": f"₹{int(blinkit_price)}" if blinkit_price is not None else "—",
            "Blinkit Stock": "✅ In Stock" if blinkit_in_stock else "❌ Out of Stock",
            "Best Deal On": best_deal,
        })

    result_df = pd.DataFrame(rows)

    # Best deal banner — based on all prices regardless of stock
    all_prices = []
    for r in rows:
        if r["Zepto (₹)"] != "—":
            all_prices.append((r["Product"], r["Pack Size"], float(r["Zepto (₹)"].replace("₹","")), "Zepto 🟣", r["Zepto Stock"]))
        if r["Blinkit (₹)"] != "—":
            all_prices.append((r["Product"], r["Pack Size"], float(r["Blinkit (₹)"].replace("₹","")), "Blinkit 🟡", r["Blinkit Stock"]))

    if all_prices:
        best = min(all_prices, key=lambda x: x[2])
        st.success(f"**Best deal today:** {best[0]} ({best[1]}) on **{best[3]}** at **₹{int(best[2])}** — {best[4]}")

    st.subheader("📊 Ghee Price Comparison — Zepto vs Blinkit")
    st.dataframe(result_df, use_container_width=True, hide_index=True)

    st.caption("⏱ Prices update automatically every day at 8:00 AM. Out of Stock items update when back in stock.")

except Exception as e:
    st.error("Couldn't load data. Please check your internet connection.")
    st.info(f"Technical details: {e}")