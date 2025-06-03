import streamlit as st
import pandas as pd
from app.logic import get_all_test_runs, get_test_run_by_id
from app.ui import generate_test_run_report_pdf 

runs = get_all_test_runs()

if "selected_run_id" not in st.session_state:
    st.session_state.selected_run_id = None

if st.session_state.selected_run_id is None:
    st.title("📋 Отчёт о запусках сценариев")

    for run in runs:
        scenario = run.scenario.name if run.scenario else "Без названия"
        status_icon = "🟢" if run.status == "success" else "🔴"
        run_id = run.id
        timestamp = run.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        col1, col2 = st.columns([5, 1])
        col1.markdown(f"{status_icon} **ID: {run_id}** **{scenario}** — `{timestamp}`")
        if col2.button("Подробнее", key=f"btn_{run.id}"):
            st.session_state.selected_run_id = run.id
            st.rerun()

else:
    run = get_test_run_by_id(st.session_state.selected_run_id)
    if not run:
        st.error("Запуск не найден")
    else:
        st.markdown(f"## 🧾 Отчёт о запуске: **{run.scenario.name}**")
        st.markdown(f"## ID запуска: **{run.id}**")
        st.markdown(f"**Дата:** {run.timestamp.strftime('%d.%m.%Y %H:%M:%S')}")
        st.markdown(f"**Тестировщик:** {run.tester_name}")
        st.markdown(f"**Статус:** {'🟢 Успешно' if run.status == 'success' else '🔴 Ошибка'}")
        st.markdown("---")
        st.markdown("### ✅ Результаты шагов")

        df = pd.DataFrame([
            {
                "#": i + 1,
                "Шаг": case.title,
                "Описание": case.description,
                "Статус": "🟢 Успешно" if case.status == "success" else "🔴 Ошибка",
                "Время": f"{case.duration:.2f} сек"
            }
            for i, case in enumerate(run.test_cases)
        ])
        st.table(df)

        if st.button("← Назад"):
            st.session_state.selected_run_id = None
            st.rerun()

        
    if st.button("📥 Сформировать PDF"):
        pdf = generate_test_run_report_pdf(runs)
        st.download_button(
            label="💾 Скачать PDF",
            data=pdf,
            file_name="test_run_report.pdf",
            mime="application/pdf"
        )