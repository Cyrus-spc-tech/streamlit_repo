import streamlit as st
import random
import time

# Initialize session state variables
if "score" not in st.session_state:
    st.session_state.score = 0
if "highscore" not in st.session_state:
    st.session_state.highscore = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "question" not in st.session_state:
    st.session_state.question = None
if "answer" not in st.session_state:
    st.session_state.answer = None

# Function to generate a random math question
def generate_question():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operation = random.choice(["+", "-", "*"])
    question = f"{num1} {operation} {num2}"
    answer = eval(question)
    return question, answer

# Start the game
st.title("Math Random Question Game 🧮")
st.write("Solve as many math questions as you can before the timer runs out!")

if st.button("Start Game"):
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    st.session_state.question, st.session_state.answer = generate_question()

# Timer
if st.session_state.start_time:
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(30 - elapsed_time, 0)
    st.write(f"Time Remaining: {remaining_time:.1f} seconds")

    if remaining_time <= 0:
        st.write("Time's up!")
        st.session_state.highscore = max(st.session_state.highscore, st.session_state.score)
        st.write(f"Your Score: {st.session_state.score}")
        st.write(f"High Score: {st.session_state.highscore}")
        st.session_state.start_time = None

# Display question and input box
if st.session_state.start_time and st.session_state.question:
    st.write(f"Question: {st.session_state.question}")
    user_answer = st.text_input("Your Answer:", key="user_answer")

    if user_answer:
        if int(user_answer) == st.session_state.answer:
            st.session_state.score += 1
            st.session_state.question, st.session_state.answer = generate_question()
            st.success("Correct!")
        else:
            st.error("Wrong answer! Try again.")
        st.session_state.user_answer = ""  # Clear input box

# Display score and high score
st.write(f"Score: {st.session_state.score}")
st.write(f"High Score: {st.session_state.highscore}")