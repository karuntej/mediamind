#!/usr/bin/env python3
"""Run MediaMind stack with one command.

Starts Ollama (if installed), the FastAPI backend via uvicorn and the
Streamlit UI. Any existing processes are terminated so ports do not
need to be cleared manually.
"""
import subprocess
import shutil
import signal
import time
import sys


DEVNULL = subprocess.DEVNULL


def kill_process(pattern: str) -> None:
    """Terminate processes matching the pattern using pkill."""
    if shutil.which("pkill"):
        subprocess.run(["pkill", "-f", pattern], stdout=DEVNULL, stderr=DEVNULL)


def start(cmd: list[str]):
    return subprocess.Popen(cmd)


def main() -> None:
    # Stop any previous runs
    for pat in ("uvicorn", "streamlit run", "ollama serve"):
        kill_process(pat)

    processes = []

    # Start Ollama server if available
    if shutil.which("ollama"):
        processes.append(start(["ollama", "serve"]))
        time.sleep(2)
    else:
        print("⚠️  ollama not installed - skipping")

    # Start FastAPI backend
    processes.append(start(["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]))
    time.sleep(2)

    # Start Streamlit UI
    processes.append(start(["streamlit", "run", "ui/app.py"]))

    def shutdown(*args):
        for p in processes:
            p.terminate()
        for p in processes:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Wait on Streamlit process
    processes[-1].wait()


if __name__ == "__main__":
    main()
