import streamlit as st
import json
from app import ui, state, logic

# st.title("🛠 Конструктор сценария")
state.init_state()
ui.export_scenario()
ui.import_scenario()

ui.add_step_form()
ui.view_steps()
ui.save_scenario_form()