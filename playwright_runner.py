import subprocess
import json
import streamlit as st

def run_steps(steps: list):
    try:
        process = subprocess.Popen(
            ["python", "playwright_runner_cli.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=json.dumps(steps))

        if process.returncode == 0:
            try:
                results = json.loads(stdout)
                return results
            except json.JSONDecodeError:
                st.error("Ошибка парсинга ответа от runner.")
                st.code(stdout)
                return []
        else:
            st.error("Произошла ошибка при выполнении:")
            st.code(stderr)
            return []

    except Exception as e:
        st.error("Критическая ошибка:")
        st.exception(e)
        return []
