# Independent audit of the finite-tap route

**Normalized claim.** For coprime integers `A>B>=1`, positive integers `n,d`, and any integer polynomial `T(z)=sum_(j=0)^r t_j z^j`, forward-shift taps act on `s_n=A^n+B^n` by evaluation at the two modes. All integer finite stride-`d` outputs at fixed `n` generate precisely `gcd(s_n,A^d-B^d) Z`. At an odd output prime with even birth order `d`, the two-tap gcd retains exactly the birth valuation. Full primitive stride `d=2n` has minimum positive output `s_n`, while half-order shifts have gcd `1` or `2`. Repeated differences multiply valuation and log height by the same factor. Contact preservation for general taps is equivalent to divisibility of `T(A)-T(B)`, with the exact nonzero-difference minimum stated in Section 6.

**Primary verdict: proved as written.** This verdict covers the elementary finite-tap statements in the frozen `PROOF_NOTE.md`, under the positive-integer stride/index convention above. No mathematical flaw was found. It does not promote the open continuation into an ABC result or assert an optimized degree/norm tradeoff for constrained taps.

The audit used the `mathbox:proof-audit` skill and its general-logic, computation, and source obligations. It is an independent review in a separate agent session, with a fresh derivation and no imported author functions in the supplemental checks. It is not a formal proof check; agents can still share model errors.

## Exact revision and scope

The route owner `/root/quadratic_route` supplied the frozen paths and hashes before this report. All three hashes were independently recomputed and matched:

| Source relative to `abc_work/polyphase_taps/routes/taps/` | SHA-256 |
| --- | --- |
| `PROOF_NOTE.md` | `7470bf6cdbb75d2f91e4db8f51f35024ae9a1ce9636aff8212e325c6b3586100` |
| `verify.py` | `414060a4e9e7ca1cc5b0b00fc68d3b43aa1c36349dc7c42fe56404d0a9c6852f` |
| `verification.json` | `7a02c62b90cb31cb0e55d6380de23316c1d298086ea0dd1d2208c3c9f77ee524` |
| `ROUTE.json` | `845443495cce48b566bcba178e28abed631168dafffb203eef42cfac8337f1bc` |

The route records base checkpoint RR3 and archive hash `557eeb61fcd37c984884b7123e7b599b403200244786f6fb549279d6b4b05302`. This review did not re-audit that whole checkpoint or prove any claim merely from its archive label. The only inherited proof needed here is the elementary odd-prime lifting identity, checked in `abc_work/routes/global/PROOF_NOTE.md`, Theorem 1, SHA-256 `f4b1c1eb8d4e52ee43634b454ea5fa3e12e88488dc148d76ea68e79a58e29bfc`.

There is no `.mathbox` directory in the inspected `abc_work` tree. The route evidence label is “Elementary proof and exact finite consistency checks.” No source proof or author output was changed; the author script was rerun only on review-local copies.

## Claim card and dependencies

- Coefficient domain: `Z`; finite polynomials only. No infinite-tap completion or coefficient-size restriction is assumed in the ideal/minimum statements.
- Source: the sequence indexed by positive integers. `E` is forward shift; `E^d` advances the index by `d`.
- Target: an integer at a fixed base index and stride. A zero output is allowed, but every size-divisibility use explicitly excludes it.
- Physical convention: positive integer decimation `N`, `y[m]=sum_k h[k]s_(Nm-k)`, and base index `n=Nm-rd>=1`.
- Prime hypotheses: `p` is odd and `p` does not divide `AB`; birth-order claims use `d=ord_p(A/B)`, even, and `s=v_p(A^d-B^d)`. The valuation formula uses `p|s_n`.
- General preservation: the listed distinct prime powers `p^(s_p)` each divide `s_n`. The sharper minimum `P(A-B)` uses odd even-order birth primes, hence `gcd(P,A-B)=1`. It would not hold for an arbitrary `P` lacking this coprimality; the proof supplies it in the stated birth setting.
- Rational normalization: valuations are valuations in `Q`, and the integer numerator is reconstructed before applying integer divisibility.

The dependency graph has the following leaves and implications:

1. Definition of `s_n` and integer polynomial evaluation (internal definitions) imply the two-mode tap formula and physical reversal formula.
2. Coprimality of `A,B` (hypothesis) implies `gcd(s_n,A)=1`; subtraction gives the two-term gcd; integer Euclid (elementary internal tool) gives a positive nonzero auxiliary.
3. The two-mode recurrence (direct expansion) makes every later strided value a combination of the first two; Bezout gives the reverse ideal inclusion.
4. Even multiplicative order and odd-prime lifting (the local RR2 proof identified above) give the birth valuation and its exact retention in the gcd.
5. Order at a half step and parity (elementary congruences) give the half-step gcd and difference-phase transport.
6. A mode eigenvalue computation gives repeated differences, their norm, and their exact valuation. Integer size then gives the height inequality.
7. The initial contact congruence gives the preservation criterion. Polynomial division and `A-B` divisibility give its equal-value kernel and nonzero minimum.
8. The definition of rational valuation gives normalization loss.

No universal assertion depends on the finite tests. They are consistency checks, not exhaustive proofs over unbounded parameters. No circular dependency was found.

## Obligation matrix and decisive derivations

| Obligation | Status | Check |
| --- | --- | --- |
| Forward versus physical shift | passed | With `h[(r-j)d]=t_j`, `Nm-(r-j)d=(Nm-rd)+jd=n+jd`. The reversal has no amplitude factor. Arbitrary `N` changes selected indices only. |
| Integer tap action | passed | Applying `E^d` to the two modes multiplies them by `A^d` and `B^d`; linearity gives `A^nT(A^d)+B^nT(B^d)`. |
| Constructive nonzero two-tap auxiliary | passed | `s_(n+d)-B^d s_n=A^n(A^d-B^d)` and `gcd(s_n,A)=1`; therefore `gcd(s_n,s_(n+d))=gcd(s_n,A^d-B^d)`. Bezout produces the positive gcd and standard coefficient bounds. |
| Exact whole finite-tap ideal | passed | The order-two recurrence has integer coefficients, so the first two values generate every future value. Their gcd is in the finite-tap image by Bezout. Both ideal inclusions hold. |
| Primitive full stride | passed | For `d=2n`, `A^(2n)-B^(2n)=(A^n-B^n)s_n`, so the gcd is `s_n`; zero or absolute value at least `s_n` is exact. |
| Birth valuation in the gcd | passed | Put `h=d/2`, `n=hk`, `k` odd. Since `d|p-1`, `p` divides neither `h` nor `d`. Lifting gives valuations `s+v_p(n)` and `s+v_p(n+d)`. They cannot both exceed `s`, because that would make `p|d`. Their minimum is `s`. |
| Half-step gcd | passed | An odd common prime would make `x^k=x^(k+1)=-1`, hence `x=1` and `1=-1`. For odd bases the even-power output is `2 mod 8`, while the other output is even; gcd is exactly `2`. Opposite parity gives odd outputs and gcd `1`. |
| Half-step phase transport | passed | Direct cancellation gives `a_(n+h)+B^h s_n=A^n(A^h+B^h)`. This uses the difference phase, as explicitly stated. |
| Repeated differences | passed | The `B` mode vanishes after the first factor of `E^d-B^d`; the `A` mode acquires `(A^d-B^d)^r`. Binomial coefficients have norm `(1+B^d)^r`. Since `p` does not divide `A`, valuation is exactly `rs`. |
| Divisibility/height comparison | passed | After exact division by `A^n`, the positive integer is `Delta_d^r`; `p^(rs)|Delta_d^r` gives `rs log p<=r log Delta_d<rd log A`. The factor `r` cancels. |
| General contact criterion | passed | From `A^n=-B^n mod p^s`, output is `B^n(T(B)-T(A)) mod p^s`. Invertibility of `B` proves the stated “if and only if.” |
| Nonzero difference bound and minimum | passed | Triangle inequality gives the upper bound. Every difference is divisible by `A-B`; coprimality with `P` forces a nonzero preserving difference to be a multiple of `P(A-B)`. `T(z)=Pz` attains it. |
| Equal-value kernel | passed | If both values equal `C`, monic division first by `z-A`, then by `z-B`, yields `T=C+(z-A)(z-B)Q` over `Z`. The output is `Cs_n`; a nonzero integer `C` cannot lower its absolute height. |
| Rational denominators | passed | `v_p(Y/D)=v_p(Y)-v_p(D)` even before reducing the fraction. Decimation itself contributes no denominator. |
| Uniform low-cost preserving tap | not addressed | Section 8 explicitly leaves this construction open. The exact ideal and difference minimum do not supply it. |
| Unrestricted ABC | out of scope | The frozen note expressly makes no ABC proof claim. |

The normalized-sequence statement in Section 5 is also correct: applying `(E^d-1)^r` to `(A/B)^n+1` and multiplying by `B^(n+rd)` recovers `A^n(A^d-B^d)^r`. Denominator clearing pays exactly the stated cost.

The local RR2 lifting source has the required hypotheses and gives exactly `v_p(s_n)=s+v_p(n)`: even order implies an odd multiple of its half order, the half-order sum has valuation `s`, and `p` does not divide the order. No stronger external theorem was silently used.

## Source and computation checks

The author script is exact integer arithmetic plus `Fraction`; its enumerated ranges match the finite assertions it actually checks. It does not purport to enumerate all taps or bases. In particular:

- Base loop: coprime `2<=A<=8`, `1<=B<A`; `1<=n<=12`, `1<=d<=6`, and `1<=r<=4` for binomial taps.
- Half-step loop: `1<=h<=6` and `k` in `{1,3,5,7}`.
- Physical loop: three base pairs, `1<=N,d,r<=4`, with binomial taps and guaranteed positive sampled indices.
- Preservation loop: five selected inputs and all `625` degree-at-most-three coefficient vectors in `[-2,2]^4`. Four have `P=9`; one has `P=1`. These cases alone give no multi-prime or general-depth coverage.
- The explicit `p=1093` case tests repeated-difference valuation and rational normalization. The source does not explicitly verify `ord_1093(2)=364`, although that exact order is not needed for its direct numeric assertions there. The general birth-order theorem is established algebraically, not by this example.

Review-local reproduction command:

```text
python3 abc_work/polyphase_taps/reviews/taps_checks/source/verify.py
```

It completed successfully, and the resulting `source/verification.json` was byte-identical to the frozen author output, with SHA-256 `7a02c62b90cb31cb0e55d6380de23316c1d298086ea0dd1d2208c3c9f77ee524`.

Supplemental independent command:

```text
python3 abc_work/polyphase_taps/reviews/taps_checks/independent_check.py
```

It imports no author implementation. It completed using exact arithmetic with these check counts:

| Family | Cases |
| --- | ---: |
| Gcd ideal and recurrence, eight future values | 6,480 |
| Half-step gcd and phase transport | 2,880 |
| Birth valuations, including an exponent factor `p` | 1,068 |
| Repeated differences and denominator loss | 4,272 |
| Arbitrary physical taps | 3,888 |
| Arbitrary preserving taps | 3,750 |
| Explicit kernel and degree-zero boundary base points | 9 |

The independent ranges are `2<=A<=12`, all smaller positive coprime `B`, `1<=n<=18`, `1<=d<=8`; half-step `1<=h<=8`, odd `1<=k<=15`; odd primes through `43` with even order and multipliers `k in {1,3,p}`; difference orders `1<=r<=4`. Physical tests use all `[-1,1]^4` tap vectors at three base pairs and `1<=N,d<=4`. Preservation tests use all `[-2,2]^4` vectors at six deliberate examples, including `P=27`, `P=225=3^2*5^2`, and `P=1225=5^2*7^2`, supplementing the author's small contact list. Exact annihilators, constant-plus-annihilator taps, and degree-zero taps are explicitly checked.

| Review computation artifact | SHA-256 |
| --- | --- |
| `reviews/taps_checks/independent_check.py` | `80dc63b7ae7fb34130c9e9fb0cf02df9956b414e036d3eddb51ad40dd1c106dc` |
| `reviews/taps_checks/independent_results.json` | `a5334ab342d6e1d7e59b1a0671532c3c981ba6d6a5406bbe24a8878682bcfff4` |

## Remaining gap, safe statement, and next check

There is no missing implication in the audited finite-tap conclusions. The research objective remains open at exactly the point identified in Section 8: construct a nonzero preserving tap with uniform sublinear total degree/coefficient height, or a separately nonvanishing auxiliary outside this two-mode integer linear span. The present analysis does not supply either construction.

The strongest safe statement is the exact unrestricted integer-output floor together with the exact preserving-difference floor and the stated coefficient/degree upper bound. “Complete coefficient-height classification” in route metadata should be understood in that scope; no optimum norm at fixed degree/support is proved.

The cheapest useful next check for a proposed continuation is to compute both `T(A)-T(B)` and the reconstructed integer output, prove the relevant one nonzero, and give its actual coefficient/degree or denominator budget. A short modular vector or a small rational amplitude alone does not pass those obligations.

Review provenance: `/root/taps_review`, 2026-10-25, independent audit of the exact frozen revisions above. The author proof and outputs remain unchanged.
