# Independent characteristic-function inversion audit — v1.7

Date: 2026-09-24

## Question

Does the positive-tail solver remain accurate around p ~ 1e-16 on heterogeneous spectra when compared with an independent direct inversion of the original characteristic function?

## Reference calculation

For Q = sum_j lambda_j chi^2_{h_j}, central and positive, the direct inversion used

P(Q >= q) = 1/2 + (1/pi) int_0^infinity sin(theta(u)) / (u rho(u)) du,

with

theta(u) = 1/2 sum_j h_j atan(lambda_j u) - q u / 2,

rho(u) = product_j (1 + lambda_j^2 u^2)^(h_j/4).

This computation does not use exponential tilting, COS inversion, packet compression, or the K-COS error controller.

## Omitted-integral bound

Since

rho(u) >= u^(r/2) product_j lambda_j^(h_j/2),

where r = sum h_j, the omitted reference integral obeys

|R_U| <= C/(pi p) U^(-p),

p = r/2,
C = product_j lambda_j^(-h_j/2).

Each case was evaluated at two increasing truncation limits. The final truncation bound and the observed convergence between the two integrals are both recorded.

## Cases

1. balanced rank 80: weights 0.04, 0.06, 0.09, 0.12, 0.16, each multiplicity 16.
2. skewed rank 80: weights 0.02, 0.035, 0.07, 0.16, 0.40 with multiplicities 20,20,16,16,8.
3. spiky rank 80: weights 0.015, 0.025, 0.05, 0.10, 0.25, 0.80 with multiplicities 24,18,14,10,8,6.
4. balanced rank 120: the first five weights with multiplicity 24 each.

Thresholds were selected near log10 p = -16 using the production solver. The independent inversion then evaluated the probability at that fixed threshold.

## Results

The absolute differences in log10 probability were:

- balanced rank 80: 6.52e-15 decades;
- skewed rank 80: 4.13e-15 decades;
- spiky rank 80: 5.19e-15 decades;
- balanced rank 120: 2.88e-15 decades.

The implied relative probability differences range from 6.64e-15 to 1.50e-14.

The final omitted-integral bounds relative to p range from 4.19e-29 to 7.00e-17. Convergence between the two reference truncations is smaller than the K-COS/reference discrepancy in every case.

## Interpretation

This is independent numerical validation, not a proof that the K-COS point estimate is exact. The rigorous positive exact-spectrum guarantee remains the directed-rounding enclosure of v1.4/v1.5. The inversion battery provides orthogonal evidence that ordinary high-speed evaluation remains accurate around the practically important 1e-16 regime on heterogeneous spectra.
