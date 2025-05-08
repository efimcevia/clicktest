import streamlit as st
import json
from app import state, logic

def step_form():
    with st.form("step_form"):
        st.subheader("➕ Добавить шаги")
        step_type = st.selectbox("Тип шага", ["goto", "click", "fill", "wait_for", "screenshot"])
        selector = st.text_input("Селектор (если нужно)", "")
        value = st.text_input("Значение (URL, текст, время и т.п.)", "")
        submitted = st.form_submit_button("Добавить шаг")

        if submitted:
            step = {"type": step_type}
            if selector:
                step["selector"] = selector
            if value:
                step["value"] = value
            state.add_step(step)
            st.success("Шаг добавлен!")

def step_view():
    st.subheader("🧾 Шаги сценария")
    steps = state.get_steps()

    if not steps:
        st.info("Шаги пока не добавлены.")
    else:
        for step in steps:
            st.code(json.dumps(step, indent=2), language="json")

        # Форма сохранения прямо здесь
        with st.form("save_scenario_form"):
            name = st.text_input("Название сценария", key="save_scenario_name")
            submitted = st.form_submit_button("Сохранить сценарий")

            if submitted:
                if not name:
                    st.warning("Введите название сценария.")
                else:
                    ok, err = logic.save_scenario(name, steps)
                    if ok:
                        st.success("Сценарий сохранён!")
                    else:
                        st.error(err)

        if st.button("Очистить шаги"):
            state.clear_steps()


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