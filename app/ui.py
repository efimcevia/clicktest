import streamlit as st
import json
from app import state, logic
from datetime import datetime
import datetime

def export_scenario():
    steps = state.get_steps()
    if not steps:
        st.warning("Нет шагов для экспорта.")
        return

    # Формируем JSON
    json_data = json.dumps(steps, indent=2)
    
    # Создаем имя файла
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"scenario_{timestamp}.json"

    # Кнопка для скачивания
    st.download_button(
        label="Экспортировать сценарий",
        data=json_data,
        file_name=filename,
        mime='application/json'
    )
    st.success("Сценарий экспортирован!")

def import_scenario():
    uploaded_file = st.file_uploader("Выберите .json файл для импорта", type=["json"])
    
    if uploaded_file is not None:
        try:
            # Считываем содержимое файла
            content = uploaded_file.read()
            steps = json.loads(content)

            # Валидация структуры данных
            if not isinstance(steps, list) or not all(isinstance(step, dict) and "type" in step for step in steps):
                st.error("Файл повреждён или невалидный сценарий.")
                return

            # Перезаписываем сессия с новыми шагами
            state.clear_steps()
            for step in steps:
                state.add_step(step)

            st.success("Сценарий успешно импортирован!")
        
        except json.JSONDecodeError:
            st.error("Ошибка чтения JSON. Проверьте файл.")

def add_step_form():
    st.subheader("➕ Добавить шаг")

    with st.container():
        step_type = st.selectbox("Тип шага", ["goto", "click", "fill","cwait_for","screenshot"], key="step_type")
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
        if st.button(f"✏️ Редактировать шаг {i}", key=f"edit_step_{i}"):
            edit_step_form(i - 1)  # Передаем индекс для редактирования

    if st.button("🗑 Очистить шаги"):
        state.clear_steps()
        st.success("Шаги очищены")

def edit_step_form(step_index):
    steps = state.get_steps()
    
    if step_index < 0 or step_index >= len(steps):
        return

    st.subheader(f"✏️ Редактировать шаг {step_index + 1}")

    step = steps[step_index]
    step_type = step.get("type")
    selector = step.get("selector", "")
    value = step.get("value", "")

    with st.container():
        step_type = st.selectbox("Тип шага", ["goto", "click", "fill","cwait_for","screenshot"], index=["goto", "click", "fill","cwait_for","screenshot"].index(step_type), key=f"step_type_edit_{step_index}")
        selector = st.text_input("CSS селектор", selector, key=f"step_selector_edit_{step_index}")
        if step_type == "fill":
            value = st.text_input("Значение", value, key=f"step_value_edit_{step_index}")
        elif step_type == "goto":
            value = st.text_input("URL", value, key=f"step_value_edit_{step_index}")

        if st.button("Сохранить изменения", key=f"save_edit_step_{step_index}"):
            updated_step = {"type": step_type}
            if selector:
                updated_step["selector"] = selector
            if value:
                updated_step["value"] = value
            state.update_step(step_index, updated_step)  # Обновляем шаг в состоянии
            st.success("Шаг обновлён!")

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
    selected_name = st.selectbox("Сценарии", [""] + names)

    if selected_name != "<Создать новый>":
        s = logic.get_scenario_by_name(selected_name)
        state.clear_steps()
        steps = json.loads(s.steps_json)
        for step in steps:
            state.add_step(step)
        return s
    return None