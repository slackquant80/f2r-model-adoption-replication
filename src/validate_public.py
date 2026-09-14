from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {
    "Figure_1_reproduced.pdf",
    "Figure_1_reproduced.png",
    "Figure_2_reproduced.pdf",
    "Figure_2_reproduced.png",
    "Figure_3_reproduced.pdf",
    "Figure_3_reproduced.png",
    "Figure_4_reproduced.pdf",
    "Figure_4_reproduced.png",
    "Figure_5_reproduced.pdf",
    "Figure_5_reproduced.png",
    "headline_portfolio_metrics.csv",
    "REPRODUCTION_REPORT.json",
}


def main(output_dir: Path) -> int:
    present = {p.name for p in output_dir.iterdir() if p.is_file()}
    missing = sorted(REQUIRED - present)
    if missing:
        raise RuntimeError(f"Missing reproduced outputs: {missing}")

    report = json.loads((output_dir / "REPRODUCTION_REPORT.json").read_text(encoding="utf-8"))
    if report.get("status") != "PASS":
        raise RuntimeError("Reproduction report is not PASS")
    if report.get("signal_months") != 112 or report.get("assets") != 11:
        raise RuntimeError("Panel identity check failed")
    if report.get("changed_top4_months") != 58:
        raise RuntimeError("Changed-decision count check failed")
    if any(x.get("status") != "PASS" for x in report.get("checks", [])):
        raise RuntimeError("One or more numerical checks failed")

    print("PASS - public reproduction outputs validated.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.output_dir.resolve()))
