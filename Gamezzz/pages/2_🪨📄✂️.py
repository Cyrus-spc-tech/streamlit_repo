import streamlit as st
import random

st.title("🪨📄✂️ Rock Paper Scissors")
choices = ["Rock", "Paper", "Scissors"]

game_mode = st.radio("Choose Game Mode:", ["Play with Computer", "Play with Friend"])

if game_mode == "Play with Computer":
    st.subheader("Play with Computer")
    player_choice = st.selectbox("Your Choice:", choices)
    if st.button("Play"):
        computer_choice = random.choice(choices)
        st.write(f"Computer chose: {computer_choice}")
        if player_choice == computer_choice:
            st.write("It's a tie!")
        elif (player_choice == "Rock" and computer_choice == "Scissors") or \
             (player_choice == "Paper" and computer_choice == "Rock") or \
             (player_choice == "Scissors" and computer_choice == "Paper"):
            st.write("You win!")
        else:
            st.write("You lose!")

elif game_mode == "Play with Friend":
    st.subheader("Play with Friend")
    player1_choice = st.text_input("Player 1  Choise R / P / S",type='password').capitalize()
    player2_choice = st.text_input("Player 2 Choise  R / P / S",type='password').capitalize()
    if st.button("Play"):
        st.write(f"Player 1 chose: {player1_choice}")
        st.write(f"Player 2 chose: {player2_choice}")
        if player1_choice == player2_choice:
            st.write("It's a tie!")
        elif (player1_choice == "R" and player2_choice == "S") or \
             (player1_choice == "P" and player2_choice == "R") or \
             (player1_choice == "S" and player2_choice == "P"):
            st.write("Player 1 wins!")
        else:
            st.write("Player 2 wins!")
        if st.button('play Again'):
            st.write('play')

        