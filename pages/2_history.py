import streamlit as st
from app import state, logic

def render():

    st.header("📈 История запусков")
    selected_scenario = state.get_selected_scenario()
    if not selected_scenario:
        st.info("Сначала выбери сценарий в разделе '📋 Сценарии'")
        return

    runs = logic.get_runs(selected_scenario.id)
    if not runs:
        st.write("Запусков пока нет.")
    else:
        for run in runs:
            st.write(f"{run.timestamp.strftime('%Y-%m-%d %H:%M:%S')} — {run.status}")

render()