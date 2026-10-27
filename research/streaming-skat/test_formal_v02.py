from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent

part = pd.read_csv(HERE/'partition_invariance.csv')
hier = pd.read_csv(HERE/'hierarchical_refinement.csv')
lc = pd.read_csv(HERE/'polyphase_psd_light_cone.csv')
rank = pd.read_csv(HERE/'phase_local_rank_audit.csv')
qr = pd.read_csv(HERE/'qr_core_update_audit.csv')
mem = pd.read_csv(HERE/'memory_asymptotic_sweep.csv')

assert part['gram_rel_error'].max() < 1e-12
assert part['action_rel_error'].max() < 1e-12
assert hier['coarse_vs_fine_rel_error'].iloc[0] < 1e-12
assert lc.loc[lc['outside_light_cone'], 'norm'].max() == 0.0
assert (rank['constructed_rank'] == rank['svd_numerical_rank']).all()
assert qr['relative_l2_singular_difference'].iloc[0] < 1e-12
assert mem['stream_kernel_action_MiB'].max() == mem['stream_kernel_action_MiB'].min()
assert mem['full_factor_MiB'].iloc[-1] > 90 * mem['full_factor_MiB'].iloc[0]
print('PASS: v0.2 formal regression invariants')
