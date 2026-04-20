# @ buit with CHATGPT  
import streamlit as st
import requests

# Title and Description
st.title("Currency Converter")
st.write("Convert currencies in real-time using this simple app.")

# Sidebar for user input
st.sidebar.header("Converter Settings")
base_currency = st.sidebar.selectbox("Select base currency", ["USD", "EUR", "GBP", "INR", "AUD"])
target_currency = st.sidebar.selectbox("Select target currency", ["USD", "EUR", "GBP", "INR", "AUD"])
amount = st.sidebar.number_input("Amount to convert", min_value=0.0, value=1.0, step=0.01)

# Function to fetch exchange rate
def get_exchange_rate(base, target):
    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rates = data.get("rates", {})
        return rates.get(target, None)
    else:
        st.error("Error fetching exchange rates. Please try again later.")
        return None

# Perform conversion
st.header("Conversion Result")
if base_currency == target_currency:
    st.write("Base and target currencies are the same. Conversion is not needed.")
else:
    rate = get_exchange_rate(base_currency, target_currency)
    if rate:
        converted_amount = amount * rate
        st.write(f"{amount} {base_currency} = {converted_amount:.2f} {target_currency}")
    else:
        st.write("Unable to fetch conversion rate.")

# Footer
st.write("Data provided by ExchangeRate-API.")
