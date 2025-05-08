import streamlit as st
from app import ui, state

st.title("🛠 Конструкsdsdтор сценария")
state.init_state()
ui.export_scenario()
ui.import_scenario()
ui.step_form()
ui.step_view()
