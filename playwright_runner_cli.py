# playwright_runner_cli.py
import sys
import json
from playwright.sync_api import sync_playwright

def run_steps(steps):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for step in steps:
            t = step.get("type")

            if t == "goto":
                page.goto(step["value"])

            elif t == "click":
                page.click(step["selector"])

            elif t == "fill":
                page.fill(step["selector"], step["value"])

            elif t == "wait_for":
                import time
                time.sleep(float(step["value"]))

            elif t == "wait_for_selector":
                page.wait_for_selector(step["selector"])

            elif t == "press":
                page.press(step["selector"], step["value"])

            elif t == "type":
                page.type(step["selector"], step["value"])

            elif t == "hover":
                page.hover(step["selector"])

            elif t == "check":
                page.check(step["selector"])

            elif t == "uncheck":
                page.uncheck(step["selector"])

            elif t == "select_option":
                page.select_option(step["selector"], step["value"])

            elif t == "screenshot":
                path = step.get("value", "screenshot.png")
                page.screenshot(path=path)

            elif t == "get_text":
                text = page.locator(step["selector"]).inner_text()
                print(f"Текст элемента: {text}")

            elif t == "get_attribute":
                attr = page.locator(step["selector"]).get_attribute(step["attr"])
                print(f"Значение атрибута: {attr}")

            elif t == "wait_for_url":
                page.wait_for_url(step["value"])

            elif t == "eval":
                # Выполняет произвольный JavaScript код на странице
                result = page.evaluate(step["script"])
                print(f"Результат eval: {result}")

            elif t == "upload_file":
                page.set_input_files(step["selector"], step["filepath"])

            elif t == "download":
                with page.expect_download() as download_info:
                    page.click(step["selector"])
                download = download_info.value
                download.save_as(step.get("path", "downloaded_file"))

            else:
                print(f"❌ Неизвестный тип действия: {t}")



        browser.close()

if __name__ == "__main__":
    raw = sys.stdin.read()
    steps = json.loads(raw)
    run_steps(steps)
