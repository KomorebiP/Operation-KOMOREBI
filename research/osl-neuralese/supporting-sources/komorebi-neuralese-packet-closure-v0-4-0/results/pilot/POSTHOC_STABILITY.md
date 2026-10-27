# Exploratory recurrent-stability audit

This analysis was designed after the developmental pilot and is not preregistered evidence.

## D4 depth extrapolation and latent magnitude

| Arm | L=8 accuracy | L=8 median norm | L=12 accuracy | L=12 median norm | L=32 accuracy | L=32 median norm | L=64 accuracy | L=64 median norm |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| linear_terminal | 0.9473 | 182 | 0.8413 | 2.12e+03 | 0.5034 | 7.05e+08 | 0.3762 | 5.32e+17 |
| linear_relation | 0.9998 | 9.3 | 0.9976 | 20.8 | 0.8269 | 1.39e+03 | 0.5708 | 1.41e+06 |
| gru_terminal | 0.4792 | 3.33 | 0.4211 | 3.34 | 0.3823 | 3.35 | 0.3645 | 3.36 |

## Learned linear-operator spectra

| Arm | Family | Median spectral radius | P95 spectral radius | Median operator norm |
|---|---|---:|---:|---:|
| linear_terminal | d4 | 1.9124 | 2.0333 | 2.2056 |
| linear_terminal | c8 | 1.7469 | 1.9189 | 2.1406 |
| linear_terminal | mixed_cycle | 1.8846 | 2.0280 | 2.1974 |
| linear_terminal | random | 1.7470 | 1.9964 | 2.0958 |
| linear_relation | d4 | 1.2643 | 1.3085 | 1.6810 |
| linear_relation | c8 | 1.2252 | 1.2623 | 1.6260 |
| linear_relation | mixed_cycle | 1.2544 | 1.3081 | 1.6748 |
| linear_relation | random | 1.2459 | 1.3715 | 1.5964 |

## Reading

The terminal-only linear model can decode accurately while its hidden magnitude grows rapidly. Relation pressure substantially contracts the learned dynamics toward a stable near-representation and extends usable recurrence. This identifies spectral and relation stability, rather than one-step correctness alone, as the next mechanistic control variable.
