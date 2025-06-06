import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Product Profit Calculator", page_icon="👑", layout="centered")
st.title("Product Profit Calculator")
st.caption("All calculations are local · Multi-product supported · Created by Andy Wang ")

# =============== 产品订货成本 ===============
st.header("1. Product Cost")
cost_mode = st.radio(
    "Input mode:",
    ["Total order cost", "Individual product cost"],
    horizontal=True
)

costs = []
if cost_mode == "Total order cost":
    total_cost = st.number_input(
        "Total order cost (NZD)",
        min_value=0.0,
        step=0.01,
        format="%.2f",
        value=None,
        placeholder="E.g. 350.00"
    )
else:
    num_products = st.number_input("Number of products", min_value=1, max_value=20, value=2)
    cols = st.columns(int(num_products))
    for i in range(int(num_products)):
        cost = cols[i].number_input(
            f"Product {i+1} cost",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            value=None,
            placeholder="E.g. 289.75",
            key=f"cost_{i}"
        )
        costs.append(cost if cost is not None else 0.0)
    total_cost = sum(costs) if costs else 0.0

# =============== 产品体积 ===============
st.header("2. Product Volume (m³)")
vol_mode = st.radio(
    "Input mode:",
    ["Total volume", "Individual product volume"],
    horizontal=True
)
volumes = []
if vol_mode == "Total volume":
    total_volume = st.number_input(
        "Total volume (m³)",
        min_value=0.0,
        step=0.0001,
        format="%.3f",
        value=None,
        placeholder="E.g. 0.75"
    )
else:
    num_vols = int(num_products) if cost_mode == "Individual product cost" else st.number_input(
        "Number of volume products", min_value=1, max_value=20, value=2, key="volume_cnt"
    )
    cols = st.columns(num_vols)
    for i in range(num_vols):
        v = cols[i].number_input(
            f"Product {i+1} volume",
            min_value=0.0,
            step=0.0001,
            format="%.3f",
            value=None,
            placeholder="E.g. 0.15",
            key=f"volume_{i}"
        )
        volumes.append(v if v is not None else 0.0)
    total_volume = sum(volumes) if volumes else 0.0

# =============== 运费单价 ===============
st.header("3. Shipping Unit Price")
shipping_unit_price = st.number_input(
    "Shipping unit price (NZD/m³, GST not included, default 150)",
    min_value=0.0,
    step=0.01,
    format="%.2f",
    value=150.0,
    placeholder="E.g. 150"
)

# =============== 售价 ===============
st.header("4. Sale Price")
sale_price = st.number_input(
    "Input sale price (GST included, NZD)",
    min_value=0.0,
    step=0.01,
    format="%.2f",
    value=None,
    placeholder="E.g. 1200"
)

# =============== 计算区 ===============
gst_cost = (total_cost or 0) * 1.15
shipping_cost = (total_volume or 0) * (shipping_unit_price or 0)
shipping_gst = shipping_cost * 1.15
rent = (sale_price or 0) * 0.10
jcd = (sale_price or 0) * 0.09
cogs_and_shipping = gst_cost + shipping_gst
total_expense = cogs_and_shipping + rent + jcd
profit_with_gst = (sale_price or 0) - total_expense
profit_no_gst = profit_with_gst / 1.15 if profit_with_gst != 0 else 0.0

def percent(n):
    return f"{(n/(sale_price or 1)*100):.2f}%" if sale_price and sale_price > 0 else "-"

# =============== 结果展示 ===============
st.header("5. Results")
result_rows = [
    ["COGS", gst_cost, percent(gst_cost)],
    ["Shipping", shipping_gst, percent(shipping_gst)],
    ["Rent (10%)", rent, percent(rent)],
    ["JCD Cost (9%)", jcd, percent(jcd)],
    ["Total Cost", total_expense, percent(total_expense)],
    ["Profit (incl. GST)", profit_with_gst, percent(profit_with_gst)],
    ["Profit (excl. GST)", profit_no_gst, ""],
]
df = pd.DataFrame(result_rows, columns=["Item", "Amount (NZD)", "Ratio to Sale Price"])
df["Amount (NZD)"] = df["Amount (NZD)"].apply(lambda x: f"{x:.2f}")
st.table(df)

with st.expander("Calculation details"):
    st.markdown(f"""
- **Total order cost** = {total_cost or 0:.2f} NZD
- **COGS** = Total order cost × 1.15 = {gst_cost:.2f} NZD
- **Total volume** = {total_volume or 0:.3f} m³
- **Shipping (no GST)** = Total volume × Shipping unit price = {shipping_cost:.2f} NZD
- **Shipping (GST included)** = Shipping × 1.15 = {shipping_gst:.2f} NZD
- **COGS & Shipping** = COGS + Shipping = {cogs_and_shipping:.2f} NZD
- **Rent** = Sale price × 10% = {rent:.2f} NZD
- **JCD Cost** = Sale price × 9% = {jcd:.2f} NZD
- **Total cost** = COGS & Shipping + Rent + JCD Cost = {total_expense:.2f} NZD
- **Profit (incl. GST)** = Sale price - Total cost = {profit_with_gst:.2f} NZD
- **Profit (excl. GST)** = Profit (incl. GST) / 1.15 = {profit_no_gst:.2f} NZD
    """)

# =============== 饼图 ===============
if sale_price and sale_price > 0:
    labels = [
        "COGS",
        "Shipping",
        "Rent",
        "JCD Cost",
        "Profit"
    ]
    values = [
        gst_cost,
        shipping_gst,
        rent,
        jcd,
        max(profit_with_gst, 0)
    ]
    fig, ax = plt.subplots()
    colors = ["#4e79a7", "#f28e2b", "#a0a0a0", "#e15759", "#76b7b2"]
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors
    )
    for text in texts + autotexts:
        text.set_fontproperties("DejaVu Sans")  # 兼容字体
    ax.axis("equal")
    st.pyplot(fig)

st.info("All data is calculated locally and not uploaded. Export to Excel is supported.")

# 导出Excel
if st.button("Export results to Excel"):
    to_excel = pd.DataFrame(result_rows, columns=["Item", "Amount (NZD)", "Ratio to Sale Price"])
    to_excel["Amount (NZD)"] = to_excel["Amount (NZD)"].apply(lambda x: f"{float(x):.2f}")
    to_excel.to_excel("profit_result.xlsx", index=False)
    st.success("Exported profit_result.xlsx, please check your current directory.")
