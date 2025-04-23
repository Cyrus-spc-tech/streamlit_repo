import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(page_title="Data Vizulizer", page_icon=":bar_chart:", layout="centered", initial_sidebar_state="auto", menu_items=None)


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
    st.write(df.head())# it will show the first five enteries 

    st.subheader("Data Summary")
    st.write(df.describe())# it will describe the  row and columns of the data

    st.subheader("Filter Data")
    filter = st.selectbox("Select a column to filter by", df.columns.tolist())# use to select the columns 
    
    unique_val=df[filter].unique()
    selected_val=st.selectbox("select value",unique_val)

    filtered_data=df[df[filter]==selected_val]
    st.write(filtered_data)

    st.subheader("  plotting data ")
    xaxis=st.selectbox(" Select x- axis ",df.columns)
    yaxis=st.selectbox(" Select y- axis ",df.columns)

    if "plot_option" not in st.session_state:
        st.session_state.plot_option = None
        st.write("Please click the button to generate the plot")
    if st.button("Generate Plot"):
        st.session_state.plot_option = st.sidebar.radio("Select a Graph you want to plot ", ("Line Graph", "Bar Graph", "Pie Chart"))

    if st.session_state.plot_option:
        if st.session_state.plot_option == "Line Graph":
            st.subheader("Line Graph")
            st.line_chart(filtered_data.set_index(xaxis)[yaxis])
            st.session_state.plot_option = None

        elif st.session_state.plot_option == "Bar Graph":
            st.subheader("Bar Graph")
            st.bar_chart(filtered_data.set_index(xaxis)[yaxis])
            st.session_state.plot_option = None
        elif st.session_state.plot_option == "Pie Chart":

            st.subheader("Pie Chart")
            plt.figure(figsize=(10, 6))
            plt.pie(filtered_data[yaxis], labels=filtered_data[xaxis], autopct='%1.1f%%')
            

            plt.title(f"Pie Chart of {yaxis} by {xaxis}")
            st.session_state.plot_option = None
            st.pyplot(plt)

        