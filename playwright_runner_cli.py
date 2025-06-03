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
            elif t == "screenshot":
                page.screenshot(path="screenshot.png")
            elif t == "wait_for_selector":
                page.wait_for_selector(step["selector"])
            elif t == "press":
                page.press(step["selector"], step["value"])


        browser.close()

if __name__ == "__main__":
    raw = sys.stdin.read()
    steps = json.loads(raw)
    run_steps(steps)
