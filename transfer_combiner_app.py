import streamlit as st
import pandas as pd

st.set_page_config(page_title="Transfer Combiner", layout="centered")

st.title("📦 Transfer Combiner App")

# File Uploads
available_file = st.file_uploader("Upload 'available dc.csv'", type="csv")
active_file = st.file_uploader("Upload 'active dc.csv'", type="csv")
inactive_file = st.file_uploader("Upload 'inactive.csv'", type="csv")

if available_file and active_file and inactive_file:
    with st.spinner("Processing..."):

        # Read CSVs
        df = pd.read_csv(available_file)
        df2 = pd.read_csv(active_file)
        df3 = pd.read_csv(inactive_file, low_memory=False)

        # Filtering
        df_filtered = df2[df2['sku_id'].isin(df['sku_id'])]
        df_filtered2 = df3[df3['sku_id'].isin(df['sku_id'])]

        # Combine
        df_combined = pd.concat([df_filtered, df_filtered2, df], ignore_index=True)

        st.success("✅ Files processed and combined successfully!")

        # Show preview
        st.subheader("Preview of Combined Data")
        st.dataframe(df_combined.head())

        # Download button
        csv = df_combined.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Combined CSV",
            data=csv,
            file_name="combined.csv",
            mime="text/csv"
        )
else:
    st.warning("Please upload all three required files.")
