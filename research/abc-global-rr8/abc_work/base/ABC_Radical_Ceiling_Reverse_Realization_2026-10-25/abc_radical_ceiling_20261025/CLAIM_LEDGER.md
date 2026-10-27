# Claim ledger

| Result | Mathematical status | Basis | Main limitation |
|---|---|---|---|
| Exact two-sided radical ceiling (Equation 1) | Proved | Coprimality and algebra | Equivalent to `c>R` |
| Input-concentration barrier (Equations 1a–1c) | Proved | Rearrangement of the radical inequality | Necessary condition only, no high-concentration bound |
| High-quality prime-multiplier threshold (Equation 1d) | Proved | Rearrangement of the exact height condition | Necessary condition, not new global height estimate |
| Infinite ordinary hits of `1+(2^(6t)-1)=2^(6t)` | Proved | Divisibility by 9 | Ordinary hits are not necessarily fixed-epsilon exceptions |
| Fixed-offset ceiling (Equation 2) | Proved | Integer rounding | Needs prime multiplier, coprimality and size condition |
| Bounded-radical count (Equation 4) | Proved | Radical-support enumeration | Counting, not height |
| Subpower exceptional count (Equation 5 and Corollary) | Proved | Stirling plus output ceiling | Requires `U(Q)=H^{o(1)}` |
| Complete `Q=4,8,9,16` classification | Proved | Congruence and factorization | Prime multipliers only |
| `Q=243,H<=10^9` enumeration | Finite exact check | `verify.py`, integer arithmetic | No extension past bound |
| General ABC conjecture | Open | No proof claimed | Exceptional high-concentration inputs remain |

External input: factorial lower bound/Stirling estimate only for asymptotics; no advanced or unverified theorems needed.
