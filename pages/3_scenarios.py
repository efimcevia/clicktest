import streamlit as st
from app import ui, logic, runner, state
from pathlib import Path
from pathlib import Path
from datetime import datetime
import uuid


st.title("📋 Сценарии")
state.init_state()

selected_scenario = ui.select_scenario()
state.set_selected_scenario(selected_scenario)

steps = state.get_steps()

if steps and st.button("🚀 Выполнить сценарий"):
    try:
        # Запуск сценария
        runner.run_steps_safe(steps)

        # Проверка скриншота
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_name = f"screenshot_{uuid.uuid4().hex[:8]}_{timestamp}.png"
        output_path = Path("screenshots") / unique_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Path("screenshot.png").rename(output_path)
        screenshot_path = str(output_path)

        if selected_scenario:
            run_id = logic.save_run(selected_scenario.id, "success")

            if screenshot_path:
                logic.save_screenshot(run_id, "TestRun", screenshot_path)

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")
        if selected_scenario:
            logic.save_run(selected_scenario.id, "fail")

ui.delete_scenario_button()