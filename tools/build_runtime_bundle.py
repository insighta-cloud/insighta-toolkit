"""Build a self-contained AgentCore direct-code deployment bundle."""

from __future__ import annotations

import shutil
import subprocess
from os import utime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src-python"
APP = ROOT / "apps" / "agentcore"
OUTPUT = ROOT / ".runtime-package"


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python-platform",
            "aarch64-unknown-linux-gnu",
            "--python-version",
            "3.13",
            "--target",
            str(OUTPUT),
            "-r",
            str(SOURCE / "requirements.txt"),
        ],
        check=True,
        cwd=ROOT,
    )
    shutil.copy2(APP / "main.py", OUTPUT / "main.py")
    shutil.copytree(SOURCE / "insighta_toolkit", OUTPUT / "insighta_toolkit")
    for cache in OUTPUT.rglob("__pycache__"):
        shutil.rmtree(cache)
    for path in OUTPUT.rglob("*"):
        if path.is_file():
            utime(path, (0, 0))


if __name__ == "__main__":
    main()
