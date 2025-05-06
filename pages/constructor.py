import streamlit as st
from app import ui, state

st.title("🛠 Конструктор сценария")
ui.export_scenario()
state.init_state()
ui.step_form()
ui.step_view()