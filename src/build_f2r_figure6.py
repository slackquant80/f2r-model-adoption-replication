"""Public F2R figure 6: monthly-sampled cumulative net wealth from frozen CSV.

No model inference, daily return interpolation, or daily-risk recomputation.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SERIES = [
    ('CURRENT4_RANK', 'Incumbent four-model'),
    ('C3_REX3_CHRONOS20', 'Selected hybrid (C3)'),
    ('C2_CURRENT4_CHRONOS50', '50% Chronos challenger (C2)'),
]
EXPECTED = {
    'CURRENT4_RANK': 3.6217583326610043,
    'C3_REX3_CHRONOS20': 4.3204624974884,
    'C2_CURRENT4_CHRONOS50': 4.495479414208333,
}

def run(data_path: Path, output_dir: Path) -> None:
    with data_path.open(newline='', encoding='utf-8-sig') as f:
        grouped = defaultdict(list)
        for row in csv.DictReader(f):
            grouped[row['variant']].append(row)
    paths = {}
    for key, _ in SERIES:
        src = sorted(grouped[key], key=lambda r: r['month'])
        if len(src) != 112 or src[0]['month'] != '2017-05' or src[-1]['month'] != '2026-08':
            raise RuntimeError(f'Expected monthly evidence window mismatch: {key}')
        months = [x['month'] for x in src]
        if len(months) != len(set(months)):
            raise RuntimeError(f'Duplicate monthly evidence: {key}')
        monthly = np.asarray([float(x['net_return']) for x in src], dtype=float)
        if not np.isfinite(monthly).all() or (monthly <= -1).any():
            raise RuntimeError(f'Invalid monthly net returns: {key}')
        wealth = np.cumprod(1 + monthly)
        if not np.isclose(wealth[-1], EXPECTED[key], atol=1e-9, rtol=0):
            raise RuntimeError(f'F2R frozen end-wealth mismatch: {key}')
        paths[key] = wealth

    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 3.06), dpi=160)
    fig.subplots_adjust(left=.092, right=.985, top=.89, bottom=.27)
    for key, name in SERIES:
        wealth = paths[key]
        ax.plot(np.arange(1, 113), wealth, lw=1.7, label=f'{name} (final {wealth[-1]:.2f}x)')
    ax.set_title('Portfolio net wealth, observed at monthly reporting intervals', loc='left', fontsize=10)
    ax.set_ylabel('Cumulative net wealth (start = 1.00)', fontsize=9)
    ax.set_xlabel('Monthly reporting period', fontsize=9)
    ax.set_xlim(1, 112)
    ax.set_ylim(.8, 5.4)
    ax.set_xticks([1, 21, 45, 69, 93, 112], ['May 2017', '2019', '2021', '2023', '2025', 'Aug 2026*'])
    ax.tick_params(axis='both', labelsize=7.6)
    ax.grid(axis='y', alpha=.24)
    ax.legend(loc='upper left', fontsize=7.5, frameon=False)
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(.092, .075, '* August 2026 is a partial month ending August 3. From frozen monthly net returns;', fontsize=7.2)
    fig.text(.092, .042, '  not a daily-performance curve or a real-time Chronos-2 deployment record.', fontsize=7.2)
    fig.savefig(output_dir / 'Figure_6_reproduced.pdf')
    fig.savefig(output_dir / 'Figure_6_reproduced.png', dpi=160)
    plt.close(fig)
    m = {'status': 'PASS', 'source': 'PHASE1_MONTHLY_RETURNS_v1.0.csv', 'reporting_frequency': 'monthly',
         'monthly_observations': 112, 'first_reporting_period': '2017-05',
         'last_reporting_period': '2026-08', 'last_month_partial_through': '2026-08-03',
         'terminal_net_wealth': {k: float(v[-1]) for k, v in paths.items()},
         'daily_performance_or_drawdown_reconstructed': False}
    (output_dir / 'FIGURE_6_METRICS.json').write_text(json.dumps(m, indent=2) + '\n', encoding='utf-8')
    print('PASS - F2R Figure 6 frozen monthly wealth reproduced.')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output-dir', required=True, type=Path)
    p.add_argument('--data-path', required=True, type=Path)
    args = p.parse_args()
    run(args.data_path, args.output_dir)
