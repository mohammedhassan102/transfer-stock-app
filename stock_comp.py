import streamlit as st
import pandas as pd
import io

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="📦 Transfer + Stock Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
    html, body {
        font-family: "Segoe UI", sans-serif;
    }
    .stButton > button {
        background-color: #FF6F00;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        height: 3em;
    }
    .stButton > button:hover {
        background-color: #e65c00;
    }
    .block-container {
        padding: 2rem 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("📦 Transfer + Stock Adjustment Tool")
st.markdown("Upload your files. This tool combines and adjusts `stock_on_hand`, and provides a cleaned, downloadable result.")

# ---------------- FILE UPLOAD ----------------
col1, col2, col3 = st.columns(3)

with col1:
    available_file = st.file_uploader("Available SKUs", type="csv", key="available")
with col2:
    active_file = st.file_uploader("Active SKUs", type="csv", key="active")
with col3:
    inactive_file = st.file_uploader("Inactive SKUs", type="csv", key="inactive")

# ---------------- PROCESS ----------------
if available_file and active_file and inactive_file:
    st.markdown("### ⚙️ Processing...")
    progress = st.progress(0)

    # Read files
    df = pd.read_csv(available_file)
    df2 = pd.read_csv(active_file)
    df3 = pd.read_csv(inactive_file, low_memory=False)

    progress.progress(25)

    # Combine based on sku_id
    df_filtered = df2[df2['sku_id'].isin(df['sku_id'])]
    df_filtered2 = df3[df3['sku_id'].isin(df['sku_id'])]
    df_combined = pd.concat([df_filtered, df_filtered2, df], ignore_index=True)

    progress.progress(60)

    # Adjust stock_on_hand = MAX(stock_on_hand - blocked_qty, 0)
    if "stock_on_hand" in df_combined.columns and "blocked_qty" in df_combined.columns:
        df_combined["stock_on_hand"] = (df_combined["stock_on_hand"] - df_combined["blocked_qty"]).clip(lower=0)

    # Drop unwanted columns if present
    cols_to_remove = ["putaway_reserved_qty", "can_expire", "parent_category"]
    df_combined = df_combined.drop(columns=[col for col in cols_to_remove if col in df_combined.columns])

    progress.progress(100)
    st.success("✅ Combined and adjusted successfully!")

    # Show final cleaned data
    st.markdown("### 🧾 Final Combined Data")
    st.dataframe(df_combined.head(50), use_container_width=True)

    # Summary
    st.markdown("### 📊 Summary")
    colA, colB = st.columns(2)
    with colA:
        st.metric("Total Rows", f"{len(df_combined):,}")
    with colB:
        if "sku_id" in df_combined.columns:
            st.metric("Unique SKUs", f"{df_combined['sku_id'].nunique():,}")

    st.markdown("### 📦 Breakdown by Source")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"Available SKUs: **{len(df):,}**")
    with col2:
        st.info(f"Active SKUs (filtered): **{len(df_filtered):,}**")
    with col3:
        st.warning(f"Inactive SKUs (filtered): **{len(df_filtered2):,}**")

    # ---------------- DOWNLOAD ----------------
    st.markdown("### 📥 Download Final Data")
    csv_buffer = io.StringIO()
    df_combined.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download Cleaned CSV",
        data=csv_buffer.getvalue(),
        file_name="combined_cleaned.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Please upload all 3 files to begin.")
