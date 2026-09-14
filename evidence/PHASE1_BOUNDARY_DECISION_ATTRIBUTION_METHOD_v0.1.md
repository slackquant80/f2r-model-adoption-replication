# Phase 1 Boundary-Decision Attribution Method v0.1

Status: **PASS_EXACT_RECONCILIATION**

Purpose: post-hoc mechanism diagnostic for the F2R model-adoption Investment Research paper.

This diagnostic does not re-run or alter any forecasting model. It uses the frozen Phase 1 target/rank panel and the same canonical 11-asset market-binding data, execution schedule, drift accounting, and bilateral 10 bp-per-side cost convention used by the Phase 1 portfolio simulator.

## Exact decomposition

The hybrid-versus-incumbent terminal wealth gap is decomposed in additive log-wealth terms.

- Each daily gross-return log difference is assigned to the signal-month target that was active during that close-to-close interval.
- Each transaction-cost log difference at an execution close is assigned to the incoming signal-month decision that generated the rebalance.
- The components sum exactly to the full hybrid-versus-incumbent log terminal-wealth difference over the Phase 1 reported performance window.

Reconciliation:
- monthly relative log-wealth gap: `0.176402820965`
- attributed relative log-wealth gap: `0.176402820965`
- absolute error: `2.16493489802e-15`
- terminal hybrid/incumbent wealth ratio: `1.192918`

## Mechanism findings

- Top-4 selections differ in `58` of `112` decision months (51.8%).
- Changed-selection months account for `99.4%` of the net relative log-wealth gap.
- Unchanged-selection months have zero gross-return contribution; their residual comes only from path-dependent transaction-cost differences.
- Among changed-selection months, `36` contribute positively and `22` negatively.
- The single largest favorable changed decision is `10.7%` of total positive changed-decision contribution.
- The top five favorable changed decisions are `35.2%` of total positive changed-decision contribution.

## Claim boundary

This is a **post-hoc mechanism diagnostic**, not a pre-specified confirmatory test and not independent out-of-sample evidence. It can clarify how the observed portfolio difference was transmitted through decisions; it cannot eliminate model-selection risk or convert the retrospective technology counterfactual into historical live evidence.
