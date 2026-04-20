import streamlit as st
import random

if "level" not in st.session_state:
    st.session_state.level = None
if "target_number" not in st.session_state:
    st.session_state.target_number = None
if "attempts_left" not in st.session_state:
    st.session_state.attempts_left = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False


def start_game(level):
    st.session_state.level = level
    st.session_state.target_number = random.randint(1, 100)
    st.session_state.game_over = False
    if level == "Easy":
        st.session_state.attempts_left = 10
    elif level == "Medium":
        st.session_state.attempts_left = 5
    elif level == "Hard":
        st.session_state.attempts_left = 3


st.title("🔢 Guess the Number Game")

if st.session_state.level is None:
    st.subheader("Select Difficulty Level")
    if st.button("Easy"):
        start_game("Easy")
    if st.button("Medium"):
        start_game("Medium")
    if st.button("Hard"):
        start_game("Hard")
else:
    st.subheader(f"Level: {st.session_state.level}")
    st.write(f"Attempts Left: {st.session_state.attempts_left}")

    if not st.session_state.game_over:
        guess = st.number_input("Enter your guess (1-100):", min_value=1, max_value=100, step=1)
        if st.button("Submit Guess"):
            if guess == st.session_state.target_number:
                st.success(f"🎉 Congratulations! You guessed the number {st.session_state.target_number} correctly!")
                st.session_state.game_over = True
            else:
                st.session_state.attempts_left -= 1
                if st.session_state.attempts_left == 0:
                    st.error(f"Game Over! The correct number was {st.session_state.target_number}.")
                    st.session_state.game_over = True
                elif guess < st.session_state.target_number:
                    st.warning("Too low! Try again.")
                else:
                    st.warning("Too high! Try again.")

    if st.session_state.game_over:
        if st.button("Play Again"):
            st.session_state.level = None
            st.session_state.target_number = None
            st.session_state.attempts_left = None
            st.session_state.game_over = False