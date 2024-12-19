import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("_ Data Vizulizer _")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

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

    if st.button("Generate Plot"): 
        plt.figure(figsize=(10,6))
        plt.plot(xaxis,yaxis)
        plt.title(f"Scatter plot of {xaxis} vs {yaxis}")
        st.pyplot(plt)
    else :
        st.write("Please click the button to generate the plot")