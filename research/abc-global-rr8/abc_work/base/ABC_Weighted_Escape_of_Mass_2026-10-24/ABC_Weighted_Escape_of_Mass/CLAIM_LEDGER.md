# Claim classification

| Claim | Status | Dependencies |
| --- | --- | --- |
| Weighted multiplicative-order tail `O_q(Y^-1/2)` | Elementary proof in note | Group-by-order divisibility; Chebyshev bound |
| Moving-window full shell truncated bound `O_q(Y^-1/2+sqrt(X)/F)` | Elementary proof in note | Exact non-Wieferich lifting; weighted tail; Chebyshev bound |
| Fixed support and fixed output-prime packet `log M_P=O_{S,P}(loglog c)` | Conditional only on established external theorem, i.e. an unconditional corollary when Yu is imported | Yu p-adic logarithmic-form bound |
| Restricted ABC for fixed input support and fixed repeated output-prime support | Unconditional corollary using Yu | Fixed-prime valuation bound |
| Escape-of-weighted-mass necessary condition for high-quality fixed-S triples | Unconditional corollary using Yu | Exact c/R identity and fixed-prime bound |
| Pointwise bound `log M_{<=Y} <<_S Y^3 log(H+3)` and growing cutoff `p<=(log c)^(1/3-delta)` | Unconditional corollary of published Yu bound, with explicit auxiliary-field p-dependence traced in note | Yu / Alvarado et al. Section 3 |
| Restricted ABC for **growing** repeated output-prime support `p<=(log c)^(1/3-delta)` and fixed input support | Unconditional corollary using Yu | Pointwise budget / `log R=log c+log D-log M` |
| GCD collision identity | Elementary proved | Euclidean algorithm |
| Numerical partial sums, valuation scans, gcd samples | Tested finite examples | Pure Python exact modular arithmetic; real logs used only for sums |
| Uniform bound for growing exceptional/moving output primes | OPEN | Not proved |
| Full ABC conjecture | OPEN | Not proved |
| Lean formalization of this block | NOT RUN | No Lean compilation claimed |
