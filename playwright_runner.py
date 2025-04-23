from playwright.sync_api import sync_playwright
import time

def run_steps(steps: list):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for step in steps:
            t = step["type"]
            if t == "goto":
                page.goto(step["value"])
            elif t == "click":
                page.click(step["selector"])
            elif t == "fill":
                page.fill(step["selector"], step["value"])
            elif t == "wait_for":
                time.sleep(float(step["value"]))
            elif t == "screenshot":
                page.screenshot(path="screenshot.png")

        browser.close()