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
    "Figure_6_reproduced.pdf",
    "Figure_6_reproduced.png",
    "FIGURE_6_METRICS.json",
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

    f6 = json.loads((output_dir / "FIGURE_6_METRICS.json").read_text(encoding="utf-8"))
    if (f6.get("status") != "PASS" or f6.get("monthly_observations") != 112
        or f6.get("last_month_partial_through") != "2026-08-03"
        or f6.get("daily_performance_or_drawdown_reconstructed") is not False):
        raise RuntimeError("Figure 6 monthly clock/claim checks failed")
    anchors = {"CURRENT4_RANK": 3.6217583326610043,
               "C3_REX3_CHRONOS20": 4.3204624974884,
               "C2_CURRENT4_CHRONOS50": 4.495479414208333}
    if any(abs(float(f6["terminal_net_wealth"][key]) - val) > 1e-9 for key,val in anchors.items()):
        raise RuntimeError("Figure 6 exact frozen wealth anchors mismatch")
    print("PASS - public reproduction outputs validated.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.output_dir.resolve()))
