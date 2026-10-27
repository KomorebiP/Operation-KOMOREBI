# Bayesian selection comparison

The fixed 201-task parameter holdout contains 219 outputs.

| Selector | Exact outputs | Rate |
|---|---:|---:|
| Bayesian posterior, version 0.4.0 | **32/219** | **14.6119%** |
| Deterministic ranker, identical 0.4.0 portfolio | 32/219 | 14.6119% |
| Candidate-oracle union | 33/219 | 15.0685% |
| Historical Bayesian version 0.3.0 | 28/219 | 12.7854% |

The Bayesian and deterministic 0.4.0 selectors solve one different output each. Bayesian selection changes the chosen abstraction and supplies calibrated uncertainty, but it does not improve aggregate exact accuracy over the same candidate portfolio. The four-output holdout gain over 0.3.0 comes primarily from the expanded typed grammar.
