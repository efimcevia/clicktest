from playwright_runner import run_steps as real_run_steps

def run_steps_safe(steps: list):
    return real_run_steps(steps)