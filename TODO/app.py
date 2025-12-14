import streamlit as st
from dataclasses import dataclass, field
import uuid

st.set_page_config(page_title="To-do list", page_icon="📋")

state = st.session_state


