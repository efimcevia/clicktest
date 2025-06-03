import streamlit as st
import json
from app import state, logic
from datetime import datetime
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

SUPPORTED_STEP_TYPES = [
            "goto",
            "click",
            "fill",
            "wait_for",
            "wait_for_selector",
            "press",
            "type",
            "hover",
            "check",
            "uncheck",
            "select_option",
            "screenshot",
            "get_text",
            "get_attribute",
            "wait_for_url",
            "eval",
            "upload_file",
            "download"
        ]
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
        step_type = st.selectbox("Тип шага", SUPPORTED_STEP_TYPES, key="step_type")
        description = st.text_input("Описание", key="step_description")

        selector = ""
        value = ""

        if step_type == "goto":
            value = st.text_input("URL", key="step_value")
        if step_type == "screenshot":
            value = st.text_input("URL", key="step_value")
        else:
            selector = st.text_input("CSS селектор", key="step_selector")
            if step_type == "fill":
                value = st.text_input("Значение", key="step_value")

        if st.button("Добавить шаг"):
            step = {"type": step_type, "description": description}
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

    edit_steps()
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


import streamlit as st

def edit_steps():
    # Кнопка, управляющая отображением редактора
    if "show_editor" not in st.session_state:
        st.session_state.show_editor = False

    if not st.session_state.show_editor:
        if st.button("✏️ Редактировать шаги"):
            st.session_state.show_editor = True
        return  # Прерываем, пока не нажали кнопку

    steps = state.get_steps()

    if not steps:
        st.info("Нет шагов для редактирования.")
        return

    for i, step in enumerate(steps):
        st.markdown(f"**Шаг {i+1}**")
        col1, col2, col3, col4, col5 = st.columns([3, 2, 4, 1, 5])

        with col1:
            step["selector"] = st.text_input("Селектор", value=step.get("selector", ""), key=f"selector_{i}")
        with col2:
            step["type"] = st.selectbox(
                "Тип", options=SUPPORTED_STEP_TYPES,
                index=SUPPORTED_STEP_TYPES.index(step.get("type", "click")),
                key=f"type_{i}"
            )
        with col3:
            if step["type"] in ["fill", "goto"]:
                step["value"] = st.text_input("Значение", value=step.get("value", ""), key=f"value_{i}")
            else:
                step["value"] = None
        with col4:
            step['description'] = st.text_area("Описание", value=step.get('description', ''), key=f"description_{i}")
        with col5:
            if st.button("🗑", key=f"delete_{i}"):
                steps.pop(i)
                state.clear_steps()
                for s in steps:
                    state.add_step(s)

    if st.button("💾 Сохранить изменения"):
        state.clear_steps()
        for step in steps:
            state.add_step(step)
        st.success("Шаги обновлены")


def delete_scenario_button():
    scenario = state.get_selected_scenario()

    if not scenario:
        st.info("Сценарий не выбран.")
        return

    st.warning(f"Удалить сценарий «{scenario.name}»? Это действие необратимо.")

    if st.button("❌ Удалить сценарий"):
        ok, err = logic.delete_scenario(scenario.id)
        if ok:
            st.success("Сценарий удалён.")


pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSans.ttf'))
def generate_test_run_report_pdf(runs) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setFont("DejaVu", 12)

    y = height - 50
    pdf.drawString(50, y, f"📄 Отчёт о запуске сценариев — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 40

    for run in runs:
        scenario_name = run.scenario.name if run.scenario else "Без названия"
        status_icon = "✅" if run.status == "success" else "❌"
        status_text = "успех" if run.status == "success" else "провал"
        line = f"{status_icon} [{run.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] — {scenario_name} — {status_text}"
        pdf.drawString(50, y, line)
        y -= 20
        if y < 50:
            pdf.showPage()
            pdf.setFont("DejaVu", 12)
            y = height - 50

    pdf.save()
    buffer.seek(0)
    return buffer.read()


def render_run_details(run):
    st.markdown(f"## Отчёт о тестировании веб-приложения: **ClickTest**")

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**Дата:** {run.timestamp.strftime('%d.%m.%Y')}")
    col2.markdown(f"**Версия сборки:** 1.2.3-beta")
    col3.markdown(f"**Тестировщик:** Григорьев Дмитрий")
    st.markdown(f"**Среда:** Windows 11 / Chrome 124.0 / 1920x1080")

    st.markdown("---")
    st.markdown("### 🎯 Цель тестирования")
    st.markdown("Проверка работоспособности ключевых пользовательских сценариев...")

    st.markdown("### ✅ Результаты тест-кейсов")

    test_cases = run.test_cases  # если хранятся в БД
    # или временно:
    test_cases = [
        {"title": "Навигация между страницами", "desc": "Переходы через sidebar", "status": "success", "time": 2.1},
        {"title": "Создание нового сценария", "desc": "Через форму с 3 шагами", "status": "success", "time": 3.8},
        {"title": "Запуск сценария", "desc": "Клики по DOM", "status": "success", "time": 5.6},
        {"title": "Просмотр отчёта", "desc": "Проверка UI таблицы", "status": "success", "time": 1.4},
        {"title": "Поведение при пустом сценарии", "desc": "Запуск без шагов", "status": "failure", "time": 0.5},
    ]

    import pandas as pd
    df = pd.DataFrame([
        {
            "#": i + 1,
            "Название": case["title"],
            "Описание": case["desc"],
            "Статус": "🟢 Успешно" if case["status"] == "success" else "🔴 Ошибка",
            "Время": f'{case["time"]} сек'
        }
        for i, case in enumerate(test_cases)
    ])
    st.table(df)

    # Вывод
    passed = sum(1 for c in test_cases if c["status"] == "success")
    total = len(test_cases)
    st.markdown("### 📌 Вывод")
    st.success(f"Тестирование завершено: {passed}/{total} кейсов пройдены успешно.")
    if passed < total:
        st.warning("Некоторые кейсы завершились с ошибками. Необходимо провести доработку.")
