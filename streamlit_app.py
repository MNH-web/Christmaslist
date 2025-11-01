import streamlit as st
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Price Tracker", page_icon="💸", layout="wide")
st.title("💸 Price Tracker")
st.caption("Add items and track their current prices — works great on iPhone.")

DATA_FILE = "tracked_items.csv"

# Load or initialize data
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "Name", "URL", "Category/Notes",
        "Target Price (£)", "Current Price (£)",
        "Price Change", "Alert", "Date Added"
    ])

# --- Add new item ---
with st.form("add_item"):
    name = st.text_input("Product name")
    url = st.text_input("Product URL")
    category = st.text_input("Category or notes", placeholder="e.g. Gaming, Smart Home…")
    target = st.number_input("Target/Highest Price (£)", min_value=0.0, step=0.5)
    submitted = st.form_submit_button("Add Item")
    if submitted and name and url:
        df.loc[len(df)] = [name, url, category, target, None, None, "", datetime.date.today()]
        df.to_csv(DATA_FILE, index=False)
        st.success(f"✅ Added '{name}'")

# --- Helper: scrape price ---
def get_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        sel = soup.select_one(".a-price-whole, .price, .offer-price, span[data-a-color='price']")
        if sel:
            text = sel.get_text(strip=True).replace("£", "").replace(",", "")
            return float(text)
    except Exception:
        return None
    return None

# --- Check prices manually ---
if st.button("🔁 Check Current Prices"):
    st.info("Checking prices... please wait.")
    for i, row in df.iterrows():
        price = get_price(row["URL"])
        if price:
            prev = df.at[i, "Current Price (£)"]
            df.at[i, "Price Change"] = (
                "↓" if prev and price < prev else ("↑" if prev and price > prev else "—")
            )
            df.at[i, "Current Price (£)"] = price
            df.at[i, "Alert"] = "✅ BUY" if price <= row["Target Price (£)"] else ""
    df.to_csv(DATA_FILE, index=False)
    st.success("Prices updated!")

st.subheader("📋 Your Tracked Items")
st.dataframe(df, use_container_width=True)
