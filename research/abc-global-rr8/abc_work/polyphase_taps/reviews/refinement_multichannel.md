# Independent audit: multichannel reconstruction and nested refinement

Normalized claim: integral invertible analysis/synthesis preserves the **minimum** coordinate valuation and retains any selected scalar functional; nested polyphase selection locates contact classes without removing their birth depth, while zero-phase blocking transports order and birth/lifting mass with the stated cyclotomic degree and norm costs. Compression realizes the same exceptional packet at a smaller exponent and does not supply a new bound for a top-order packet.

**Primary verdict: proved as written**, for the final revisions identified below. This verdict concerns the displayed local algebra, transport and restricted implications. Neither route proves unrestricted ABC, constructs its proposed auxiliary integer, or bounds a general high-order exceptional birth packet.

## 1. Claim cards and authoritative revisions

This is an independent subagent audit of the raw proofs, not an author self-review. I did not edit either proof or replace any author output. The refinement author made two scope clarifications after I requested them: the target exponent is explicitly positive, and the all-phase coprime-radix sentence explicitly concerns baseline depths `k<=s`. I then reread and audited the resulting frozen revision. These are recorded restrictions of scope, not a supplied new proof route.

| Artifact | Exact SHA-256 audited |
|---|---|
| `routes/multichannel/PROOF.md` | `0ebeff111a83d322f5849723c5dcb37363abfa949a8698b7ce1b104fc34955c5` |
| `routes/multichannel/verify.py` | `e1d3ab39ae181e5630f8b0b9d679e8d33d8f5238d08cc990954a397a56a04368` |
| `routes/multichannel/results.json` | `37dc383077506dc7ae9dfc3bb6cb12c0c37d6c64e739866fdba6c279f63f085b` |
| `routes/refinement/PROOF_NOTE.md` | `d90c55275bcb536c7b8899b0d478a4903c8c553af25edcd4ab11fe68c1fff669` |
| `routes/refinement/verify.py` | `f470ac1564598c5ffe332c59c42731d92a51d6726b30c3f8e55d9089ab63a5f4` |
| `routes/refinement/verification.json` | `d19f24c6a5a678deb904fd6ed5dc6949bfc3a524fc6855da63969361a79d9dd9` |
| `abc_work/roots_unity/routes/cyclotomic/ORDER_BUDGET.md` | `46679caa7dedefda2557b48f16e3de0f375b8e4e2b03651694a6001d8837f0ea` |

The earlier refinement revision reviewed before clarification was `ece763531500f78ac9bbaa4ba9f01d6c74dae9008e327f215396c2b8bad7f885`. Its substantive formulas are unchanged. The present verdict attaches only to the final hash in the table.

**Multichannel domain.** Nonzero finite vectors over `Q` with the usual `v_p`, or over a specified valued local field; square nonsingular integral matrices for the determinant estimate; nonsingular rational matrices for its rational variants. Rectangular analysis and synthesis have compatible dimensions and satisfy `ST=I`; integral preservation requires both stages to be integral at the specified prime. Laurent evaluation is at a nonzero `p`-adic unit. The strict paraunitary claim is over `Z[z,z^-1]`, with formal transpose and `z -> z^-1`, and identity normalization exactly as written. General complex coefficients do not have a specified `p`-adic valuation.

**Refinement domain.** Coprime integers `A>B>=1`, positive target exponent `n`, odd output prime `p`, `d=ord_p(A/B)`, `s=v_p(A^d-B^d)`, target valuation depth `k>=1`. Phase parameters have the ordinary signal meaning: positive integer radix `N`, tree depth `r>=0`, `M=N^r`, `0<=j<M`, and `t>=0`. Blocking uses a positive divisor `M|n`; the symbol `r` in the cyclotomic identity instead denotes a positive conductor. These are finite algebraic objects; no completion, analytic convergence, or probabilistic interpretation is used.

## 2. Dependency graph

1. Integer coefficients imply the valuation inequality for a linear combination; the integer adjugate supplies the reverse determinant bound. These give the minimum-content, rational-denominator and reconstruction statements.
2. The identity `F=ell S y` retains the selected scalar. Explicit matrices then exhibit movable cancellation, determinant concentration and adaptive denominator/synthesis costs.
3. The diagonal constant coefficient of formal integer paraunitarity is a sum of integer squares. This gives one signed monomial per row; off-diagonal orthogonality gives distinct occupied columns.
4. Primitivity implies `p` does not divide `AB`. Finite-field order gives even `d`, `p` not dividing `d`, and the plus-contact class. Elementary odd-prime lifting gives the full valuation and modulus `L_p(k)`. Linear congruence solving gives nested phase compatibility and child counts.
5. The order of a power and the same lifting identity give blocked `d'` and `s'`. Prime-by-prime exponent bookkeeping gives `W'G'=WG` and unchanged `B_2`.
6. Primitive complex root orders give the exact cyclotomic substitution identity over `Z[X,Y]`. Its disjoint factor fibers give integer divisibility and the degree comparison. Positivity at `A>B>=1` turns divisibility into the stated size comparison.
7. The allowed plus conductors have `v_2(d)=v_2(n)+1`. Their lcm defines `m|n` with odd quotient. This gives output divisibility, equality of exceptional birth packets and the compression degree bound.
8. The exact decomposition `U=B_2 W G`, together with an independently obtained size bound, gives the stated restricted ABC implications. The unresolved size bound is not supplied by any preceding arrow.

All algebraic leaves above were checked directly below. The RR3 notation and budget were read at the recorded revision; their needed decomposition also follows prime by prime here. No unverified literature theorem or finite experiment is needed for the local conclusions. No `.mathbox` ledger was found in this project tree.

## 3. Obligation matrix

| Obligation | Result | Decisive point |
|---|---|---|
| Minimum versus maximum coordinate depth | passed | Both directions use minimum valuation; a selected sum can remain deep while all coordinates are units. |
| Field versus integral reconstruction | passed | A field inverse can introduce denominator depth; two integral stages force equality of minimum content. |
| Selected scalar functional | passed | Its exact new row is `ell S`, with all cancellation and coefficient valuations retained. |
| Determinant cost and sharpness | passed | The adjugate bound is sharp for the displayed `E(X)`. |
| Strict integer Laurent paraunitarity | passed | Sum of tap-coefficient squares equals one; no nontrivial integer energy-preserving bank survives exact identity normalization. |
| Nested modulus and phase conventions | passed | Compatibility is precisely a linear congruence with modulus `L/g`. |
| Child count, including captured phases | passed | `g'/g` divides `N`; captured compatible parents have all children compatible. |
| Baseline versus deeper valuation layers | passed | Final text distinguishes `k<=s` from `k>s`; the latter must use the full `L_p(k)`. |
| Blocked order, birth depth and `W/G` mass | passed | `d'=d/gcd(d,M)`, `s'=s+v_p(M)` for the same output primes. |
| Cyclotomic fiber identity and norm budget | passed | Distinct old conductors occupy disjoint factors in the exact substituted polynomial. |
| Degree after base-height change | passed | `D_n<=M D'_t` and `n=Mt` give the claimed direction `D'_t/t>=D_n/n`. |
| Compression, including empty exceptional set | passed | `m=2^v_2(n)` in the empty case; odd quotient and both packet equalities remain valid. |
| Claims about finite verification coverage | passed | Recorded ranges match the programs; all are finite corroboration only. |
| Unrestricted ABC or universal tap obstruction | not addressed | Neither source claims either result. |
| A new high-order arithmetic estimate or nonzero auxiliary value | not addressed | Explicitly identified as the remaining work. |

## 4. Independent derivations of the critical implications

### Integral reconstruction, determinant cost and the selected functional

For an integral matrix `M`, every output entry has valuation at least `nu_p(x)`, where `nu_p` is the minimum of the coordinate valuations and `v_p(0)=infinity`. If `D=det M` is nonzero, then

`nu_p(x)+v_p(D)=nu_p(Dx)=nu_p(adj(M)Mx)>=nu_p(Mx)`.

This proves both bounds with the displayed signs. Multiplying `Nx` by `q^-1` subtracts `v_p(q)` from its content, yielding (2). For a matrix over the valued field, the coefficient minimum gives the lower bound; applying it to the inverse gives the upper bound in (3). Zero matrix entries are harmless because their valuations are infinite. The nonzero-vector and nonsingularity hypotheses prevent an undefined finite-content comparison.

For a rectangular split pair `ST=I`, integrality of each stage gives

`nu_p(x)<=nu_p(Tx)<=nu_p(STx)=nu_p(x)`.

This does not apply when only a field inverse is available. For a diagonal single-tap channel at a unit `z`, the valuation shift is exactly `v_p(g_i)`; integral invertibility requires a unit scalar. Retaining `F=ell x` gives the exact identity `F=(ell S)y`. It supplies no bound on an individual scalar from minimum channel content alone.

For a concrete smallest odd-prime check, take `p=3`, `X=2`: the exposed channels are `(3,1)`, while the hidden channels are `(2,-1)`, both units, and `2*2+(-1)=3`. Replacing `X` by `p^e-1` gives arbitrary depth in this same example. The determinant bank sends `(1,1)` to `(p^e,0)` and has determinant `p^e`, so its minimum output depth exactly attains the upper bound. The zero second coordinate has infinite depth and does not alter the minimum. At `p=2`, the odd-prime hidden-channel example and the assertion that `1/2` is a unit are intentionally unavailable; the general determinant lemma still applies.

For the rational adaptive bank, the stated inverse is exactly `[[p^e,-1],[0,1]]`, and reconstruction of the selected contact is `p^e y_1`. The coefficient maximum is at least `p^e`, as claimed. This example proves its own cost, not a universal lower bound for every adaptive method.

For strict integer paraunitarity, write each Laurent entry as a finite sum of integer taps. The `z^0` coefficient of a diagonal entry of `F(z)F(z^-1)^T` is exactly the sum of the squares of all taps in that row. Equality to one forces exactly one tap, equal to `+1` or `-1`. Two rows using the same column would have a nonzero signed monomial in their off-diagonal inner product, contradicting zero. Squareness therefore gives a signed monomial permutation. Rational rotations or a nonidentity scale fall outside that strict claim. The displayed `3/5,4/5` example correctly incurs denominator depth at 5.

### Exact plus contacts and nested children

If `p|A^n+B^n`, then `(A/B)^n=-1` in the odd-prime field, so `d` is even and `n=(d/2)q` for odd `q`. Put `u=A^(d/2)`, `v=B^(d/2)`. Since `u/v=-1 mod p`, `p` does not divide `u-v`, and therefore `v_p(u+v)=v_p(A^d-B^d)=s`. Odd-prime lifting gives

`v_p(A^n+B^n)=s+v_p(q)=s+v_p(n)`.

The needed lifting identity can be derived without an external source: raising a unit pair congruent modulo `p` to a prime-to-`p` exponent preserves its difference depth, and a `p`th power raises that depth by exactly one. In the binomial expansion the first term has valuation `s+1`, and every later term has greater valuation because `p` is odd and `s>=1`. Iteration proves the formula for all positive exponents. Applying the same difference identity to `A^d,B^d` proves its use in blocking.

Requiring valuation at least `k` says that the odd multiplier `q` is divisible by `p^max(0,k-s)`. Thus the exact residue is `L_p(k)/2 mod L_p(k)`, with the half-period correctly defined because `L_p(k)` is even.

Solving `Mt=L/2-j mod L` gives compatibility `gcd(M,L)|(L/2-j)` and one solution class modulo `L/g`. For children, put `g'=gcd(MN,L)`. If the parent is compatible, divide the child congruence by `g`: its coefficient `M/g` is a unit modulo `g'/g`, because `g'/g` divides `L/g` and `gcd(M/g,L/g)=1`. Exactly one class of `a` modulo `g'/g` works; `g'/g|N`, giving exactly `Ng/g'` children. This proof includes `N=1`, `r=0`, residual period one, and the fully captured case `L|M`.

At the baseline, the captured phase has exponent `(d/2)(2t+1)`, so its valuation is exactly `s+v_p(2t+1)`. Writing `t=pu+a`, the unique exceptional child has `a=(p-1)/2` and `2t+1=p(2u+1)`; all other children have valuation exactly `s`. The birth floor is therefore retained, not diluted by the fraction of compatible paths. The final baseline restriction on the coprime-radix sentence is necessary: for example, with `A=2,B=1,p=3,d=2,s=1,N=3`, the three first-level phases are all compatible at depth 1, but only the phase `j=0` is compatible at depth 2.

### Blocking, fibers and the normalization direction

Let `g=gcd(d,M)`. The order of `(A/B)^M` is `d/g`. Its difference at that order is `A^(d M/g)-B^(d M/g)`, with valuation `s+v_p(M/g)=s+v_p(M)` because `p` does not divide `d` or `g`. Since the output prime set is unchanged and `n=Mt`, each odd output prime gains `v_p(M)` in its birth exponent and loses precisely that amount from its inherited lifting exponent. This proves both `W'` and `G'` identities. The product `H_M` uses only some prime-power factors of `M`, so it divides `M`; ordinary primes can indeed become exceptional. The example `2^3+1=9` verifies this at the smallest such case.

For the cyclotomic identity, the roots of `Phi_r(z^M)` are exactly roots of unity of orders `d` satisfying `d/gcd(d,M)=r`. They are simple in characteristic zero, and `d` divides `Mr`. Both monic polynomials have that exact root set. Hence the identity is over `Z[z]`, and its homogeneous form is valid over `Z[X,Y]` with degree `M phi(r)`. Different old conductors yield disjoint cyclotomic factors even when they map to the same new conductor. Consequently the product indexed by `S` divides the full product indexed by `S'`, without repeated allocation of a factor.

At `A>B>=1`, every added homogeneous cyclotomic value is a positive integer: conductors 1 and 2 give `A-B` and `A+B`; all other roots pair into positive conjugate products. Thus the exact new norm product is at least the old one. The map on primitive roots has at most `M` preimages per root, yielding the degree inequality. New exceptional orders can only enlarge the new occupied set. The inequality after dividing by the new exponent goes in the stated direction:

`D'_t/t >= D_n/(Mt) = D_n/n`.

The example `7^2+1=50` gives `d=4,s=2`; blocking by 2 gives `d'=2,s'=2` and exactly the same factor 50. Halving the degree did not halve the logarithmic evaluation cost.

### Compression and its actual ABC scope

For a plus conductor `d|2n`, `d` not dividing `n`, write `n=2^a q` with `q` odd. Then `d=2^(a+1)e` for some `e|q`, so `d/2` divides `n` and has 2-adic valuation `a`. Their lcm with `2^a` therefore divides `n` with odd quotient, including when the exceptional set is empty. Every old exceptional prime occurs at exponent `m`, since `m/(d/2)` is odd. Conversely `x[m]|x[n]`, so no new exceptional birth prime appears at `m`. The original-base birth depths are independent of exponent; hence `E_m=E_n` and `W_m=W_n` exactly.

The 2-adic radical defect is unchanged because `m` and `n` have the same parity; when both are odd and both bases are odd, the value `v_2(A^h+B^h)=v_2(A+B)` is independent of the positive odd exponent. In all other cases the 2-adic defect is 1. Each exponent in `G_m` is at most its exponent in `G_n`, so `G_m|G_n`; the quotient divides `G_n`, and `G_n|n`. All occupied orders are allowed at exponent `m`; summing the degrees of **all** plus factors gives exactly `m`, so `D_n<=m`.

From compression alone,

`log U(x[n]) <= log x[m] + log n <= m log A + log 2 + log n`.

Since `log x[n]>=n log A` and `A>=2`, the ratio tends to zero uniformly in the bases whenever `m/n -> 0`. This yields the stated restricted eventual ABC implication. The condition also gives `D_n/n -> 0`, already inside RR3's pointwise degree criterion. The safe conclusion is that this compression condition gives no new asymptotic regime and no high-order estimate. It is not a claim that every numerical sufficient bound obtained from compression is dominated term by term by every coarse implementation of the degree estimate.

Finally, the multichannel sufficient certificate is arithmetically correct. If a nonzero integer `Z` is divisible by `W_n`, then `W_n<=|Z|`. The displayed bound implies `U(c)=B_2W_nG_n<=D c^gamma`; primitivity gives `rad(ABc)=D c/U(c)>=c^(1-gamma)`. With `gamma=epsilon/(1+epsilon)` and `epsilon>0`, this is exactly the stated pointwise ABC inequality with constant one. Constructing such a nonzero, sufficiently small integer is still missing.

## 5. Computation checks and reproducibility

Both original verifiers were rerun with all output redirected to the disjoint `reviews/refinement_multichannel_checks/` tree. Source hashes were checked before and after the independent tests; the author results were not overwritten.

Commands from `/workspace/scratch/f276b5072653`:

```sh
python3 abc_work/polyphase_taps/reviews/refinement_multichannel_checks/independent_check.py
python3 abc_work/polyphase_taps/reviews/refinement_multichannel_checks/refinement_independent.py
```

The first command also runs the multichannel verifier with its output directory redirected. The refinement verifier was run as an absolute script path with current working directory `reviews/refinement_multichannel_checks/refinement`, so its relative `verification.json` output stayed there.

| Check | Observed result and exact scope |
|---|---|
| Author multichannel verifier | Passed 8 exact-depth contacts and 50,688 matrix/vector checks, matching its recorded range. |
| Independent linear algebra checks | Passed 95,232 nonsingular 2-by-2 matrix/vector cases with entries `-2..2`, primes 2,3,5,7, all 24 nonzero vectors in `-2..2`, and scales 1 and `p^-2`; checked integer, inverse-coefficient and rational-denominator bounds. 20,352 cases had positive determinant depth. |
| Author refinement verifier | Passed 252 full-factorization grid cases, 735 divisor blockings, 1,029 component identities, 252 compressions, 78,945 sampled nested contacts and 3,165 child-count checks, matching its record. |
| Independent complete phase periods | Passed 20,586 direct membership checks and 1,164 direct child-existence checks, for four local examples, `k=1..3`, radices 1,2,3,5,6 and tree levels 0,1,2. Every phase and its complete residual period was tested, including index zero. |
| Independent symbolic substitution | Passed 48 exact polynomial identities over `Z[z]`, `M=1..6`, `r=1..8`, including conductor 1. |
| Independent output transport | Passed 297 direct blockings and 110 compressions on coprime `1<=B<A<=6`, `n=1..10`; orders and birth depths came directly from output factorization and powers, not the author's cyclotomic helper. |

One finite-coverage nuance: the author's bounded-matrix sweep uses `p=17` and entries `-3..3`. Its nonsingular determinants never have a factor 17, so that sweep tests the unit-determinant specialization; the separate contact-dependent bank tests sharp positive determinant depth. The additional independent sweep above explicitly includes positive determinant depth. This limits the interpretation of the original finite sweep without invalidating its stated assertion or the adjugate proof.

Independent scripts and machine-readable outputs are beside this report under `refinement_multichannel_checks/`. Script SHA-256 values: `independent_check.py` is `e3c32f4d364e189a477e1af9f8a5456afa58603569e640bc7665fd4562271305`; `refinement_independent.py` is `f65db6707babcb21da8133a67104a5feb2fe9ce0c288d3620ba06cf2236ae350`. Finite agreement is supplementary evidence, not proof of a universal claim.

## 6. Remaining gap and cheapest next check

There is no remaining gap in the local statements at the audited revisions. The research gap is a global estimate that controls a selected high-order birth contact or a provably nonzero auxiliary integer without paying the same determinant, denominator, degree or evaluation-height cost already recorded here. Neither sparse compatible paths nor preserved channel content supplies that estimate.

For any proposed next tap/refinement certificate, the cheapest decisive check is to state its exact selected functional and a concrete nonzero integer value, then prove both the exceptional-prime divisibility and an independent height bound. Check these on a single full-order exceptional contact before claiming a global ABC consequence. A mere coordinate change or a relabeling of `W` and `G` does not meet that obligation.
