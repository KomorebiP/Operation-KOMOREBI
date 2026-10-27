# v0.7 verification

## Test suite
- `test_streaming_skat.py`: PASS
- `test_approximate_lightcone.py`: PASS
- `test_budget_scheduler.py`: PASS
- `test_spectral_tail_bridge.py`: PASS

## Direct pruning -> spectrum -> tail
- all spectral intervals contain the true eigenvalues: True
- all direct tail brackets contain the true K-COS probability: True

## Dual-budget scheduler
- all tested schedules respect their certified tail bracket: True
- at operator budget 0.005, omitted phase pairs: 23
- corresponding 1e-8 bracket width: 0.221071 decades

## Certify-after-prune range core
- every interval contains the true probability: True
- first depth with nontrivial exact-scale bracket: 9
- residual at that depth: 1.234e-15

## Claim boundary
The direct spectral/tail bridge is proved for positive Gaussian quadratic-form
coefficients using Weyl and common-Z stochastic ordering.  The dual-budget
scheduler is certified but not globally optimized.  The range-core experiment
demonstrates a limitation: a valid spectral interval may be too conservative
for deep-tail use until the range residual is small.
