# Fresh audit of Circuit Obstructions C03–C08

Audit date: 2026-10-07. Target: the written claims in the source archive `komorebi-circuit-obstructions-v1.2.0`, principally `docs/THEORY.md` §§2–5, with definitions and lower-bound dependencies in `docs/FOUNDATIONS.md`. The unchanged historical `docs/reference/Theorems_v1.0.0.pdf` supplies the more precise theorem statements in Chapters 4–8. This is an adversarial mathematical review and bounded computational replay, not a new Lean verification or a novelty search. Original source and baseline files were not edited.

The main calibration, small-oracle, projection, algebra-dimension, and fingerprint formulas have valid written proofs in the stated models. Two surrounding sentences need explicit boundaries in the consolidation: the scalar impossibility sentence needs at least two witnesses, and disjoint trace factorization must specify its variable domains. The historical PDF already states the blockwise factorization correctly. The algorithmic consequence remains conditional on an evaluator that has not been constructed.

| Claim | Primary verdict for the normalized claim | Qualification |
|---|---|---|
| C03 | Proved as written | The old bound of `n−1` includes the degree term; the affine one-packet term alone is 3. |
| C04 | Proved as written | Explicit constructions plus lower bounds prove optimality; no exhaustive reversible-circuit search is needed or claimed. |
| C05 | Proved as written | Domain is `m≥2`. Unsafe extraction starts at `m=3`; strict restored-cost separation starts at `m=4`. |
| C06 | Proved as written | Main dimension theorem includes `m=0`. Its scalar satisfiability-impossibility sentence requires `m≥1`. |
| C07, polynomial identities | Proved as written | `w` is Boolean-quotient data; `z` consists of ordinary formal polynomial variables. |
| C07, efficient algorithm | Conditional on a named input | A uniform exact polynomial-time evaluator over efficiently represented growing fields is assumed, not supplied. |
| C08, blockwise factorization and displayed overlap counterexamples | Proved as written in the historical theorem statement | The compressed Markdown sentence is correct only after specifying each trace domain. A common ambient-domain reading is false. |

## 1. Exact conventions and claim cards

The Boolean algebra on `n` inputs is `F2[x_1,…,x_n]/(x_i^2−x_i)`, identified with Boolean functions on `F2^n`. Degree is the degree of the unique multilinear ANF. The mathematical zero degree can be treated as `−∞`; source Python uses `−1`, while stored tables use a zero sentinel. None of the arguments below depends on identifying that sentinel with a nonzero degree-zero polynomial.

For a Boolean function `f`, `I_f={h:h(1+f)=0}` is exactly the ideal of functions supported on `f^{-1}(1)`. For `f(v)=1`,

\[
\beta_v(f)=\min\{\deg h:h\in I_f,\ h(v)=1\},\quad
\beta(f)=\max_{f(v)=1}\beta_v(f),\quad \beta(0)=0.
\]

For nonzero `f`, `alpha_1(f)` is the minimum degree of a nonzero member of `I_f`. The affine optimization uses all `2^{n+1}` affine masks `ell`, with `beta*(f)=max_ell beta(f+ell)` and the documented zero sentinel for `alpha_1(0)`.

`M(f)` denotes minimum fan-in-two AND count in an XOR–AND computation with constants, affine operations, and arbitrary sharing. `T_rest(f)` denotes minimum Toffoli count among legal distinct-wire NOT/CNOT/Toffoli permutations implementing `(x,0^a,y) -> (x,0^a,y+f(x))` for every `x` and both target values, with any finite number of initially zero ancillas restored at the boundary. Intermediate workspace and output feedback are allowed. Affine operations have zero Toffoli cost but count toward total gate count.

| ID and exact locator | Objects, quantifiers, and conclusion | Hypotheses and exceptions |
|---|---|---|
| C03: `THEORY.md` §2, equations (4)–(5); historical Results 4.1–4.4, printed pp.7–8 | For every integer `k≥2`, `n=k+2`, `F_k=ab OR product_i z_i`, one has `alpha_1(F_k)=2`, `beta(F_k)=k`, `deg F_k=k+2`, `max_ell alpha_1(F_k+ell)=3`, and `beta*(F_k)=k+1`. Consequently `2n−5≤T_rest(F_k)≤2n−3`. | All polynomials are Boolean multilinear over `F2`. No exact cost is claimed when interval endpoints differ. |
| C04: `THEORY.md` §2, “Exact small restored-oracle calibration”; historical Theorem 4.5, printed p.9 | Every Boolean function on one, two, or three logical inputs attains `max(0,deg f−1,2 beta*(f)−3)`. Optimal counts are 0 for affine functions, 1 for nonaffine quadratics, and 3 for three-variable cubics. | Sizes are separately quantified; 276 counts truth tables across all three sizes, not 276 distinct three-input functions. |
| C05: `THEORY.md` §3, equations (6)–(8); historical Theorems 5.3–5.4 and Proposition 5.5, printed pp.11–12 | For every `m≥2`, set `a=(1,…,1)`, `V=F2^m \ {0,a}`, `n=2^m−2`, `L_j=sum_{v_j=1}x_v`, `P_m=product_j L_j`, and `Q_m=[P_m]_2` in the original `x` coordinates. Then `M(P_m)=m−1`, `T_rest(P_m)=2m−3`, and `M(Q_m)=T_rest(Q_m)=n/2`. An extracted grade need not belong to `I_{P_m}`. | Projection is in the original coordinate system. Safety failure is existential, not asserted for every `m`; indeed `Q_2=P_2`. Nonlinear count differs from total gate cost. |
| C06: `THEORY.md` §4, Theorem 4.1; historical Theorem 6.1 and Corollary 6.2, printed pp.13–14 | For a field `K`, `W={0,1}^m`, `B=K^W`, and a `K`-linear multiplicative map `Phi:B -> A` retaining every primitive point idempotent, `dim_K A≥2^m`. Every unital such map to `K` is evaluation at one witness. | Any finite nonnegative witness length is allowed. Target multiplication is bilinear; the proof needs neither commutativity, associativity, nor a unit. `Phi` is a single map on the full witness algebra. |
| C07: `THEORY.md` §5, equations (10)–(11); historical Theorems 7.1, 7.3, Lemma 7.4, Proposition 7.5, printed pp.15–16 | For `R:{0,1}^m -> {0,1}` and a characteristic-two field `K`, `P_R(z)=sum_w R(w)product_i z_i^{w_i}` is formally zero iff `R` has no accepting witness, and equals top-`w` coefficient extraction of `R(w)product_i(1+(1+z_i)w_i)` after Boolean reduction in `w`. Degree is at most `m`. A uniform exact efficient evaluator would give the stated one-sided randomized SAT algorithm. | Ordinary polynomial variables `z` are not reduced by `z_i^2=z_i`; only `w` is reduced. Algorithm requires succinct verifier input, efficient field arithmetic/encoding, independent uniform field samples, and a field family of polynomial size with `q≥4m`. |
| C08: `THEORY.md` §5, overlap subsection; historical Proposition 8.1 and Counterexample 8.2, printed p.17 | For disjoint coordinate sets `S,U`, `T_{S union U}(AB)=T_S(A)T_U(B)`. For one shared bit, `T_z(w)=z`, `T_z(1+w)=1`, but `T_z(w(1+w))=0`; also `T_z(w^2)=z` while `T_z(w)^2=z^2`. | Each block trace sums only over its own block. The first inequality requires `z≠0`; the second requires `z^2≠z`, hence cannot be demonstrated over `F2` alone. |

## 2. Dependency graph and obligations

The graph has no circular dependency. C03–C05 use the complete-cover bound as a lower-bound input and supply their own upper constructions. C06–C08 are independent of circuit lower bounds.

- C03: Boolean ideal definitions -> monotone monomial ideal -> raw parameters; accepting affine flats and two-point indicators -> affine maxima; complete-cover lower bound + legal compute/uncompute circuit -> cost interval.
- C04: degree bound + classification of alternating forms in at most three variables -> quadratic lower/upper counts; cubic translation + affine-mask invariance + monomial oracle lower/upper bound -> cubic optimum.
- C05: rank-`m` coordinate change -> full-function degree and codimension-`m` accepting flat -> exact full cost; pair evaluations -> matching quadratic; affine restriction + nondegenerate polar form -> exact quadratic lower bound; legal direct accumulation -> upper bound.
- C06: primitive orthogonal idempotents -> linearly independent images -> dimension bound; field scalar idempotents + unitality -> evaluation classification.
- C07: distinct monomials -> zero/nonzero equivalence; Boolean-cube sum identity -> weighted top coefficient; root-count induction + assumed efficient evaluator -> randomized implication.
- C08: independent exponent blocks -> product expansion; shared-bit Boolean reductions -> counterexamples.

| Obligation | Status | Evidence or limitation |
|---|---|---|
| C03 upper safe packet for every affine mask | Passed | On `z_1=0`, either one remaining `z` coefficient supplies an affine accepting flat, or fix an accepting `(a,b)` pair. Full-space codimension is at most 3. |
| C03 exclusion of degree-2 packets for `G_k=F_k+a` | Passed | Separate `k≥3` and `k=2` cases are necessary and present. The negative face and one negative point kill the residual affine factor. |
| C03 complete detection at the designated positive point | Passed | `b=1` restricts `G_k` to the singleton `(1+a)B` on `k+1` variables. |
| C04 quadratic factorization and cubic translation | Passed | Nonzero alternating rank on at most three dimensions is 2; translations independently cancel the three cubic-induced quadratic coefficients. |
| C04 restored witnesses, including target 1 | Passed | Fresh scalar replay checks both target values and every input; all 276 constructions attain the bound. |
| C05 linear rank, pair extraction, and full polar rank | Passed | Standard basis columns remain for `m≥2`; zero and singleton evaluations vanish; complementation partitions `V` into pairs. |
| C05 lower bound with arbitrary intermediate degree/sharing | Passed | Restrict successive AND outputs to affine functions using at most one nonempty affine equation per gate. No assumption of quadratic intermediate gates enters. |
| C05 safety preservation | Failed, with counterexample | This is deliberately the refuted candidate inference; see input 13 below. |
| C06 independence under stated algebra hypotheses | Passed | Right multiplication by one image isolates its coefficient; bilinearity suffices. |
| C06 scalar impossibility at empty witness length | Failed, with counterexample | The theorem remains true, but the ancillary sentence must restrict to `m≥1`. |
| C07 field arithmetic and top coefficient | Passed | Characteristic two and Boolean reduction are used exactly where needed. GF16 field laws and extraction are explicitly checked. |
| C07 unconditional efficient evaluator | Not addressed | Neither the mathematical statement nor finite code claims to supply it. The algorithmic consequence is conditional. |
| C08 intended blockwise factorization | Passed | Cartesian-product expansion proves it; finite controls use separate one-bit traces and a joint two-bit trace. |
| C08 same-domain multiplication reading | Failed, with counterexample | Merely having disjoint predicate dependence sets does not justify multiplying two full ambient traces. |
| C03–C08 fresh Lean checking | Out of scope | These groups remain written/finite, without a new kernel certificate. |
| Broad novelty or current best circuit bound | Out of scope | No such assertion is used or tested. |

The complete-cover theorem itself is under the parallel core audit. This extended pass inspected its exact stated use and the necessary model conventions; it does not certify a separate fresh Lean replay of that dependency.

## 3. Decisive mathematical reconstruction

### C03: affine maxima really separate the parameters

On `z_1=0`, the polynomial `ab+ell|_{z_1=0}` cannot be zero: its quadratic coefficient is 1 and an affine mask cannot cancel it. If the restricted mask contains a remaining `z` coefficient, imposing `a=0` and the affine mask equal to 1 gives a nonempty accepting flat. If it does not, some `(a,b)` pair is accepting, since the nonzero two-bit polynomial is not identically zero. Multiplying indicators of the imposed affine equations gives a nonzero safe polynomial of degree at most 3.

For `G_k=F_k+a`, the explicit degree-three packet is `a(1+b)(1+z_1)`. At `a=0`, a degree-at-most-two safe packet is supported where all `z_i=1`. For `k≥3`, the monotone support ideal forces that restriction to zero. Therefore `h=aL`, with `L` affine in `(b,z)`. The negative face `a=b=1` forces all `z` coefficients of `L` to vanish and its constant/b coefficients to agree, so `L=c(1+b)`. The negative input `a=1,b=0,z=all ones` forces `c=0`. At `k=2`, the possible nonzero restriction is `c z_1z_2`; its quadratic coefficient survives on `a=b=1` and cannot be cancelled by affine `L`, so again `c=0`.

Restricting `b=1` gives `G_k=(1+a)B`. A safe polynomial detecting its sole accepting point on that face equals the singleton indicator after restriction, so has degree at least `k+1`. Conversely no affine adjustment is zero (because `F_k` has degree `k+2`) or a singleton (its one-packet degree is at most 3, whereas a singleton's is `n≥4`). Every adjustment therefore has at least two accepting points, and the sum of two point indicators supplies degree at most `n−1` at each positive. This proves both maxima for every `k≥2`.

The first equality-extrapolation failure is `n=5`, where the maxima are 3 and 4. Their gap is `k−2`, hence unbounded. This is an exact counterexample to the proposed equality, not merely an observed mismatch. The cost interval follows from the complete-cover bound and the explicit `A`, `B`, `AB` compute/uncompute implementation. It does not determine an optimum inside that interval.

Publication wording: the former combined lower bound is
\[
\max\{0,\deg F_k-1,2\max_\ell\alpha_1(F_k+\ell)-3\}=n-1.
\]
Its alpha-only term is 3. Spell out the combined expression instead of attributing the growing `n−1` term to alpha alone.

### C04: small optimality follows from complete cases

For nonaffine quadratics on two or three variables, the alternating polar matrix has rank 2. A change of linear coordinates reduces the quadratic part to a product of two independent linear forms; diagonal reductions produce only affine terms. One legal Toffoli on two parity registers accumulates that product, after which the parity registers are uncomputed. Degree 2 requires at least one multiplication/Toffoli.

For a three-input cubic, write `f=x_1x_2x_3+q+ell`. Translating coordinate `x_i` changes the coefficient of the quadratic product of the other two coordinates by its translation bit. Translation of `q` leaves its quadratic coefficients unchanged. Thus choose the three translation bits to cancel all quadratic coefficients. The remainder is a cubic monomial plus an affine mask, so the singleton/codimension-three complete-cover lower bound gives 3, and the monomial oracle attains 3.

The counts independently follow from ANF coefficient dimensions: affine counts `4+8+16=28`, nonaffine quadratic counts `(16−8)+(128−16)=120`, and three-bit cubics count `256−128=128`. These are all functions in the specified sizes; a lower bound plus a matching construction is an exact optimum argument even without circuit search.

### C05: exact costs, and the smallest safety witness

The retained columns include the `m` standard basis vectors, including at `m=2`; hence the forms are independent and extend to an invertible linear coordinate system. In those coordinates the function is an `m`-fold monomial with unused coordinates. Its degree is `m`, and every nonzero safe polynomial contains the `m` required coordinate factors, so has degree at least `m`. This gives `M≥m−1` and `T_rest≥2m−3`, with matching explicit constructions.

For distinct `u,v`, the quadratic ANF coefficient is the second Boolean difference at zero,
\[
P_m(e_u+e_v)+P_m(e_u)+P_m(e_v)+P_m(0)=[u+v=a].
\]
The excluded zero and `a` columns are exactly what make the latter three evaluations zero. The involution `v -> v+a` has no fixed point and preserves `V`, so these coefficients form a perfect matching. Its polar matrix is a direct sum of nonsingular two-by-two alternating blocks.

In a general computation with `t` ANDs, successively restrict a nonconstant affine operand of each new AND to zero. Such a restriction is nonempty and loses one direction dimension; if an operand is already constant, no restriction is needed. This gives an affine subspace of dimension at least `n−t` on which the output is affine. A quadratic with nondegenerate polar form can be affine on such a space only if its direction space is totally isotropic, of dimension at most `n/2`. Thus `t≥n/2`, even with high-degree intermediate products. Reading any restored circuit at `y=0` gives an XOR–AND computation with one multiplication per Toffoli; one Toffoli per matched pair also directly attains the lower bound.

At `m=2`, both full and projected functions cost one Toffoli and the projection is safe. At `m=3`, both costs are 3, but safety already fails: with labels `1,…,6`, input 13 selects labels `1,3,4`. Their XOR is 6 rather than 7, so `P_3=0`; the pair `(3,4)` contributes exactly one term to `Q_3`, so `Q_3=1`. At `m=4`, restored costs are 5 and 7, the first strict separation. At `m=10`, they are 17 and 511. The ratio grows exponentially in `m`, but the extracted cost remains linear in the true input length `n`.

The constructed full circuit has `2m(2^{m−1}−1)` CNOTs as well as `2m−3` Toffolis. Consequently its total length is `O(n log n)`, while the projection has `n/2` direct gates. No exponential separation in total ordinary gate count follows.

### C06: the dimension theorem is correct; one ancillary boundary is false

Let `e_v=Phi(delta_v)`. Linearity and multiplicativity give nonzero orthogonal idempotents. In a relation `sum_v c_v e_v=0`, multiply on the right by `e_u`. Bilinearity gives `c_u e_u=0`; the vector-space field axiom and `e_u≠0` imply `c_u=0`. This proves the bound with no hidden unital, associative, commutative, or finite-dimensional-target assumption.

For scalar target `K`, each idempotent is 0 or 1. Orthogonality permits at most one 1; unitality forces exactly one, so the map is evaluation. `THEORY.md:215` then says that such a summary cannot preserve satisfiability of every singleton verifier. That requires `m≥1`. At `m=0`, `W` has one empty witness, `B=K`, and identity/evaluation preserves its unique singleton verifier. This is the smallest valid counterexample to that surrounding sentence, not to the dimension theorem or evaluation classification. The historical PDF's wording “loses every singleton witness other than v_0” is valid even when there are no others.

The hypotheses concern a single linear multiplicative summary serving every predicate on a fixed witness space. They impose no lower bound on the succinct representation length of one algebra element and do not constrain arbitrary syntax-dependent or nonlinear algorithms.

### C07–C08: formal variables, algorithmic input, and trace domains

Different witnesses contribute different exponent vectors to the ordinary formal polynomial `P_R`; accepting coefficients are 1, so none cancels. The top Boolean coefficient identity follows by summing each `w` monomial over the Boolean cube in characteristic two: a proper-support monomial has an even number of accepting evaluations; the full monomial has one. At a witness bit 0, its multiplier is 1; at bit 1, its multiplier is `z_i`. This proves the weighted identity after Boolean reduction in `w`.

The root-count induction is valid for every finite field: a last-variable leading coefficient of degree at most `d−r` is zero with probability at most `(d−r)/q`; otherwise the resulting univariate polynomial has at most `r` roots. The union bound gives `d/q`. To obtain the proposed SAT running time, the evaluator must accept a succinct verifier description, not its `2^m`-entry truth table, and work uniformly over a growing explicitly represented characteristic-two field with efficient arithmetic. For `m≥1`, choosing `q=2^ceil(log_2(4m))` gives `4m≤q<8m`, permitting `O(m log m)` uniform random bits. Under that named evaluator hypothesis, unsatisfiable inputs always yield zero and satisfiable inputs accept with probability at least `3/4`. The implementation holds exponentially many coefficients and does not satisfy the hypothesis. The historical Proposition 7.5 already states the efficient-field qualification explicitly.

For precision define
\[
T_S(A)=\sum_{u\in\{0,1\}^S} A(u)\prod_{i\in S}z_i^{u_i}.
\]
Then, for disjoint `S,U`, the correct rule is `T_{S union U}(AB)=T_S(A)T_U(B)`, by distributing a sum over the Cartesian product. Both the historical PDF and checker use this convention.

If instead both separate traces are over one common ambient set `S union U`, each irrelevant block contributes a factor `product_i(1+z_i)`, and the naive product generally fails. The smallest useful full-domain counterexample has two bits: `A=w_1`, `B=w_2`, `z_1=z_2=1`. Their two full ambient traces are both zero, while the ambient trace of `AB` is 1. Thus write the domains rather than relying on a dependence-set phrase.

The intended one-bit overlap failure is even smaller: `T_z(w)=z`, `T_z(1+w)=1`, but `w(1+w)=0` in the Boolean algebra, so the joint trace is zero. In GF16 at the code's `z=2`, separate-product and joint values are 2 and 0; the square comparison is 4 versus 2. These refute ordinary field multiplication of trace summaries. They do not exclude every nonlinear lookup rule, context-dependent representation, or evaluator.

## 4. Computation scope and provenance

Fresh audit evidence is separated from frozen release evidence. New bounded replay uses source constructors and profile helpers where stated, so independent scalar interpretation should not be represented as an independent implementation of every mathematical component.

| Evidence | Fresh scope | Result and limitation |
|---|---|---|
| `reviews/calibration_audit.py`, `calibration_audit_checks.json` | All 32, 64, and 128 affine masks for designated C03 families with `n=4,5,6`; all 276 C04 functions; all input/target boundary states for their constructed circuits | PASS. Maxima `(3,3),(3,4),(3,5)`; 4,240 scalar boundary cases; counts `28/120/128`; lower-bound equality. Fresh scalar interpreter differs from source bit-sliced trace, but constructors and rank/profile helpers are reused. |
| Projection reviewer replay, `projection_gluing_audit_checks.json` | `m=2,…,10` coefficients/ranks/construction counts; full truth tables and both oracle target values only `m=2,3,4` | PASS and exact equality to frozen `projection.json`. 693,965 pair coefficients, 9 rank cases, 16,452 truth inputs, 65,808 input/target cases. Temporary full output was deleted; provenance file records that limitation. |
| Fingerprint reviewer replay, `fingerprint_audit_checks.json` | Every Boolean verifier for `m=1,2,3`; GF16 root/fingerprint evaluations on all field points; top extraction full GF16 grids only `m≤2`, coordinates `0,…,3` for `m=3`; two disjoint one-bit blocks | PASS. 1,052,736 fingerprint evaluations; 20,544 extraction checks; 4,096 disjoint controls; 4,096 field-law triples. Baseline JSON equality was not separately compared in this reviewer run; temporary output was deleted and this is recorded. |
| Original `verify_completeness.py` inspected | All profiles `n=1,…,4`; C03 designated family tables `n=4,…,9`; every affine family mask only `n≤8` | Full four-input table is 65,536 functions, but independent evaluation-span checks are only the specified 765 cases. Ninth-input affine maxima are proved, not exhaustively searched by this checker. |

To reproduce the fresh calibration audit:

```sh
PYTHONDONTWRITEBYTECODE=1 python reviews/calibration_audit.py \
  --source source/komorebi-circuit-obstructions-v1.2.0 \
  --out reviews/calibration_audit_checks.json
```

The project-level fresh `scripts/verify.py --all` replay is owned by the parent publication workflow. Do not attribute that broader run to this sub-audit or claim full isolated output retention from the two reviewer reruns.

Source pins:

| File | SHA-256 |
|---|---|
| `docs/THEORY.md` | `6d06aa874dd9ef2dbdd17e574157872334e9594ce2eb7b695cba61e4e53703c8` |
| `docs/FOUNDATIONS.md` | `f8d428d6263bd1380f08d74711ffa7577c9a6b9013a6cffc9ddcc83d5ce629c6` |
| `docs/CLAIMS.md` | `b22b1b87a7f22169e861b2d5906770976a2c1d6d50cd4176a057fc9fc72872b1` |
| `docs/reference/Theorems_v1.0.0.pdf` | `3e3da3b419f70470e3e8120093811dc6120d76ad4923007476f6429ddc6a18a6` |
| `checks/verify_completeness.py` | `693f60831b368bbae50fbc8b782a18b4472711af1dc1d463ee2477ed15e9e4d4` |
| `checks/verify_projection.py` | `253069b7f3b5cdbcd88c151c41a5dca887cbc1cc0fbd45dc12b237979ac2bc17` |
| `checks/verify_fingerprint.py` | `4c82a822adbdccf5a1472b5c3b4ea5317d573645cd3f8e92e1b230c8e0e0c68f` |

## 5. Exact primary-source dependency check

The source proofs are self-contained at the points used here. References S1–S3 supply standard models and terminology; no external theorem is needed to fill a missing C03–C08 implication. Their exact primary versions were inspected through official arXiv full texts on 2026-10-07. No broad literature or priority search was attempted. No external PDF bytes were saved locally, so no cache-content hash is asserted.

| Reference | Verified version and locator | Required translation and finding |
|---|---|---|
| S1, Mathias Soeken, *Determining the Multiplicative Complexity of Boolean Functions using SAT* | `arXiv:2005.01778v1`, 4 May 2020; [official PDF](https://arxiv.org/pdf/2005.01778), printed p.2, Section III | States the algebraic-degree-minus-one multiplicative-complexity lower bound in the two-input AND/XOR/inverter model. The manuscript gives its own proof; citation is valid background, not a substitute for that proof. |
| S2, Joan Boyar and Magnus Gausdal Find, *Multiplicative Complexity of Vector Valued Boolean Functions* | `arXiv:1407.6169v3`, 22 February 2018; [official PDF](https://arxiv.org/pdf/1407.6169), printed pp.4–5, definitions and paragraph preceding Proposition 2 | General XOR–AND multiplicative complexity is the default. It states existence of an affine subspace of dimension `n−M` where a one-output function is affine. This supports the exact general-circuit model used by C05. The manuscript's gate-by-gate proof establishes the needed implication internally. |
| S3, Chris Beck and Yuan Li, *Represent MOD function by low degree polynomial with unbounded one-sided error* | `arXiv:1304.0713v1`, 2 April 2013; [official PDF](https://arxiv.org/pdf/1304.0713), printed pp.1–2, immunity definition | One-sided immunity is the least degree of a nonzero element of the ideal generated by `f` in the Boolean quotient. Over `F2`, this is the manuscript's `alpha_1`; it differs from the minimum of the two polarities called two-sided immunity. No MOD theorem is transferred to C03–C08. |

The 2018 S2 version label in the current references is correct. An older NIST-hosted author manuscript is dated July 2015 and must not be used to overwrite that version date. The official v3 author order is Boyar, then Find; correcting citation order is bibliographic only.

## 6. Exact remaining gaps and recommended consolidation edits

There is no missing implication in the normalized C03, C04, C05, C06 dimension theorem, or C07 algebraic identities. Retain their written/finite status. The strongest safe C08 statement is the explicit blockwise equation above together with the one-bit overlap counterexamples. The algorithmic C07 statement has exactly the named efficient-evaluator hypothesis still open; finite interpolation and truth-table evaluation do not supply it.

Recommended narrow edits, without changing the mathematical program:

1. Replace C03's “one-packet bound gives `n−1`” with the explicit combined degree/alpha expression.
2. Define `M` and `T_rest` before the projection formulas; preserve `m≥2`, original-coordinate projection, and total-gate qualifications.
3. State `Q_2=P_2`, safety failure at `m=3`, and strict restored-cost separation from `m=4` if the visual presentation suggests separation at every parameter.
4. Replace the C06 scalar sentence by the historical PDF's “loses every singleton witness other than the selected witness,” or impose `m≥1`.
5. Preserve historical Proposition 7.5's explicitly represented characteristic-two fields of polynomial size and uniform exact evaluator on succinct verifier descriptions. Distinguish ordinary formal `z` variables from Boolean `w` reduction.
6. State C08 as `T_{S union U}(AB)=T_S(A)T_U(B)` for disjoint coordinate sets; include `z≠0` and `z^2≠z` for the displayed unequal values.
7. Keep finite ranges next to evidence claims: family masks through eight inputs; projection truth tables only through `m=4`; full three-bit GF16 root grids versus smaller extraction grid; no new Lean coverage for C03–C08.

The cheapest outstanding action is editorial incorporation of these exact hypotheses and boundary cases, followed by a notation/proofreading pass on the consolidated theorem statements. No new proof route, broad experiment, or novelty search is needed for this audit's closed scope.
