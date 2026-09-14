# Tie-breaking and integration specification

The frozen target/rank panel already contains the resolved rank order and Top-4 selection for each variant. The research implementation used the following deterministic conventions.

## Fixed asset order used only as the final deterministic tie-break

`SPY, QQQ, IWM, EFA, EEM, VNQ, DBC, IEF, TLT, EWY, GLD`

## Conventional rank ensemble

For each signal date and asset, model rank points are averaged across the included conventional models. Assets are ordered by:

1. average rank score, descending;
2. average model z-score, descending;
3. fixed asset order above.

## Weighted rank hybrid

For the three-model + Chronos configurations, the primary rank score is computed using exact integer weights corresponding to the stated Chronos model-combination contribution. Assets are ordered by:

1. exact weighted rank score, descending;
2. weighted z-score, descending;
3. fixed asset order.

## Standardized-forecast hybrid

The three conventional models are averaged in cross-sectional standardized-score space and combined 80/20 with the standardized Chronos score. Assets are ordered by:

1. combined standardized score, descending;
2. fixed asset order.

## Single-model variants

Assets are ordered by model prediction, descending, with the fixed asset order as the deterministic final tie-break.

The Top-4 are the first four assets under the relevant ordering and each receives a 25% target portfolio weight.
