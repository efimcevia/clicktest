import streamlit as st
import json
import datetime
import os
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from app import ui, logic, runner, state
from pathlib import Path


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

def search_and_display_scenarios():
    # Поле поиска
    search_query = st.text_input("Поиск по названию", "")
    
    # Функция для поиска и отображения сценариев
    def fetch_and_display_scenarios(query: str):
        with Session() as session:
            results = session.execute(
                sa.text("SELECT * FROM scenarios WHERE LOWER(name) LIKE LOWER(:query)"),
                {"query": f'%{query}%'}
            ).fetchall()
        
        if results:
            scenario_buttons = [scenario.name for scenario in results]
            selected_scenario_name = st.radio("Найденные сценарии:", scenario_buttons)
            
            # Загружаем выбранный сценарий
            if selected_scenario_name:
                selected_scenario = next(s for s in results if s.name == selected_scenario_name)
                state.set_selected_scenario(selected_scenario)
        else:
            st.write("Сценарии не найдены.")

    # Выполняем поиск при изменении поля
    if search_query:
        fetch_and_display_scenarios(search_query)
    else:
        selected_scenario = ui.select_scenario()
        state.set_selected_scenario(selected_scenario)

    # Получаем шаги
    steps = state.get_steps()

def history_render():

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

   
def select_scenario():
    scenarios = logic.get_all_scenarios()
    names = [s.name for s in scenarios]
    selected_name = st.selectbox("Сценарии", ["<Создать новый>"] + names, key="scenario_selector")

    if selected_name != "<Создать новый>":
        s = logic.get_scenario_by_name(selected_name)
        state.clear_steps()
        steps = json.loads(s.steps_json)
        for step in steps:
            state.add_step(step)
        return s
    return None

# Основная часть Streamlit приложения
def main():
    st.title("Конструктор сценариев")

    # Отображаем элементы интерфейса
    export_scenario()  # Кнопка для экспорта сценария
    import_scenario()  # Кнопка для импорта сценария
    step_form()
    step_view()        # Отображение шагов сценария
    select_scenario()  # Выбор сценария

if __name__ == "__main__":
    main()


