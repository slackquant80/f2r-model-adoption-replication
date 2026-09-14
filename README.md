# F2R Model-Adoption Replication Materials

Replication materials for **A Second Opinion for the Portfolio: How a New Forecasting Model Changes Cross-Asset Allocation Decisions** by Sungkyu Lee (2026), SlackQuant Investment Research Series.

## Scope

This repository reproduces the paper-level figures and numerical checks from **frozen derived research evidence**. It is intentionally narrower than the scientific forecasting pipeline and the production Forecast-to-Rank Allocation (F2R) system.

The public replay:

- recomputes CAGR and cumulative turnover from the included monthly portfolio paths;
- recomputes the matched CAGR contrasts from the included portfolio summaries;
- recomputes Top-4 overlap and changed-decision counts from the frozen target/rank panel;
- recomputes the reported attribution concentration shares from the detailed attribution evidence;
- regenerates Figures 1–5; and
- verifies the reported Sharpe-ratio and RMSE anchors against the frozen scientific summaries.

It does **not** rerun Chronos-2 inference, refit the conventional forecasting models from raw market data, recreate the scientific backtest from downloaded source data, or expose live F2R production configuration.

Accordingly, this is a **paper-level research replication package from frozen derived evidence**, not a raw-data model-training replication and not a second production implementation.

## One-command reproduction

Python 3.11+ is recommended.

```bash
python -m pip install -r requirements.txt
python reproduce.py
```

A successful run ends with:

```text
PASS - F2R model-adoption paper reproduction complete.
```

Generated outputs are written to `reproduced/` and are intentionally not version-controlled.

## Experimental clock and accounting

- Signal dates: 112 monthly decisions, March 2017 through June 2026.
- Portfolio-performance support: May 1, 2017 through August 3, 2026.
- Signal cutoff: last common U.S. market close at or before month-end.
- Execution: first subsequent common close.
- Portfolio rule: Top-4, 25% target weight per selected ETF.
- Between rebalances: weights drift with market prices.
- One-way turnover: half-L1 distance between drifted pre-trade weights and target weights.
- Transaction cost: 10 basis points per side, applied bilaterally through turnover.
- Sharpe ratio in the scientific summary: daily net returns, zero risk-free rate, annualized by sqrt(252).

The first March 2017 signal is executed in early April, but reported performance starts May 1 to exclude the initial partial month. The series extends through August 3, 2026 to complete the holding interval associated with the final June 2026 signal.

## Forecast-information boundary

At each historical signal date, the comparisons share the same F2R-side price-data domain and the same portfolio implementation rules. The models themselves are not informationally identical.

The conventional models use engineered price features fitted within F2R. Chronos-2 consumes a sequence of daily log returns and brings prior information from pretraining. The Chronos-2 pretraining corpus and its temporal overlap with the historical evaluation window are not audited here.

The Chronos-2 evidence is therefore a **retrospective technology counterfactual**, not a real-time historical out-of-sample track record.

## Integration comparison

For the matched rank-versus-standardized comparison, the frozen forecasts, three conventional models, Chronos-2 contribution, 80/20 model-combination weights, Top-4 rule, execution clock, and transaction-cost treatment are held fixed. Only the forecast-integration interface changes.

## Repository map

```text
.
├── README.md
├── reproduce.py
├── requirements.txt
├── CITATION.cff
├── DATA_AND_RIGHTS.md
├── SOURCE_IDENTITY.md
├── METHODS_AND_CLAIM_BOUNDARY.md
├── TIE_BREAKING_AND_INTEGRATION_SPEC.md
├── VARIANT_MAP.md
├── src/
│   ├── f2r_paper_reproduction.py
│   └── validate_public.py
├── data/
├── evidence/
└── reference/
    ├── figures/
    ├── metadata/
    └── A_Second_Opinion_for_the_Portfolio.pdf
```

Technical research identifiers are retained in the frozen CSVs so the public evidence remains identical to the audited research snapshot. `VARIANT_MAP.md` maps them to the reader-facing configurations used in the paper.

## Figure reproducibility

The reproduction script regenerates the data, ordering, labels, axes, and marked sensitivity points used in Figures 1–5. Exact PDF/PNG bytes can still differ across operating systems because font rendering, Matplotlib backends, FreeType versions, and PDF serialization are environment-sensitive. Numerical equality, figure content, and validation checks—not cross-platform byte identity—define public replay success.

## Disclosure boundary

The repository follows an **architecture-visible / recipe-protected** disclosure boundary. It exposes the frozen evidence and calculations needed to audit the paper while withholding live production configuration, private runtime state, and model-serving details.

## Citation

If you use these materials, please cite the accompanying working paper. See `CITATION.cff`.
