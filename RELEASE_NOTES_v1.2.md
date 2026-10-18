# F2R public replication v1.2 — paper v0.16

- Accompanies the **10-page revision** of *A Second Opinion for the Portfolio* (existing SSRN Abstract ID 7460378).
- Adds **Figure 6**, a monthly-sampled cumulative net-wealth comparison drawn exclusively from existing frozen monthly net returns (112 observations, May 2017 through partial August 2026, ending August 3).
- Compares incumbent four-model ensemble (3.6217583x), selected C3 hybrid (4.3204625x) and separate higher-Chronos-weight C2 challenger (4.4954794x). These are terminal normalized wealth ratios, **not** prospective investment forecasts.
- Adds a public standalone Figure 6 generator, numeric JSON anchors, and validation to the existing `python reproduce.py` sequence.
- Preserves the original scientific evidence, Figures 1–5, existing accounting, returns, and historical v1.1 release via versioned Git tag/manifest.
- **Do not infer daily Sharpe or daily maximum drawdown from the monthly graph.** The paper's volatility, Sharpe, and maximum drawdown derive from 2,327 actual daily portfolio return observations, unchanged by this release.
- The Chronos-2 reconstruction is a **retrospective technology counterfactual**, not historical live out-of-sample deployment; pretraining temporal coverage is not audited.
- No raw licensed data, model weights, runtime secrets, production operation or live F2R configuration is included.

Existing GitHub Release and Zenodo archival records should be checked **after** tag publishing; do not presume a new Zenodo version DOI until actual ingestion is verified.
