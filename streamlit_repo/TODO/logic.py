import streamlit as st

state = st.session_state


def init_todos():
    if "todos" not in state:
        state.todos = [
            
        ]


def add_todo(text):
    if text.strip():
        state.todos.append({"text": text, "done": False})
        state.new_task = ""


def toggle_todo(index):
    state.todos[index]["done"] = not state.todos[index]["done"]


def delete_todo(index):
    state.todos.pop(index)


def delete_completed():
    state.todos = [t for t in state.todos if not t["done"]]
