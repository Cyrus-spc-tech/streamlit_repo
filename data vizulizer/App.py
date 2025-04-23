import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Data Vizulizer", page_icon=":bar_chart:", layout="centered", initial_sidebar_state="auto")

st.title("_ Data Vizulizer _")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

st.sidebar.title("Data Vizulizer")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        st.stop()
    st.success("File uploaded successfully!")

    st.subheader("Data Preview")
    st.write(df.head())  # Show the first five entries

    st.subheader("Data Summary")
    st.write(df.describe())  # Describe the rows and columns of the data

    st.subheader("Filter Data")
    filter_column = st.selectbox("Select a column to filter by", df.columns.tolist())  # Select a column

    unique_values = df[filter_column].unique()
    selected_value = st.selectbox("Select value", unique_values)

    filtered_data = df[df[filter_column] == selected_value]
    st.write(filtered_data)

    st.subheader("Plotting Data")
    xaxis = st.selectbox("Select x-axis", df.columns)
    yaxis = st.selectbox("Select y-axis", df.columns)

    plot_option = st.radio("Select a Graph to plot", ("Line Graph", "Bar Graph", "Pie Chart"))

    if st.button("Generate Plot"):
        if plot_option == "Line Graph":
            st.subheader("Line Graph")
            st.line_chart(filtered_data.set_index(xaxis)[yaxis])

        elif plot_option == "Bar Graph":
            st.subheader("Bar Graph")
            st.bar_chart(filtered_data.set_index(xaxis)[yaxis])

        elif plot_option == "Pie Chart":
            st.subheader("Pie Chart")
            plt.figure(figsize=(10, 6))
            plt.pie(filtered_data[yaxis], labels=filtered_data[xaxis], autopct='%1.1f%%')
            plt.title(f"Pie Chart of {yaxis} by {xaxis}")
            st.pyplot(plt)