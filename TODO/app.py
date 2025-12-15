import streamlit as st
from logic import (
    init_todos,
    add_todo,
    toggle_todo,
    delete_todo,
    delete_completed,
)

st.set_page_config(page_title="TODO",page_icon="📋",layout="centered")

state = st.session_state
init_todos()

st.sidebar.title("TODO")

# Add new task
with st.form("add_form"):
    col1, col2 = st.columns([7, 1])
    with col1:
        st.text_input("",
            placeholder="Enter task",
            key="new_task"
        )
    with col2:
        st.form_submit_button(
            "➕",
            on_click=add_todo,
            args=(state.new_task,)
        )

# Display tasks
if state.todos:
    for i, todo in enumerate(state.todos):
        col1, col2 = st.columns([6, 1])

        with col1:
            st.checkbox(
                todo["text"],
                value=todo["done"],
                key=f"chk_{i}",
                on_change=toggle_todo,
                args=(i,)
            )

        with col2:
            st.button(
                "🗑️",
                key=f"del_{i}",
                on_click=delete_todo,
                args=(i,)
            )

    st.button("Delete all tasks", on_click=delete_completed)

else:
    st.sidebar.info("No tasks available.")
