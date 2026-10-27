# Exploratory relation-pressure phase sweep

This sweep was designed after the developmental pilot. It is mechanistic exploration, not confirmatory evidence.
Every condition uses identical architecture, initialization by seed, data stream by seed, optimization budget, and terminal objective; only the D4 relation-loss weight changes.

| Relation weight | D4 L12 | D4 L32 | D4 L64 | C8 L12 | Random L12 | Median spectral radius | Relation hidden residual | Median hidden norm L64 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.8408 | 0.5225 | 0.3994 | 0.6597 | 0.3198 | 1.9173 | 5.6360 | 8.66e+17 |
| 0.01 | 0.9004 | 0.6089 | 0.4312 | 0.7397 | 0.3579 | 1.6442 | 3.3479 | 1.16e+13 |
| 0.03 | 0.9429 | 0.6499 | 0.4575 | 0.8149 | 0.4038 | 1.4777 | 2.2476 | 1.76e+10 |
| 0.10 | 0.9912 | 0.7651 | 0.5215 | 0.9482 | 0.4756 | 1.3104 | 1.3345 | 1.33e+07 |
| 0.15 | 0.9990 | 0.8384 | 0.5679 | 0.9785 | 0.4883 | 1.2647 | 1.1046 | 1.52e+06 |
| 0.30 | 1.0000 | 0.9321 | 0.6782 | 0.9937 | 0.5044 | 1.2097 | 0.8254 | 1.03e+05 |
| 0.60 | 0.9995 | 0.9116 | 0.7241 | 0.9956 | 0.5034 | 1.2254 | 0.7626 | 1.38e+05 |

## Initial interpretation

The best tested D4 depth-64 condition used relation weight `0.60` and reached `0.7241` mean accuracy across two seeds.
The sweep tests whether relation consistency acts as a dynamical-stability regularizer. It does not establish that the hidden matrices form an exact group representation, because ambient and hidden-return residuals remain nonzero.
