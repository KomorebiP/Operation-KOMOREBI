# Claim ledger

- **EXACT, elementary:** For any `1+b=c`, `c>rad(bc)` iff `rad(c)<=b/rad(b)`. For coprime prime `h` and `Q`, this becomes `rad(1+hQ)<=Q/rad(Q)`.
- **EXACT, elementary:** For primitive `a+b=c`, `c>rad(abc)^(1+delta)` iff `U(a)U(b)U(c)>ab*c^(delta/(1+delta))`.
- **THEOREM from classical PNT:** For `U(b)<=theta log X`, the number of `1+b` ABC hits up to `X` is at most `X^(theta+o(1))`. The uniform `Q<=H^A` prime-multiplier version follows.
- **THEOREM using classical Brun–Titchmarsh:** Uniform bounded prime-multiplier moments when `sigma<eta/(2-eta)`, improving the previous conservative threshold `eta/[2(2-eta)]`.
- **THEOREM using Brun–Titchmarsh and Siegel–Walfisz:** Uniform Euler-product moment asymptotic for the same sigma range, and uniform squarefree-density law in the same `Q` range.
- **THEOREM, elementary:** `O_epsilon(X^(1+epsilon))` ordinary ABC hits, and `O_delta,epsilon(X^(1-delta/(2*(1+delta))+epsilon))` for stronger high-quality hits. The latter is generally weaker than known 2026 results; historical priority is not claimed.
- **TESTS:** 10,000 exact integer divisor-expansion checks; 51,320 exact prime-multiplier classification checks; all unordered primitive triples with `c<=10,000`; analytic moment comparisons for six `Q` values.
- **NOT PROVED:** Full ABC conjecture; pointwise estimates for every chosen prime multiplier; new historical priority; Lean verification.
