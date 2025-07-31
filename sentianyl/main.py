import transformers 
from transformers import pipeline 
import streamlit as st 

st.title("Sentiment Analysis")
text=st.text_input("Enter the text")
t=pipeline("sentiment-analysis")

if st.button("Analyze"):    
    result=t(text)
    st.write(result)    

    
