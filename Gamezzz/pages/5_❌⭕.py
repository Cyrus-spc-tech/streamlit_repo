import streamlit as st 

# Initialize the game state
if "board" not in st.session_state:
    st.session_state.board = [""] * 9
    st.session_state.current_player = "X"
    st.session_state.winner = None

def check_winner(board):
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  
        (0, 4, 8), (2, 4, 6)              
    ]
    for a, b, c in winning_combinations:
        if board[a] == board[b] == board[c] and board[a] != "":
            return board[a]
    if "" not in board:
        return "Draw"
    return None


# Game logic
def make_move(index):
    if st.session_state.board[index] == "" and st.session_state.winner is None:
        st.session_state.board[index] = st.session_state.current_player
        st.session_state.winner = check_winner(st.session_state.board)
        if st.session_state.winner is None:
            st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"
st.title("Tic Tac Toe")
st.markdown(
    """
    <style>
    .tic-tac-toe-button {
        width: 100px;
        height: 100px;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        background-color: #f0f0f0;
        border: 2px solid #ccc;
        border-radius: 10px;
        cursor: pointer;
    }
    .tic-tac-toe-button:hover {
        background-color: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

cols = st.columns(3)
for i in range(3):
    for j in range(3):
        index = 3 * i + j
        with cols[j]:
            if st.button(
                st.session_state.board[index] or " ",
                key=index,
                help="Click to make a move",
                use_container_width=True,
            ):
                make_move(index)

# Display the game result
if st.session_state.winner:
    if st.session_state.winner == "Draw":
        st.success("It's a draw!")
    else:
        st.success(f"Player {st.session_state.winner} wins!")

# Reset button
if st.button("Restart Game"):
    st.session_state.board = [""] * 9
    st.session_state.current_player = "X"
    st.session_state.winner = None