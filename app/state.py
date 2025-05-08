import streamlit as st

def init_state():
    st.session_state.steps = []
    if "steps" not in st.session_state:
        st.session_state.steps = []
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = None

def add_step(step: dict):
    st.session_state.steps.append(step)

def clear_steps():
    st.session_state.steps = []

def get_steps():
    return st.session_state.steps

def set_selected_scenario(scenario):
    st.session_state.selected_scenario = scenario
    if scenario:
        import json
        steps = json.loads(scenario.steps_json)
        st.session_state.steps = steps

def get_selected_scenario():
    return st.session_state.selected_scenario