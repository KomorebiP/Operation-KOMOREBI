# Narrow OEIS formula support

All source leaves below were read from the same pinned official OEIS export as the metadata records. Each full-entry SHA-256 matches the earlier authenticated hash. This supplement verifies exact statements, indexing and normalization. It does not convert a formula stated in OEIS into an independently audited universal proof.

- Commit: `2ce625d68f85e35e26e15c0d9681f69280c095e7`.
- Export time: `2026-10-07T03:00:24-04:00`.
- Checked: `2026-10-07T22:36:49.825709+00:00`.
- Reads: **7/7**, no access failures or source mismatches.
- License: OEIS Foundation, CC BY-SA 4.0.

## Formula leaves

| Entry | Exact project formula | Range and normalization | Pinned source leaf | Status |
|---|---|---|---|---|
| A005259 | (n+1)^3 A(n+1) = (34n^3+51n^2+27n+5) A(n) − n^3 A(n−1), n≥1; A(0)=1, A(1)=5. | A(n)=Σ_{k=0}^n binom(n,k)^2 binom(n+k,k)^2 (the ζ(3) Apéry sequence). Coefficients, index and seeds match exactly. Recurrence n≥1; defining binomial sum n≥0. | [Formula field, line 70](https://github.com/oeis/oeisdata/blob/2ce625d68f85e35e26e15c0d9681f69280c095e7/seq/A005/A005259.seq#L70) | Stated, no proof audited here. |
| A000110 | Σ_{n≥0} B(n) z^n/n! = exp(exp(z)−1). | B(n) is the Bell number; B(0)=1. This is an exponential generating function, not an ordinary coefficient stream. n≥0, formal power series over Q. | [Formula field, line 402](https://github.com/oeis/oeisdata/blob/2ce625d68f85e35e26e15c0d9681f69280c095e7/seq/A000/A000110.seq#L402) | Stated, no proof audited here. |
| A000670 | Σ_{n≥0} F(n) z^n/n! = 1/(2−exp(z)). | F(n) counts ordered set partitions (Fubini numbers); F(0)=1. This is an exponential generating function. n≥0, formal power series over Q. | [Formula field, line 217](https://github.com/oeis/oeisdata/blob/2ce625d68f85e35e26e15c0d9681f69280c095e7/seq/A000/A000670.seq#L217) | Stated, no proof audited here. |
| A000111 | Σ_{n≥0} U(n) z^n/n! = sec(z)+tan(z). | U(n)=OEIS A000111(n), beginning 1,1,1,2,5,16,… . Preserve n! weights when splitting the ordinary numeric stream U(n). n≥0, formal power series over Q. | [Formula field, line 173](https://github.com/oeis/oeisdata/blob/2ce625d68f85e35e26e15c0d9681f69280c095e7/seq/A000/A000111.seq#L173) | Stated, no proof audited here. |
| A000364 | sec(z)=Σ_{k≥0} S(k) z^(2k)/(2k)!; S(k)=U(2k). | S(k)=OEIS A000364(k), nonnegative secant numbers. These are the even-index derivatives of sec, not coefficients weighted by k!. k≥0, formal power series over Q. | [Formula field, line 98](https://github.com/oeis/oeisdata/blob/2ce625d68f85e35e26e15c0d9681f69280c095e7/seq/A000/A000364.seq#L98) | Stated, no proof audited here. |
| A000182 | tan(z)=Σ_{k≥0} A000182(k+1) z^(2k+1)/(2k+1)!; A000182(k+1)=U(2k+1). | A000182 has OEIS offset 1. A zero-based tangent stream T(k)=A000182(k+1) uses odd factorial weights (2k+1)!. k≥0, equivalently OEIS n≥1, formal power series over Q. | [Formula field, line 106](https://github.com/oeis/oeisdata/blob/2ce625d68f85e35e26e15c0d9681f69280c095e7/seq/A000/A000182.seq#L106) | Stated, no proof audited here. |
| A000041 | Σ_{n≥0} p(n) z^n = ∏_{j≥1}(1−z^j)^(−1). | p(0)=1. This is an ordinary generating function. Its formal degree-N prefix depends only on factors j≤N. n≥0, formal power series over Z. | [Formula field, line 233](https://github.com/oeis/oeisdata/blob/2ce625d68f85e35e26e15c0d9681f69280c095e7/seq/A000/A000041.seq#L233) | Stated, no proof audited here. |

## Apéry recurrence contract

The A005259 formula field states the requested polynomial recurrence with exactly the coefficients 34, 51, 27 and 5, valid for n≥1. Its name field gives the squared-binomial definition, and its term field gives A(0)=1 and A(1)=5. These three source leaves are recorded together. Checking the binomial sum against the recurrence for a finite range supports a computation report, but is not a proof for every n.

## Euler channel indexing

Write U(n)=A000111(n). The source EGFs give S(k)=A000364(k)=U(2k) and T(k)=A000182(k+1)=U(2k+1). The tangent shift by one is required by its OEIS offset 1. The subsequence equalities follow by coefficient uniqueness: sec is even, tan is odd, and their sum is the full up/down EGF. Factorial denominators remain (2k)! and (2k+1)!, respectively. They do not become k! under numeric-stream channel splitting.

## Scope and attribution

Bell, Fubini and Euler formulas are known source statements, with no novelty claim. They are interpreted as formal series, so no analytic convergence claim is needed for the coefficient lessons. The author confirmed that the partition lesson uses the ordinary product generating function; its source leaf is included. Euler’s pentagonal recurrence is not displayed and is not a dependency.

`OEIS_FORMULA_SUPPORT.json` contains exact compact source-field excerpts, line locators, revision headers, full-source hashes, the notation dictionary and the source/proof boundary. Full entry texts used for verification remain temporary and are not included in the deliverable.
