from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path('/mnt/data')
TABLE = ROOT / 'abc_sparse_prony' / 'sparse_prony_channels.csv'
RESULTS = ROOT / 'abc_sparse_prony' / 'sparse_prony_results.json'


def main() -> None:
    frame = pd.read_csv(TABLE)
    assert len(frame) == 16
    assert (frame.nontrivial_fourier_energy + 1e-7 >= frame.sparsity_energy_lower_bound).all()
    assert (frame.krylov_rank_numeric + 2 >= frame.krylov_rank_exact).all()
    tested = frame[frame.prony_tested == True]
    assert len(tested) == 9
    assert tested.prony_recurrence_residual.max() < 1e-8
    balanced = frame[frame.galois_balance_tested == True]
    assert len(balanced) == 11
    assert balanced.target_log_discriminant_best_galois.min() > -1e-8

    record = frame[frame.label == 'Reyssat: 3^9 in b'].iloc[0]
    assert record.assignment_count == record.occupied_residues == 9
    assert abs(record.nontrivial_fourier_energy - 1457.0) < 1e-8
    assert record.target_log_discriminant_original < -11
    assert record.target_log_discriminant_best_galois > 3

    synthetic8 = frame[frame.label == 'synthetic 3^9 support 8'].iloc[0]
    synthetic10 = frame[frame.label == 'synthetic 3^9 support 10'].iloc[0]
    assert synthetic8.assignment_count < synthetic8.group_order
    assert synthetic10.assignment_count > synthetic10.group_order

    results = json.loads(RESULTS.read_text())
    assert results['channels'] == 16
    print('PASS sparse energy barrier')
    print('PASS exact Krylov rank checks')
    print('PASS Prony recurrence checks')
    print('PASS Galois balancing checks')
    print('PASS record and entropy-transition checks')
    print('5 verification groups passed')


if __name__ == '__main__':
    main()
