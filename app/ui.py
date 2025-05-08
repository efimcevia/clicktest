import streamlit as st
import json
from app import state, logic
from datetime import datetime

def add_step_form():
    st.subheader("➕ Добавить шаг")

    with st.container():
        step_type = st.selectbox("Тип шага", ["goto", "click", "fill"], key="step_type")
        selector = ""
        value = ""

        if step_type == "goto":
            value = st.text_input("URL", key="step_value")
        else:
            selector = st.text_input("CSS селектор", key="step_selector")
            if step_type == "fill":
                value = st.text_input("Значение", key="step_value")

        if st.button("Добавить шаг"):
            step = {"type": step_type}
            if selector:
                step["selector"] = selector
            if value:
                step["value"] = value
            state.add_step(step)
            st.success("Шаг добавлен")

def view_steps():
    st.subheader("🧾 Шаги сценария")
    steps = state.get_steps()

    if not steps:
        st.info("Шаги пока не добавлены.")
        return

    for i, step in enumerate(steps, start=1):
        st.code(json.dumps(step, indent=2), language="json")

    if st.button("🗑 Очистить шаги"):
        state.clear_steps()
        st.success("Шаги очищены")

def save_scenario_form():
    st.subheader("💾 Сохранить сценарий")
    steps = state.get_steps()

    if not steps:
        st.info("Добавьте хотя бы один шаг перед сохранением.")
        return

    name = st.text_input("Название сценария", key="scenario_name_input")

    if st.button("Сохранить сценарий"):
        if not name.strip():
            st.warning("Введите название сценария.")
            return

        ok, err = logic.save_scenario(name.strip(), steps)
        if ok:
            st.success(f"Сценарий «{name}» сохранён!")
            state.clear_steps()
        else:
            st.error(err or "Ошибка при сохранении.")


def select_scenario():
    scenarios = logic.get_all_scenarios()
    names = [s.name for s in scenarios]
    selected_name = st.selectbox("Сценарии", ["<Создать новый>"] + names)

    if selected_name != "<Создать новый>":
        s = logic.get_scenario_by_name(selected_name)
        state.clear_steps()
        steps = json.loads(s.steps_json)
        for step in steps:
            state.add_step(step)
        return s
    return None