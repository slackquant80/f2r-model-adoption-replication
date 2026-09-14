from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVID = ROOT / "evidence"

INCUMBENT = "CURRENT4_RANK"
SELECTED = "C3_REX3_CHRONOS20"
THREE_MODEL = "REX3_RANK"
STANDARDIZED = "ZSPACE_REX3_CHRONOS20"


def assert_close(name: str, actual: float, expected: float, tol: float = 5e-6) -> dict:
    ok = math.isfinite(actual) and abs(actual - expected) <= tol
    if not ok:
        raise AssertionError(f"{name}: {actual} != {expected} (tol={tol})")
    return {"check": name, "actual": float(actual), "expected": float(expected), "status": "PASS"}


def compound_return(x: pd.Series) -> float:
    return float(np.prod(1.0 + pd.to_numeric(x, errors="raise").to_numpy(float)) - 1.0)


def recompute_cagr(monthly: pd.DataFrame, summary_row: pd.Series) -> float:
    terminal = 1.0 + compound_return(monthly["net_return"])
    d0 = pd.Timestamp(summary_row["support_start"])
    d1 = pd.Timestamp(summary_row["support_end"])
    years = (d1 - d0).days / 365.25
    return float(terminal ** (1.0 / years) - 1.0)


def top4_set(panel: pd.DataFrame, variant: str, month: str) -> set[str]:
    g = panel[(panel["variant"] == variant) & (panel["origin_signal_month"] == month)]
    return set(g.loc[g["selected_top4"].astype(bool), "asset"])


def decision_similarity(panel: pd.DataFrame, other: str) -> float:
    months = sorted(panel["origin_signal_month"].astype(str).unique())
    vals = []
    for month in months:
        a = top4_set(panel, SELECTED, month)
        b = top4_set(panel, other, month)
        vals.append(len(a & b) / len(a | b))
    return float(np.mean(vals))


def changed_month_count(panel: pd.DataFrame) -> int:
    months = sorted(panel["origin_signal_month"].astype(str).unique())
    return sum(top4_set(panel, SELECTED, m) != top4_set(panel, INCUMBENT, m) for m in months)


def save_figure(fig, output_dir: Path, stem: str) -> None:
    fig.savefig(output_dir / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main(output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics = pd.read_csv(DATA / "PHASE1_POINT_FORECAST_METRICS_v1.0.csv")
    summary = pd.read_csv(DATA / "PHASE1_PORTFOLIO_SUMMARY_v1.0.csv")
    ablation = pd.read_csv(DATA / "PHASE1_ABLATION_CONTRASTS_v1.0.csv")
    monthly = pd.read_csv(DATA / "PHASE1_MONTHLY_RETURNS_v1.0.csv")
    diversity = pd.read_csv(DATA / "PHASE1_DECISION_DIVERSITY_v1.0.csv")
    panel = pd.read_csv(DATA / "PHASE1_TARGET_AND_RANK_PANEL_v1.0.csv", dtype={"origin_signal_month": str})
    attr = pd.read_csv(EVID / "PHASE1_BOUNDARY_DECISION_ATTRIBUTION_v0.1.csv")
    top_events = pd.read_csv(EVID / "PHASE1_BOUNDARY_DECISION_TOP_EVENTS_v0.1.csv")

    S = summary.set_index("variant")

    checks = []

    # Structural checks from the frozen decision panel.
    if panel["origin_signal_month"].nunique() != 112:
        raise AssertionError("Expected 112 signal months")
    if panel["asset"].nunique() != 11:
        raise AssertionError("Expected 11 assets")
    selected_counts = panel.groupby(["variant", "origin_signal_month"])["selected_top4"].sum()
    if not selected_counts.eq(4).all():
        raise AssertionError("Every variant must select exactly four assets per signal month")

    # Recompute CAGR and cumulative one-way turnover from the monthly path.
    for variant in [INCUMBENT, SELECTED, THREE_MODEL, STANDARDIZED, "CURRENT4_CHRONOS20"]:
        m = monthly[monthly["variant"] == variant].sort_values("month")
        row = S.loc[variant]
        cagr = recompute_cagr(m, row)
        turnover = float(m["turnover"].sum())
        checks.append(assert_close(f"{variant}_cagr_from_monthly_path", cagr, float(row["cagr"]), 5e-10))
        checks.append(assert_close(f"{variant}_turnover_from_monthly_path", turnover, float(row["total_one_way_turnover"]), 5e-10))

    # Recompute matched CAGR contrasts from the portfolio summary rather than the stored contrast table.
    ablation_map = ablation.set_index("contrast")["delta_cagr"].to_dict()
    contrasts = {
        "full_adoption_delta_cagr": (SELECTED, INCUMBENT, "FULL_ADOPTION_DELTA"),
        "rf_removal_delta_cagr": (THREE_MODEL, INCUMBENT, "RF_REMOVAL_ONLY"),
        "chronos20_incumbent_delta_cagr": ("CURRENT4_CHRONOS20", INCUMBENT, "CHRONOS20_HOLD_CURRENT4"),
        "chronos20_three_model_delta_cagr": (SELECTED, THREE_MODEL, "CHRONOS20_HOLD_REX3"),
        "rank_vs_standardized_delta_cagr": (SELECTED, STANDARDIZED, "RANK_VS_ZSPACE"),
    }
    for name, (a, b, contrast_id) in contrasts.items():
        actual = float(S.loc[a, "cagr"] - S.loc[b, "cagr"])
        expected = float(ablation_map[contrast_id])
        checks.append(assert_close(name, actual, expected, 5e-12))

    # Decision overlap is recomputed directly from the target/rank panel.
    similarities = {
        "Incumbent ensemble": decision_similarity(panel, INCUMBENT),
        "Three-model conventional ensemble": decision_similarity(panel, THREE_MODEL),
        "Chronos-2 alone": decision_similarity(panel, "CHRONOS_STANDALONE"),
        "Same model mix, standardized forecasts": decision_similarity(panel, STANDARDIZED),
    }
    drow = diversity[((diversity["variant_a"] == SELECTED) & (diversity["variant_b"] == INCUMBENT)) | ((diversity["variant_a"] == INCUMBENT) & (diversity["variant_b"] == SELECTED))]
    if len(drow) != 1:
        raise AssertionError("Expected one stored selected-vs-incumbent diversity row")
    checks.append(assert_close("selected_vs_incumbent_jaccard", similarities["Incumbent ensemble"], float(drow.iloc[0]["mean_top4_jaccard"]), 5e-12))
    if changed_month_count(panel) != 58:
        raise AssertionError("Expected 58 changed Top-4 months")

    # Attribution shares are recomputed from the detailed monthly attribution table.
    total_gap = float(attr["relative_log_wealth_contribution"].sum())
    changed = attr[~attr["same_top4"].astype(bool)]
    positive = changed[changed["relative_log_wealth_contribution"] > 0].sort_values(
        "relative_log_wealth_contribution", ascending=False
    )
    changed_share = float(changed["relative_log_wealth_contribution"].sum() / total_gap)
    top5_net_share = float(positive.head(5)["relative_log_wealth_contribution"].sum() / total_gap)
    top5_positive_share = float(
        positive.head(5)["relative_log_wealth_contribution"].sum()
        / positive["relative_log_wealth_contribution"].sum()
    )
    checks.append(assert_close("changed_decisions_share_of_net_log_gap", changed_share, 0.9941202468514544, 5e-12))
    checks.append(assert_close("top5_share_of_net_log_gap", top5_net_share, 0.7125304530778578, 5e-12))
    checks.append(assert_close("top5_share_of_positive_changed_contribution", top5_positive_share, 0.35150706847038465, 5e-12))

    # Reported Sharpe and RMSE anchors are verified against the frozen scientific summary.
    checks.append(assert_close("incumbent_sharpe_anchor", float(S.loc[INCUMBENT, "sharpe_rf0"]), 0.8912607910074706, 5e-12))
    checks.append(assert_close("selected_sharpe_anchor", float(S.loc[SELECTED, "sharpe_rf0"]), 0.9871266596269239, 5e-12))
    chronos_rmse = float(metrics.loc[metrics["model"] == "Chronos2_ZeroShot", "rmse"].iloc[0])
    checks.append(assert_close("chronos_rmse_anchor", chronos_rmse, 0.05700360225840087, 5e-12))

    # Figure 1: forecast error vs standalone portfolio Sharpe.
    model_map = {
        "Chronos2_ZeroShot": ("CHRONOS_STANDALONE", "Chronos-2"),
        "ElasticNet": ("ELASTICNET_STANDALONE", "Elastic Net"),
        "RandomForest": ("RANDOMFOREST_STANDALONE", "Random Forest"),
        "Ridge": ("RIDGE_STANDALONE", "Ridge"),
        "XGBoost": ("XGBOOST_STANDALONE", "XGBoost"),
    }
    rows = []
    for _, row in metrics.iterrows():
        variant, label = model_map[row["model"]]
        rows.append((label, float(row["rmse"]), float(S.loc[variant, "sharpe_rf0"])))
    f1 = pd.DataFrame(rows, columns=["label", "rmse", "sharpe"])

    fig, ax = plt.subplots(figsize=(7.1, 3.75))
    ax.scatter(f1["rmse"], f1["sharpe"], s=54)
    offsets = {
        "Chronos-2": (8, -17),
        "Elastic Net": (7, 7),
        "Random Forest": (7, -15),
        "Ridge": (7, 7),
        "XGBoost": (7, 7),
    }
    for _, row in f1.iterrows():
        ax.annotate(
            row["label"],
            (row["rmse"], row["sharpe"]),
            xytext=offsets[row["label"]],
            textcoords="offset points",
            fontsize=8.8,
            ha="left",
            va="center",
        )
    ax.set_xlabel("Point-forecast RMSE (lower is better)", fontsize=9.2)
    ax.set_ylabel("Standalone portfolio Sharpe ratio (higher is better)", fontsize=9.2)
    ax.tick_params(axis="both", labelsize=8.4)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.5f"))
    ax.set_xlim(0.05490, 0.05718)
    ax.set_ylim(0.745, 0.980)
    ax.grid(True, alpha=0.22)
    fig.tight_layout(pad=0.5)
    save_figure(fig, output_dir, "Figure_1_reproduced")

    # Figure 2: matched ensemble contrasts.
    f2 = pd.DataFrame(
        [
            ("Selected hybrid vs incumbent", (S.loc[SELECTED, "cagr"] - S.loc[INCUMBENT, "cagr"]) * 100),
            ("Chronos-2 added after Random Forest removal", (S.loc[SELECTED, "cagr"] - S.loc[THREE_MODEL, "cagr"]) * 100),
            ("Chronos-2 added to incumbent", (S.loc["CURRENT4_CHRONOS20", "cagr"] - S.loc[INCUMBENT, "cagr"]) * 100),
            ("Random Forest removed", (S.loc[THREE_MODEL, "cagr"] - S.loc[INCUMBENT, "cagr"]) * 100),
        ],
        columns=["label", "delta_pp"],
    )
    fig, ax = plt.subplots(figsize=(7.4, 2.55))
    bars = ax.barh(f2["label"], f2["delta_pp"])
    ax.invert_yaxis()
    ax.set_xlabel("CAGR difference (percentage points)", fontsize=9.0)
    ax.tick_params(axis="x", labelsize=8.2)
    ax.tick_params(axis="y", labelsize=8.3)
    ax.set_xlim(0, 2.48)
    ax.grid(True, axis="x", alpha=0.22)
    for bar, value in zip(bars, f2["delta_pp"]):
        ax.text(value + 0.04, bar.get_y() + bar.get_height() / 2, f"+{value:.2f}", va="center", ha="left", fontsize=8.6)
    fig.tight_layout(pad=0.35)
    save_figure(fig, output_dir, "Figure_2_reproduced")

    # Figure 3: Top-4 decision similarity.
    f3 = pd.DataFrame(list(similarities.items()), columns=["label", "jaccard"])
    fig, ax = plt.subplots(figsize=(7.1, 2.7))
    bars = ax.barh(f3["label"], f3["jaccard"])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("Average Top-4 overlap (Jaccard similarity; 1 = identical)", fontsize=9.0)
    ax.tick_params(axis="x", labelsize=8.2)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.grid(True, axis="x", alpha=0.22)
    for bar, value in zip(bars, f3["jaccard"]):
        ax.text(value + 0.015, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", va="center", fontsize=8.6)
    fig.tight_layout(pad=0.4)
    save_figure(fig, output_dir, "Figure_3_reproduced")

    # Figure 4: largest favorable and unfavorable changed-decision contributions.
    favorable = top_events[top_events["direction"] == "Favorable"].copy()
    unfavorable = top_events[top_events["direction"] == "Unfavorable"].iloc[::-1].copy()
    e = pd.concat([favorable, unfavorable], ignore_index=True)
    e["label"] = (
        e["signal_month"].astype(str)
        + ": "
        + e["leaving_incumbent"].fillna("")
        + " to "
        + e["entering_hybrid"].fillna("")
    )
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    bars = ax.barh(e["label"], e["approx_relative_return_pp"])
    ax.invert_yaxis()
    ax.axvline(0, linewidth=0.8)
    ax.set_xlabel("Approx. contribution to hybrid-vs-incumbent relative wealth (%)", fontsize=9.0)
    ax.tick_params(axis="x", labelsize=8.2)
    ax.tick_params(axis="y", labelsize=8.2)
    ax.grid(True, axis="x", alpha=0.22)
    for bar, value in zip(bars, e["approx_relative_return_pp"]):
        ax.text(
            value + (0.08 if value >= 0 else -0.08),
            bar.get_y() + bar.get_height() / 2,
            f"{value:+.1f}%",
            va="center",
            ha="left" if value >= 0 else "right",
            fontsize=8.0,
        )
    fig.tight_layout(pad=0.4)
    save_figure(fig, output_dir, "Figure_4_reproduced")

    # Figure 5: Chronos-2 contribution sensitivity within the three-model family.
    weights = [0, 10, 20, 25, 33, 50]
    variants = [
        "REX3_RANK",
        "REX3_CHRONOS10",
        SELECTED,
        "C1_REX3_CHRONOS25",
        "REX3_CHRONOS33",
        "REX3_CHRONOS50",
    ]
    cagr_values = [float(S.loc[v, "cagr"]) * 100 for v in variants]
    fig, ax = plt.subplots(figsize=(7.1, 2.75))
    ax.plot(weights, cagr_values, marker="o")
    ax.set_xlabel("Chronos-2 model-combination contribution (%)", fontsize=9.0)
    ax.set_ylabel("CAGR (%)", fontsize=9.0)
    ax.set_xticks(weights)
    ax.tick_params(axis="both", labelsize=8.3)
    ax.grid(True, alpha=0.22)
    for x, y in zip(weights, cagr_values):
        ax.text(x, y + 0.08, f"{y:.1f}", ha="center", fontsize=8.3)
    fig.tight_layout(pad=0.4)
    save_figure(fig, output_dir, "Figure_5_reproduced")

    # Compact public outputs.
    headline_variants = [
        INCUMBENT,
        THREE_MODEL,
        "CURRENT4_CHRONOS20",
        SELECTED,
        STANDARDIZED,
        "C2_CURRENT4_CHRONOS50",
        "C1_REX3_CHRONOS25",
        "REX3_CHRONOS50",
    ]
    S.loc[headline_variants].reset_index().to_csv(output_dir / "headline_portfolio_metrics.csv", index=False)

    report = {
        "status": "PASS",
        "checks": checks,
        "signal_months": int(panel["origin_signal_month"].nunique()),
        "assets": int(panel["asset"].nunique()),
        "changed_top4_months": int(changed_month_count(panel)),
        "note": "Sharpe and RMSE anchors are verified against frozen scientific summaries; CAGR, turnover, matched deltas, Top-4 overlap, and attribution shares are recomputed from included derived evidence.",
    }
    (output_dir / "REPRODUCTION_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS - reported outputs reproduced from frozen public evidence.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.output_dir.resolve()))
