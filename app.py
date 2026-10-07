import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Smart Laptop Recommender System", page_icon="💻", layout="wide"
)

# Custom Styling & Header
st.markdown(
    """
    <style>
        .main-title { text-align: center; font-size: 2.5rem; font-weight: 700; color: #1E88E5; }
        .sub-title { text-align: center; font-size: 1.1rem; color: #555555; margin-bottom: 2rem; }
    </style>
    <div class="main-title">💻 Smart Laptop Finder & Recommendation System</div>
    <div class="sub-title">Find the best laptop in your budget</div>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    return pd.read_csv("laptops.csv")


try:
    df = load_data()
except Exception:
    st.error(
        "Error loading laptops.csv! Ensure the file exists in the directory."
    )
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Options")
search_term = st.sidebar.text_input("Search Name/Brand", "")
selected_cat = st.sidebar.selectbox(
    "Select Category", ["All"] + list(df["category"].unique())
)
selected_brand = st.sidebar.selectbox(
    "Select Brand", ["All"] + list(df["brand"].unique())
)
budget = st.sidebar.slider(
    "Maximum Budget (₹)",
    30000,
    700000,
    150000,
    step=10000,
    format="₹%d",
)
sort_by = st.sidebar.radio(
    "Sort Results By",
    ["Price: Low to High", "Price: High to Low", "Rating: High to Low"],
)

# --- FILTER & SORT LOGIC ---
filtered = df[df["price"] <= budget]
if selected_cat != "All":
    filtered = filtered[filtered["category"] == selected_cat]
if selected_brand != "All":
    filtered = filtered[filtered["brand"] == selected_brand]
if search_term:
    mask = filtered["name"].str.contains(
        search_term, case=False, na=False
    ) | filtered["brand"].str.contains(search_term, case=False, na=False)
    filtered = filtered[mask]

sort_map = {
    "Price: Low to High": ("price", True),
    "Price: High to Low": ("price", False),
    "Rating: High to Low": ("rating", False),
}
col, asc = sort_map[sort_by]
filtered = filtered.sort_values(by=col, ascending=asc)

# --- METRICS & COMPARISON ---
cols = st.columns(4)
cols[0].metric("Total Available", len(df))
cols[1].metric("Laptops in Budget", len(filtered))
cols[2].metric("Max Budget", f"₹{budget:,}")
cols[3].metric("Categories", len(df["category"].unique()))

st.markdown("---")
st.subheader("⚖️ Compare Laptops Side-by-Side")
compare_list = st.multiselect(
    "Select up to 3 laptops:", options=df["name"].tolist(), max_selections=3
)

if compare_list:
    comp_cols = [
        "name",
        "brand",
        "category",
        "price",
        "cpu",
        "gpu",
        "ram",
        "storage",
        "rating",
    ]
    st.dataframe(
        df[df["name"].isin(compare_list)][comp_cols].set_index("name"),
        use_container_width=True,
    )
    st.markdown("---")

# --- MAIN GRID DISPLAY ---
st.subheader(f"Showing {len(filtered)} Laptops Under ₹{budget:,}")

if filtered.empty:
    st.warning("No laptops found matching your criteria!")
else:
    grid_cols = st.columns(3)
    for idx, row in enumerate(filtered.itertuples()):
        with grid_cols[idx % 3]:
            st.markdown(
                f"### {row.name}\n"
                f"**🏷️ Category:** {row.category}  \n"
                f"**💰 Price:** ₹{int(row.price):,}  \n"
                f"**⚙️ CPU:** {row.cpu}  \n"
                f"**🎮 GPU:** {row.gpu}  \n"
                f"**🧠 RAM & Storage:** {row.ram} | {row.storage}  \n"
                f"**⭐ Rating:** {row.rating}/5"
            )
            st.info(f"**Target Use:** {row.use_case}")

            with st.expander("View Full Specifications"):
                st.write(
                    f"- **Brand:** {row.brand}\n"
                    f"- **Processor:** {row.cpu}\n"
                    f"- **Graphics:** {row.gpu}\n"
                    f"- **Memory:** {row.ram}\n"
                    f"- **Storage:** {row.storage}\n"
                    f"- **Category:** {row.category}\n"
                    f"- **User Rating:** {row.rating} / 5.0"
                )
            st.markdown("---")