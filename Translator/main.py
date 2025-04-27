from google_trans_new import google_translator
import streamlit as st

input = st.text_area("Enter text to translate:")
language = st.selectbox("Select target language:", ["en", "es", "fr", "de", "it", "pt"])
translator = google_translator()
if st.button("Translate"):
    if input:
        try:
            translation = translator.translate(input, lang_tgt=language)
            st.success(f"Translation: {translation}")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter text to translate.")