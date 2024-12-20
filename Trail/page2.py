# @ Built with CHAT GPT 
import streamlit as st
import random

# Set the title
st.title('Number Guessing Game')

# Display instructions
st.write("I'm thinking of a number between 1 and 100. Can you guess what it is?")

# Initialize session state variables
if 'number' not in st.session_state:
    st.session_state.number = random.randint(1, 100)
    st.session_state.guesses = 0
    st.session_state.game_over = False

# If the game is over, display the result
if st.session_state.game_over:
    st.write(f"Game Over! The number was {st.session_state.number}.")
    if st.session_state.guesses == 1:
        st.write("You guessed it in 1 try!")
    else:
        st.write(f"You guessed it in {st.session_state.guesses} tries.")
    
    # Reset button
    if st.button("Play Again"):
        st.session_state.number = random.randint(1, 100)
        st.session_state.guesses = 0
        st.session_state.game_over = False

else:
    # Take user input
    guess = st.number_input("Enter your guess:", min_value=1, max_value=100, step=1)

    # Check guess
    if guess:
        st.session_state.guesses += 1
        if guess < st.session_state.number:
            st.write("Too low! Try again.")
        elif guess > st.session_state.number:
            st.write("Too high! Try again.")
        else:
            st.session_state.game_over = True
            st.write("Correct! You guessed the number!")
