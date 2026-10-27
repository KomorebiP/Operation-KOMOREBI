# Independent audit: translated-norm source recovery

Normalized claim: on `E_Q = R × ∏p Z_p`, requiring every Boolean test `t=n OR (|t-n|∏p|x_p-n|_p=1)` cuts out exactly the diagonal `Z`. On `E_K = C × ∏v O_v` for `K=Q(i)`, the corresponding tests with squared complex absolute value and norm-normalized finite absolute values cut out exactly diagonal `Z[i]`. For the finite rational construction at supplied `B,S,N,L`, the protected fiber projects exactly onto the graph of the integers in `[-B,B]` modulo the requested `p^N`, `p∈S`. The declared contravariant Set diagrams realize these same fibers.

**Primary verdict: proved as written.** The three theorems, their stated Set-valued realizations, and the source-recovery consequence pass this audit. This verdict supplies no radical-dependent height estimate, link-preservation statement, historical novelty assertion, or formal verification.

## Exact input and review provenance

- Author file: `abc_work/komorebi_global_rr8/routes/translation_gluing/PROOF_NOTE.md`.
- Audited final SHA-256: `d2f4312b98f512ca33ce66fe670960a35300aff0547a755ca96ab995cd9ea0e7`.
- The initial read was SHA-256 `e6b7476104ccb2db669594eff6d250128f547cd6f4429c15b0a778da68270415`. After notification of the freeze, the entire final file was reread. The final version expressly identifies parallel paths in the view category, making its poset presentation explicit. The verdict refers only to the final hash above.
- Review type: independent delegated audit of the raw author note. The critical rational, Gaussian, finite-resolution, and variance implications were reconstructed rather than inferred from an author or neighboring reviewer verdict. Independence is procedural; it does not by itself prove correctness.
- `INPUTS.json` and `ROUTE_STATUS.json` were read to identify scope and recorded evidence. Their evidence labels were not used as proof. The note claims complete written elementary arguments, no load-bearing computation, no Lean run, and no novelty result.
- No author-file edits were made. No applicable ancestor `AGENTS.md` or `.mathbox` ledger was found, and no ledger was updated.

## Claim cards

1. **Theorem 1:** `∀x∈R×∏pZ_p`, all tests indexed by every `n∈Z` hold if and only if `∃m∈Z` with real component `m` and every local component the image of `m`. Products are infima of all finite subproducts; zero factors are allowed and produce zero. The test at a zero real difference is explicitly vacuous. Local coordinates are integral; this hypothesis is used to bound every factor by one and make each finite valuation nonnegative.
2. **Theorem 2:** the same equivalence with `Z[i]`, complex coordinate `z`, translations indexed by all Gaussian integers, and finite factors `N_v^{-ord_v}`. The infinite products use the same convention. The complex factor is `|z-a|^2`, and a rational translation `p^k` has complex factor `p^{2k}`. The sum above a rational prime is weighted by residue degrees, with ramification appearing in `ord_v(p)=e_v`.
3. **Theorem 3:** `∀B∈Z, B≥1`, every finite set of primes `S` (including the empty set), `∀N≥1`, and every chosen integer `L>N` with `2^L>D`, all diagonal residues of each `m∈M` pass every finite test. Every passing raw point has real coordinate such an `m` and the requested congruences at primes in `S`. The conclusion is the image under the stated projection, not equality of the entire raw fiber with the full diagonal residue family. The real coordinate and Boolean tests remain exact mathematical observations.
4. **View systems:** the indexing categories have arrows from observer objects toward `raw`, and `F` is contravariant. Consequently the actual maps point from raw values to observations. The infinite category includes all declared residue levels; the finite category is a finite star. The distinguished test values are all `true`, and no additive or module quotient is asserted.
5. **Arithmetic consequence:** applying the recovery theorem coordinatewise and imposing actual addition, positivity, and primitivity gives the usual rational integer source for ordinary ABC triples. The Gaussian assertion is Gaussian-integral source recovery. No quantitative ABC conclusion is asserted.

## Dependency graph

All load-bearing leaves are internal elementary arguments, local valuation conventions, or definitions. There is no numerical or source-dependent leaf.

`integral local coordinates` + `infimum product convention`
→ every finite factor belongs to `[0,1]`
→ a nearest nonintegral archimedean translate fails
→ the archimedean coordinate is `m` in the claimed integer lattice.

`positive product` + `every nonunit local factor ≤1/2`
→ no zero factors and only finitely many nonunit factors
→ an ordinary finite product of rational prime powers.

`rational test at m+p^k`
→ product `p^{-k}`
→ rational prime unique factorization forces local exponent `k` at `p`
→ `x_p-m∈p^kZ_p` for every `k`
→ `x_p=m`.

`Gaussian Euclidean division and norm/index identity`
→ Gaussian unique factorization and `N_v=p^{f_v}`, `Σ(v|p)e_vf_v=2`
→ product formula for nonzero Gaussian integers.

`Gaussian test at m+p^k`
→ product `p^{-2k}`
→ `Σ(v|p)f_v ord_v(x_v-m-p^k)=2k`
→ unequal valuations stabilize every nonmatching coordinate for large `k`
→ comparison of slopes forces all coordinates above `p` to match `m`.

`finite B,S,N,L construction`
→ all relevant nonzero integer differences have magnitude at most `D<2^L`
→ the diagonal valuations are untruncated and supported in `Q`
→ diagonal points pass; nearest-integer tests recover `m`
→ the test at `m+p^N` forces capped exponent `N` at `p`
→ the requested congruence and exact image statement.

`observer→raw` + `contravariance` + `compatible modular reductions`
→ well-typed functor on the path-quotiented category
→ coherent families are in bijection with raw points
→ protecting every test value means exactly the stated simultaneous tests.

## Obligation matrix

| Obligation | Result | Decisive check |
|---|---|---|
| Infinite products exist under the declared convention | Passed | The infimum is over a nonempty family in `[0,1]`; a zero factor makes the infimum zero. No order of enumeration is needed. |
| Positive product forces finite nonunit support | Passed | Arbitrarily many distinct nonunit factors produce finite subproducts bounded by `2^{-r}`. A positive infimum excludes this and excludes each zero factor. |
| Rational diagonal forward direction | Passed | Factorization of nonzero `m-n` gives the exact reciprocal finite product; `n=m` uses the first alternative. |
| Rational archimedean marking | Passed | For nonintegral `t`, a nearest integer has distance in `(0,1/2]`, so its product cannot equal one. |
| Rational prime-power extraction | Passed | Finite prime-power equality forces exponent exactly `k` at `p`; adding `p^k` gives divisibility of `x_p-m` by every power of `p`. |
| Zero-translate handling | Passed | No condition at `n=m` or `a=m` is used to match local coordinates. All forcing tests use nonzero `p^k`. |
| Gaussian arithmetic normalization | Passed | The complex square, residue degree `f_v`, and ramification `e_v` give `Σe_vf_v=2`; no exponent is lost in equations (6)–(8). |
| Gaussian nearest-lattice test | Passed | Coordinatewise rounding gives squared distance at most `1/2`; a non-Gaussian complex coordinate therefore fails a test. |
| Gaussian local recovery | Passed | Each nonmatching `x_v-m` has finite fixed valuation `A_v`. For `e_vk>A_v`, subtraction of `p^k` has valuation `A_v`; every such place removes a strictly positive term from the required slope two. |
| Gaussian place coverage | Passed | Every finite Gaussian prime lies above a rational prime, and only finitely many lie above any one `p`; the proof recovers each of them. |
| Finite parameter sets and bound | Passed | For `n=m'+p^N`, `|m-n|≤2B+p^N≤D`; for `n∈M`, the bound is `2B`. Every `p∈S` satisfies `p≤p^N≤D`, so the needed residue is present. |
| Finite diagonal tests and truncation | Passed | For nonzero difference, `q^{v_q(m-n)}≤|m-n|≤D<2^L≤q^L`, hence `v_q(m-n)<L`. All prime factors belong to `Q`. |
| Finite converse at requested primes | Passed | The finite product is `p^{-N}`; distinct prime exponents give `c_(p,n)=N`. In particular, reduction agrees with `n=m+p^N` modulo `p^N`. |
| Empty `S`, boundary values, endpoints | Passed | `{0}` makes `D` defined when `S=∅`; the congruence conclusion is then vacuous. `B=1`, `N=1`, negative `m`, and interval endpoints do not alter the nearest-integer or difference estimates. |
| Finite image surjectivity | Passed | Every `m∈M` has its actual diagonal residue family at all primes in `Q`; this supplies a preimage of each point in the stated finite-resolution graph. |
| Category variance and relations | Passed | `residue_j→residue_(j+1)` induces reduction `Z/p^(j+1)→Z/p^j`; `residue_j→local_p` induces `Z_p→Z/p^j`. All parallel-path equalities are ordinary reduction compatibility. |
| Coherent-extension fiber | Passed | `raw` is terminal in the indexing category and initial in its opposite. A coherent family is uniquely determined by its raw coordinate; protecting tests imposes precisely their preimage conditions. |
| Multiplicative-reduct or link preservation | Out of scope | The tests explicitly use shared additive translations. The note does not claim they follow from multiplication or are preserved by a proposed link. |
| Radical-controlled height, optimal test cost, unrestricted ABC | Out of scope | `B` is supplied and the note supplies no bound for it from radical data; all genuine diagonal triples already pass the tests. |
| Lean or numerical certification | Out of scope | None is claimed or used. |

## Fresh derivation of the critical implications

### Rational extraction without a common-zero axiom

Suppose the tests hold. The nearest-integer argument first forces `t=m∈Z`. For fixed `p,k≥1`, the test at `n=m+p^k` has positive archimedean factor `p^k`, so its finite product is the positive number `p^{-k}`. After discarding factors equal to one, the product is finite. Write it as `∏q q^{-b_q}` with each `b_q` a finite nonnegative integer. Multiplying denominators gives `∏q q^{b_q}=p^k`; hence `b_p=k`. Thus `x_p-m-p^k∈p^kZ_p`, and adding `p^k` shows `x_p-m∈p^kZ_p`. This conclusion holds for every `k`, whose ideals have zero intersection in `Z_p`. It recovers the common zero after the fact; it does not assume that zero condition in the test definition.

### Gaussian residue degree and ramification check

Gaussian division is obtained by rounding `α/β` in both real coordinates. The remainder has norm at most `N(β)/2<N(β)` when `β≠0`. The Euclidean gcd identity gives primality of irreducibles and unique factorization. For nonzero `u+iv`, multiplication on the rank-two abelian group `Z[i]` has determinant `u^2+v^2`, so the quotient index equals its norm. A Gaussian prime quotient is therefore a finite domain, hence a finite field. Its characteristic is a rational prime `p`, and, because `Z[i]/(p)` has dimension two over `F_p`, its residue degree is one or two. Factoring `p` in the Gaussian UFD and taking norms gives `p^2=∏(v|p)(p^{f_v})^{e_v}` and therefore `Σe_vf_v=2`. Factoring any nonzero Gaussian integer likewise proves its product formula with exactly the note's squared complex factor.

After recovery of `z=m`, fix `p`. Put `y_v=x_v-m`. For `v|p`, either `y_v=0`, in which case `ord_v(y_v-p^k)=e_vk`, or `A_v=ord_v(y_v)<∞`. In the second case, once `e_vk>A_v`, the unequal-valuation identity gives `ord_v(y_v-p^k)=A_v`. There are finitely many `v|p`, so a common threshold works. Let `J` be the nonmatching places. Equation (7) becomes

`2k = k(2-Σ(v∈J)e_vf_v) + Σ(v∈J)f_vA_v`.

If `J` is nonempty, its sum of positive integers `e_vf_v` is positive. Subtracting this equality at consecutive sufficiently large `k` gives `2=2-Σ(v∈J)e_vf_v`, a contradiction. This avoids treating the rational prime exponents as individual Gaussian exponents: at a split prime, equation (7) first gives only their weighted sum, and the stabilization argument is essential.

Concrete normalization checks are `2=-i(1+i)^2` with `(e,f)=(2,1)`, the prime `3` with `(e,f)=(1,2)`, and `5=(2+i)(2-i)` with two pairs `(1,1)`. In each case the total slope is two. These are checks on normalization; the preceding argument handles all rational primes without relying on a classification by congruence class.

### Finite-resolution recovery

For a diagonal residue family `r_q=m mod q^L`, reduction determines the capped valuation as `min(v_q(m-n),L)`. Every nonzero relevant difference satisfies `|m-n|<2^L≤q^L`, making this exactly the untruncated valuation. Its prime support is contained in `Q`, so the product equals `|m-n|^{-1}`. Conversely, for a passing point, the real interval and the tests indexed by `M` force `t=m∈M`. The test at `m+p^N` then gives a finite product with denominator `p^N`. Unique factorization forces the `p`-exponent to be `N`, so the residue has the claimed digits. The theorem does not require, or derive, all other digits of every residue from this argument.

### Diagram and fiber reconstruction

Let `C` be the category specified in Section 2 after identifying parallel paths. Its generating arrows are acyclic and determine a partial order. A contravariant functor on `C` is a covariant functor on `C^op`; `raw` is initial in `C^op`. Given any raw element `x`, its projections, reductions, and Boolean values define a coherent family because reductions commute. Conversely, any coherent family must have precisely these values, by the unique morphisms from `raw` in `C^op`. Thus evaluation at raw identifies the full coherent-family set with `F(raw)`. Taking the preimage of `true` at all test objects gives exactly the set used in the theorems. The same argument applies to the Gaussian residue powers and to the finite star, with the finite conclusion taken only after the stated projection.

## Source and computation checks

No external global-field recognition result is needed. The only arithmetic ingredients are integer unique factorization, the explicitly reconstructed Gaussian Euclidean/UFD and norm argument, and the standard definitions of the integral discrete valuations and separated local integer rings. The product formulas used for integer and Gaussian-integer translates follow directly from their factorizations. There is no unchecked source-dependent implication and no load-bearing finite search to audit.

Commands used included `sha256sum`, a full `cat` and numbered read of the frozen note, reads of its input/status metadata, and ancestor checks for `AGENTS.md` and `.mathbox`. No executable test was substituted for a universal proof. The accompanying `.inputs.sha256` records the load-bearing author note; metadata is not part of the mathematical dependency set.

## Remaining gap, strongest safe statement, and next check

There is no missing implication for Theorems 1–3 or their declared Set-valued fiber interpretations. The strongest safe conclusion is exactly the full-family diagonal recovery over `Q` and `Q(i)` and the supplied-budget finite-resolution image theorem, with their stated integrality and normalization hypotheses.

The broader height obligation remains open: source recovery alone does not give `log c≤(1+ε)log rad(abc)+C_ε` with a constant independent of the triple. The cheapest relevant next mathematical check is to demand an explicit radical-dependent bound on the compatibility resolution or observer cost before treating this route as a height estimate. Such a bound is not a consequence of the audited note.
