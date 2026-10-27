# Independent mathematical review: exact dyadic periods

Verdict: proved as written. The source was independently read and the subsequent combined Lean gate passed.

For j<4, n>=0, T>0, let U_j(n)=j!*C_(4,j)(n) and d=(1,1,5,3). The difference U_j(n+T)-U_j(n) is nonzero and has exact valuation v2(T)+d_j. Every positive uniform packet period modulo2^r is exactly a positive multiple of2^max(0,r-d_j). The natural-number r=0 endpoint is also covered correctly.

| Obligation | Finding |
|---|---|
| Actual sequence and normalization | Passed: triangular recurrence, original factorial convention, original EGF bridge |
| Finite prefix | Passed: actual coefficient and Mahler identities proved in Lean; no assumed numerical table |
| Infinite tail | Passed: existing all-row bound and uniform logarithmic induction |
| Newton dominance | Passed: translated coefficient bounds, binomial denominator identity, strict leading valuation |
| Zero conventions | Passed: positive shift required, nonzero proved, higher coefficients zero-safe |
| Boundaries | Passed: row0, shift1, and precisions r<=d_j |
| Period definition | Passed: every row and arbitrary positive shifts, not just powers of two |
| Minimality | Passed: genuine IsLeast and divisibility classification |
| Degree convention | Passed: degree shift4T for packet shiftT |
| Combined audit | Passed:16modules,192declarations,9intended invalid proofs,2statement contracts |

The generic module, exact prefix, capstone, original definitions, and completed logs were inspected directly. Only propext, Classical.choice, Quot.sound occur in the combined axiom report. Earlier failed development checks were compiler/script issues and were corrected before this final gate. No further external theorem dependency was introduced.

Higher-order exact valuations, other parameter families, native unrestricted obstruction/gluing conjectures, and a continuous isometry formalization are outside this block. This review is independent agent review, not human peer review or a second proof-kernel implementation.
