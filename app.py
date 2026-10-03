import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(
    page_title="Smart Laptop Recommender System",
    page_icon="💻",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        text-align: center;
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F0F4F8;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💻 Smart Laptop Finder & Recommendation System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Find the best gaming, professional, thin & light, or creator laptop in your budget</div>', unsafe_allow_html=True)

# Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv("laptops.csv")

try:
    df = load_data()
except Exception as e:
    st.error("Error loading laptops.csv! Make sure the file exists in the same directory.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Options")

# Search Keyword
search_term = st.sidebar.text_input("Search by Laptop Name/Brand", "")

# Category Filter
categories = ["All"] + list(df["category"].unique())
selected_category = st.sidebar.selectbox("Select Category", categories)

# Brand Filter
brands = ["All"] + list(df["brand"].unique())
selected_brand = st.sidebar.selectbox("Select Brand", brands)

# Budget Filter
min_price = int(df["price"].min())
max_price = int(df["price"].max())

selected_budget = st.sidebar.slider(
    "Maximum Budget (₹)",
    min_value=30000,
    max_value=700000,
    value=150000,
    step=10000,
    format="₹%d"
)

# Sort By Filter
sort_by = st.sidebar.radio("Sort Results By", ["Price: Low to High", "Price: High to Low", "Rating: High to Low"])

# --- FILTERING LOGIC ---
filtered_df = df[df["price"] <= selected_budget]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if selected_brand != "All":
    filtered_df = filtered_df[filtered_df["brand"] == selected_brand]

if search_term:
    filtered_df = filtered_df[
        filtered_df["name"].str.contains(search_term, case=False, na=False) |
        filtered_df["brand"].str.contains(search_term, case=False, na=False)
    ]

# Sorting
if sort_by == "Price: Low to High":
    filtered_df = filtered_df.sort_values(by="price", ascending=True)
elif sort_by == "Price: High to Low":
    filtered_df = filtered_df.sort_values(by="price", ascending=False)
elif sort_by == "Rating: High to Low":
    filtered_df = filtered_df.sort_values(by="rating", ascending=False)

# --- QUICK STATS METRICS ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Laptops Available", len(df))
col_m2.metric("Laptops in Budget", len(filtered_df))
col_m3.metric("Selected Max Budget", f"₹{selected_budget:,}")
col_m4.metric("Categories", len(df["category"].unique()))

st.markdown("---")

# --- COMPARISON TOOL SETUP ---
st.subheader("⚖️ Compare Laptops Side-by-Side")
compare_list = st.multiselect(
    "Select up to 3 laptops to compare specs:",
    options=df["name"].tolist(),
    max_selections=3
)

if compare_list:
    comp_df = df[df["name"].isin(compare_list)]
    st.write("### Comparison Table")
    st.dataframe(
        comp_df[["name", "brand", "category", "price", "cpu", "gpu", "ram", "storage", "rating"]].set_index("name"),
        use_container_width=True
    )
    st.markdown("---")

# --- MAIN GRID DISPLAY ---
st.subheader(f"Showing {len(filtered_df)} Laptops Under ₹{selected_budget:,}")

if filtered_df.empty:
    st.warning("No laptops found matching your criteria! Try increasing your budget or changing filters.")
else:
    # Display Laptops in 3 columns grid
    cols_per_row = 3
    for i in range(0, len(filtered_df), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(filtered_df):
                row = filtered_df.iloc[idx]
                with cols[j]:
                    st.image(row["image_url"], use_container_width=True)
                    st.markdown(f"### {row['name']}")
                    st.markdown(f"**🏷️ Category:** {row['category']}")
                    st.markdown(f"**💰 Price:** ₹{int(row['price']):,}")
                    st.markdown(f"**⚙️ CPU:** {row['cpu']}")
                    st.markdown(f"**🎮 GPU:** {row['gpu']}")
                    st.markdown(f"**🧠 RAM & Storage:** {row['ram']} | {row['storage']}")
                    st.markdown(f"**⭐ Rating:** {row['rating']}/5")
                    st.info(f"**Target Use:** {row['use_case']}")

                    # Modal or expandable view for full details
                    with st.expander("View Full Specifications"):
                        st.write(f"- **Brand:** {row['brand']}")
                        st.write(f"- **Processor:** {row['cpu']}")
                        st.write(f"- **Graphics Card:** {row['gpu']}")
                        st.write(f"- **Memory:** {row['ram']}")
                        st.write(f"- **Storage:** {row['storage']}")
                        st.write(f"- **Primary Category:** {row['category']}")
                        st.write(f"- **User Rating:** {row['rating']} Out of 5.0")
                    
                    st.markdown("---")