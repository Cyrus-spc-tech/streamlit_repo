import streamlit as st
import smtplib
import random
from email.message import EmailMessage

st.set_page_config(page_title="Home", page_icon="🏠")
st.markdown("<h1 style='text-align:center; color:lightgreen;'>OTP TESTER</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center; color:lightgreen;'>Login Here</h2>", unsafe_allow_html=True)


if 'otp' not in st.session_state:
    st.session_state.otp = ""

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()

server.login("tanishgupta12389@gmail.com", 'rfbb itxr nbwp dwut')

name = st.text_input("Enter Your name :")
phone = st.number_input("Enter Your Phone Number :", placeholder="+91 XXXXXXXXXX", step=1)
email = st.text_input("Enter Your Email :")

if st.button("Send OTP"):

    st.session_state.otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    msg = EmailMessage()
    msg['Subject'] = "OTP verify"
    msg['from'] = "cyrus"
    msg['to'] = email
    msg.set_content("Your OTP is: " + st.session_state.otp)
    server.send_message(msg)
    print('mail sent')
    print(st.session_state.otp)
    server.quit()

    st.success("OTP sent to your email address")

st.text("Enter the OTP sent to your email address")
otp_input = st.text_input("Enter the OTP :")
if st.button("Verify OTP"):
    if otp_input == st.session_state.otp:
        st.success("OTP verified successfully")
    else:
        st.error("Invalid OTP")
st.text("If you have not received the OTP yet, please check your spam folder or try again later.")