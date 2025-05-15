import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(
    page_title="Data Visualizer",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Title
st.title("📊 _Data Visualizer_")

# Sidebar
st.sidebar.title("Upload and Settings")

# File uploader
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        @st.cache_data
        def load_data(file):
            return pd.read_csv(file)

        df = load_data(uploaded_file)
        st.success("✅ File uploaded and loaded successfully!")

        # Data Preview
        st.subheader("🔍 Data Preview")
        st.dataframe(df.head())

        # Data Summary
        st.subheader("📈 Data Summary")
        st.dataframe(df.describe())

        # Filter Data
        st.subheader("🔎 Filter Data")
        filter_column = st.selectbox("Select a column to filter by", df.columns)

        if pd.api.types.is_numeric_dtype(df[filter_column]):
            min_val, max_val = int(df[filter_column].min()), int(df[filter_column].max())
            selected_range = st.slider("Select a range", min_val, max_val, (min_val, max_val))
            filtered_data = df[df[filter_column].between(*selected_range)]
        else:
            unique_vals = df[filter_column].dropna().unique()
            selected_val = st.selectbox("Select a value", unique_vals)
            filtered_data = df[df[filter_column] == selected_val]

        st.dataframe(filtered_data)

        # Plotting
        st.subheader("📊 Plotting Data")
        xaxis = st.selectbox("Select x-axis", df.columns)
        yaxis = st.selectbox("Select y-axis", df.columns)

        if xaxis == yaxis:
            st.warning("❗X-axis and Y-axis cannot be the same.")
        elif st.button("Generate Plot"):
            try:
                st.line_chart(filtered_data.set_index(xaxis)[yaxis])
            except Exception as e:
                st.error(f"Error generating plot: {e}")
        else:
            st.info("Click the button to generate the plot.")

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
else:
    st.info("📁 Please upload a CSV file to get started.")
