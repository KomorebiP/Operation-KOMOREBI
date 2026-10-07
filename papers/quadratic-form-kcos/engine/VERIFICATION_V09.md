# v0.9 verification

## Cumulative regression tests
- `test_streaming_skat.py`: PASS (6/6)
- `test_approximate_lightcone.py`: PASS (5/5)
- `test_budget_scheduler.py`: PASS (4/4)
- `test_spectral_tail_bridge.py`: PASS (5/5)
- `test_residual_trace_cap.py`: PASS (5/5)
- `test_residual_completion.py`: PASS (3/3)
- `test_realistic_skat.py`: PASS (3/3)

## Realistic simulation battery
- scenarios: 4
- maximum streamed-kernel relative error: 6.611e-16
- maximum phenotype-path relative discrepancy: 8.318e-16
- deepest tested log10 probability: -457.973916
- worst absolute deep-tail discrepancy: 3.209e-12 decades

## Historical correction
The historical copy-LD simulator used `np.empty` followed by `+=`.
v0.9 repairs this with zero initialization.  Previous copy-LD benchmark
numbers are not authoritative validation.

## Boundary
Gaussian SKAT-style quadratic forms under synthetic rare-variant LD models
are validated here.  External cohort replication, finite-sample logistic
calibration, and native-GPU performance remain separate.

## Numerical warning boundary
Deepest adaptive queries emitted overflow warnings in an intermediate rejected
certificate-growth calculation.  Accepted results had finite certificates and
matched the full-spectrum reference.  This is not a demonstrated accuracy
failure, but the internal bound arithmetic should be made log-domain in a
future hardening pass.
