import streamlit as st
import random

def play_with_computer():
    st.subheader("Play with Computer")
    choices = ["Rock", "Paper", "Scissors"]
    user_choice = st.selectbox("Choose your option:", choices)
    if st.button("Play"):
        computer_choice = random.choice(choices)
        st.write(f"Computer chose: {computer_choice}")
        
        if user_choice == computer_choice:
            st.write("It's a tie!")
        elif (user_choice == "Rock" and computer_choice == "Scissors") or \
             (user_choice == "Paper" and computer_choice == "Rock") or \
             (user_choice == "Scissors" and computer_choice == "Paper"):
            st.write("You win!")
        else:
            st.write("You lose!")

def play_with_friend():
    st.subheader("Play with Friend")
    choices = ["Rock", "Paper", "Scissors"]
    user1_choice = st.selectbox("Player 1: Choose your option:", choices, key="player1")
    user2_choice = st.selectbox("Player 2: Choose your option:", choices, key="player2")
    if st.button("Reveal Winner"):
        st.write(f"Player 1 chose: {user1_choice}")
        st.write(f"Player 2 chose: {user2_choice}")
        
        if user1_choice == user2_choice:
            st.write("It's a tie!")
        elif (user1_choice == "Rock" and user2_choice == "Scissors") or \
             (user1_choice == "Paper" and user2_choice == "Rock") or \
             (user1_choice == "Scissors" and user2_choice == "Paper"):
            st.write("Player 1 wins!")
        else:
            st.write("Player 2 wins!")

def play_game():
    st.title("Rock, Paper, Scissors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("vsc.jpg", caption="Play with Computer")
        if st.button("Play with Computer", key="computer"):
            play_with_computer()
    
    with col2:
        st.image("vsf.jpg", caption="Play with Friend")
        if st.button("Play with Friend", key="friend"):
            play_with_friend()

play_game()