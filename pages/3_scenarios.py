import streamlit as st
from app import ui, logic, runner, state
import streamlit as st
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from pathlib import Path

st.title("📋 Сценарии")
state.init_state()
ui.search_and_display_scenarios()
steps = state.get_steps()

if steps and st.button("🚀 Выполнить сценарий"):
    try:
        runner.run_steps_safe(steps)
        st.success("Сценарий выполнен!")
        if Path("screenshot.png").exists():
            st.image("screenshot.png", caption="Скриншот после выполнения")
        if selected_scenario:
            logic.save_run(selected_scenario.id, "success")
    except Exception as e:
        st.error(f"Ошибка: {str(e)}")
        if selected_scenario:
            logic.save_run(selected_scenario.id, "fail")