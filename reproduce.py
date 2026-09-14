from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "reproduced"


def run(cmd):
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    run([sys.executable, str(ROOT / "src" / "f2r_paper_reproduction.py"), "--output-dir", str(OUT)])
    run([sys.executable, str(ROOT / "src" / "validate_public.py"), "--output-dir", str(OUT)])
    print("PASS - F2R model-adoption paper reproduction complete.")


if __name__ == "__main__":
    main()
