import streamlit as st 

st.title("Session State Example")
st.write("This example demonstrates how to use session state in Streamlit.")
# Initialize session state if not already set
if 'counter' not in st.session_state:
    st.session_state.counter = 0
# Function to increment the counter
def increment_counter():
    st.session_state.counter += 1

def decrement_counter():
    st.session_state.counter -= 1

# Button to increment the counter
if st.button('Increment Counter'):
    increment_counter()
elif st.button('Decrement Counter'):
    decrement_counter()


# Display the current counter value
st.write(f"Counter value: {st.session_state.counter}")


# Button to reset the counter
if st.button('Reset Counter'):
    st.session_state.counter = 0
    st.write("Counter has been reset.")



# Display the current session state
st.write("Current session state:", st.session_state)


# Display a message based on the counter value
if st.session_state.counter > 5:
    st.write("Counter is greater than 5!")
else:
    st.write("Counter is 5 or less.")


# Display a message when the counter reaches 10
if st.session_state.counter == 10:
    st.info("Counter has reached 10!")


# Display a message when the counter is reset
if st.session_state.counter == 0:
    st.success("Counter has been reset to 0.")


# Display a message when the counter is incremented
if st.session_state.counter > 0:
    st.success("Counter has been incremented.")
    

