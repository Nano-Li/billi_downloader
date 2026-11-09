"""Prepare the vault-local yutto environment and its FFmpeg dependency."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, type=Path)
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Python 3.11 or newer is required.")
    vault = args.vault.expanduser().resolve()
    if not vault.is_dir():
        parser.error("The vault directory must already exist.")
    environment = vault / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        if environment.exists() and any(environment.iterdir()):
            parser.error("Existing .venv is incomplete; inspect it before retrying.")
        venv.EnvBuilder(with_pip=True).create(environment)
    subprocess.run([str(python), "-c",
                    "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'"], check=True)
    pip = [str(python), "-m", "pip", "install", "--disable-pip-version-check"]
    requirements = Path(__file__).resolve().parents[1] / "requirements.txt"
    subprocess.run([*pip, "-r", str(requirements)], check=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        subprocess.run([*pip, "imageio-ffmpeg==0.6.0"], check=True)
        ffmpeg = subprocess.check_output(
            [str(python), "-c", "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"],
            text=True, encoding="utf-8",
        ).strip()
    result = subprocess.run([ffmpeg, "-version"], check=True, capture_output=True, text=True)
    subprocess.run([str(python), "-m", "yutto", "--version"], check=True)
    print(f"Python: {python}")
    print(f"FFmpeg: {ffmpeg}")
    print(result.stdout.splitlines()[0])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Setup failed: {error}", file=sys.stderr)
        raise SystemExit(1)
