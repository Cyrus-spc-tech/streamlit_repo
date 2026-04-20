import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


st.set_page_config(
    page_title="Data Visualizer",
    page_icon=":bar_chart:",
    layout="centered",
)


st.title("📊 _Data Visualizer_")

st.sidebar.title("Upload and Settings")

uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
tab1,tab2=st.tabs(["Data Visualizer","Data Analytics"])
if uploaded_file is not None:
    @st.cache_data
    def load_data(file):
        return pd.read_csv(file)
        
    try:
        with tab1:
            df = load_data(uploaded_file)
            st.success("✅ File uploaded and loaded successfully!")
            
            st.subheader("🔍 Data Preview")
            st.dataframe(df.head())
            
            st.subheader("📈 Data Summary")
            st.dataframe(df.describe())
            
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

            plot = st.selectbox("Select plot type", ["Line Plot", "Bar Plot", "Scatter Plot"])

            if xaxis == yaxis:
                st.warning("❗X-axis and Y-axis cannot be the same.")
            elif st.button("Generate Plot"):
                if plot == "Line Plot":
                    st.line_chart(filtered_data.set_index(xaxis)[yaxis])
                elif plot == "Bar Plot":
                    st.bar_chart(filtered_data.set_index(xaxis)[yaxis])
                elif plot == "Scatter Plot":
                    st.scatter_chart(filtered_data.set_index(xaxis)[yaxis])
                else:
                    st.error("❌ Invalid plot type selected.")

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

    with tab2:
        
        st.subheader("Data Analytics")
        if 'df' in locals():
            st.dataframe(df)
            
            st.subheader("Analytics Options")
            analytics_type = st.selectbox("Select Analytics Type", ['Summary Statistics', 'Visual Analytics'])
            
            if analytics_type == "Summary Statistics":
                st.subheader("Summary Statistics")
                st.write(df.describe())
                
                
            elif analytics_type == "Visual Analytics":
                st.subheader("Visual Analytics")
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                if len(numeric_cols) > 0:
                    st.subheader("Distribution Plots")
                    for col in numeric_cols:
                        fig = px.histogram(df, x=col, title=f'Distribution of {col}')
                        st.plotly_chart(fig, use_container_width=True)
                # Line Plot
                st.subheader("Line Plot")
                line_x = st.selectbox("Select x-axis", df.columns, key='line_x')
                line_y = st.selectbox("Select y-axis", df.columns, key='line_y')
                if line_x == line_y:
                    st.warning("❗X-axis and Y-axis cannot be the same.")
                elif st.button("Generate Line Plot"):
                    st.line_chart(df.set_index(line_x)[line_y])
                
                # Bar Plot
                st.subheader("Bar Plot")
                bar_x = st.selectbox("Select x-axis", df.columns, key='bar_x')
                bar_y = st.selectbox("Select y-axis", df.columns, key='bar_y')
                if bar_x == bar_y:
                    st.warning("❗X-axis and Y-axis cannot be the same.")
                elif st.button("Generate Bar Plot"):
                    st.bar_chart(df.set_index(bar_x)[bar_y])
                
                # Box Plots
                st.subheader("Box Plots")
                box_x = st.selectbox("Select x-axis for Box Plot", df.columns, key='box_x')
                if box_x in numeric_cols:
                    fig = px.box(df, y=box_x, title=f'Box Plot of {box_x}')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"❗ '{box_x}' is not a numeric column.")
                
                # Scatter Plots
                st.subheader("Scatter Plots")
                scatter_x = st.selectbox("Select x-axis for Scatter Plot", df.columns, key='scatter_x')
                scatter_y = st.selectbox("Select y-axis for Scatter Plot", df.columns, key='scatter_y')
                if scatter_x in numeric_cols and scatter_y in numeric_cols:
                    fig = px.scatter(
                        df, 
                        x=scatter_x, 
                        y=scatter_y,
                        title=f'{scatter_x} vs {scatter_y}',
                        width=800,
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"❗ '{scatter_x}' and '{scatter_y}' must both be numeric columns.")
                
                # Pie Charts
                st.subheader("Pie Charts")
                pie_col = st.selectbox("Select column for Pie Chart", df.columns, key='pie_col')
                if pie_col in df.select_dtypes(include=['object']).columns:
                    try:
                        # Only show pie charts for columns with reasonable number of unique values
                        if 1 < df[pie_col].nunique() <= 10:
                            fig = px.pie(
                                df, 
                                names=pie_col, 
                                title=f'Distribution of {pie_col}',
                                hole=0.3
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create pie chart for {pie_col}: {str(e)}")

else :
    st.warning("Please upload a CSV file.")