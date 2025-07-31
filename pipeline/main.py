import transformers 
from transformers import pipeline 
import streamlit as st 

st.title("Sentiment Analysis")

choice=st.selectbox("Select the task",["Sentiment Analysis", "Named Entity Recognition"])
text=st.text_input("Enter the text")

if st.button("Analyze"):
    if choice == "Sentiment Analysis":
        sa=pipeline("sentiment-analysis")
        result=sa(text)
        st.write(result)
    elif choice == "Named Entity Recognition":
        ner = pipeline("ner")
        result=ner(text)
        st.write(result)
