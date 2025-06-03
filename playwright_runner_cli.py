# playwright_runner_cli.py
import sys
import json
import time
from playwright.sync_api import sync_playwright

def run_steps(steps):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for step in steps:
            t = step.get("type")
            desc = step.get("description", "") or step.get("value", "")
            start = time.time()

            try:
                if t == "goto":
                    page.goto(step["value"])
                elif t == "click":
                    page.click(step["selector"])
                elif t == "fill":
                    page.fill(step["selector"], step["value"])
                elif t == "wait_for":
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
                    page.locator(step["selector"]).inner_text()
                elif t == "get_attribute":
                    page.locator(step["selector"]).get_attribute(step["attr"])
                elif t == "wait_for_url":
                    page.wait_for_url(step["value"])
                elif t == "eval":
                    page.evaluate(step["script"])
                elif t == "upload_file":
                    page.set_input_files(step["selector"], step["filepath"])
                elif t == "download":
                    with page.expect_download() as download_info:
                        page.click(step["selector"])
                    download = download_info.value
                    download.save_as(step.get("path", "downloaded_file"))
                else:
                    raise ValueError(f"Неизвестный тип действия: {t}")

                status = "success"
            except Exception as e:
                status = "failure"
                desc += f" (Ошибка: {str(e)})"

            duration = round(time.time() - start, 2)
            results.append({
                "title": t,
                "desc": desc,
                "status": status,
                "time": duration
            })

            if status == "failure":
                break  # остановка по ошибке, по желанию

        browser.close()

    print(json.dumps(results))  # возвращаем результат

if __name__ == "__main__":
    raw = sys.stdin.read()
    steps = json.loads(raw)
    run_steps(steps)
