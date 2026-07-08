import os
import subprocess


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = r"C:\Users\mateus.braga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
LOG_FILE = os.path.join(BASE_DIR, "runserver.log")


def main():
    log = open(LOG_FILE, "a", encoding="utf-8")
    subprocess.Popen(
        [PYTHON, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
        cwd=BASE_DIR,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=log,
        close_fds=False,
        creationflags=0x00000008 | 0x00000200 | 0x08000000,
    )


if __name__ == "__main__":
    main()
