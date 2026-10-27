# Large Signal Model Lean 0.10.0 — P45 proof guide

**Scope:** P45, Rational finite-certificate search, Foundations 1.0.0, 49. Searching for a domain from observable operators. This guide explains Block 10; the full 0.9.0 guide and archive remain under `history/`.

## The exact promise

Input consists of finite rational matrices $B_s$, a rational mass row $\lambda$, and a rational initial vector $z_0$, under exact per-action mass identities. If P39 has a rational normalized full-row-rank generator matrix $V$, the search eventually returns a valid certificate. The nonnegative branch lifts $A_s$ and initial coefficients $\alpha_0$ in that assumed certificate can be real. They are not silently assumed rational.

The conclusion is conditional termination and soundness. It does not assert that every valid process has a rational polyhedral certificate, that bounded search decides nonexistence, or that the exhaustive search is practical. No strict positivity or strict margin is required. The hypotheses of the later curved-certificate P77 are not imported into P45.

## Dependency chain

1. `rational_feasible`: a real feasible finite system of weak rational linear inequalities has a rational feasible point.
2. `rational_nonnegative_solution` and `rational_solution`: specialize to nonnegative and unrestricted solutions of rational equations.
3. `rational_right_inverse`: real surjectivity of rational $V$ supplies a rational $R$ with $VR=I$.
4. `rationalize_certificate`: rationalizes each branch-lift column and the initial coefficient vector while keeping the given $V$.
5. `Candidate`, `candidateEncodable`, `Valid`, `checkCode`, `search`: actual computable representations, decoder, exact checker and finite-fuel search.
6. `rational_finite_certificate_search`: some finite fuel returns an accepted witness under precisely the rational-generator hypothesis.
7. `accepted_probability_domain`, `accepted_all_word_probabilities`: connect acceptance to the inherited P39 cone and positive-instrument results.

## Rational feasibility, including faces

`RationalFeasibility.lean` works with any finite row index and $n$ unknowns. The system is

$$\sum_{j<n} a_{ij}x_j\le b_i,\qquad a_{ij},b_i\in\mathbb Q.$$

Induct on $n$. For $n=0$, the same constant inequalities hold over both fields. At a successor step write the leading coefficient as $c_i$, the remaining row as $d_i$, and the first unknown as $t$. Rows with $c_i=0$ survive unchanged. Pair every negative row $i$ with every positive row $k$, divide by $-c_i$ and $c_k$, and add to cancel $t$. Inactive row and pair slots are filled by $0\le0$, so the reduced index remains an explicit finite sum/product type.

A real feasible point satisfies the reduced system. The induction hypothesis supplies a rational tail $y$. Set $r_i=b_i-d_i y$. The paired inequalities say

$$r_i/c_i\le r_k/c_k\quad(c_i<0<c_k).$$

Choose the greatest lower bound from the finite set of active rational lower endpoints; if no lower endpoint exists, choose the least upper endpoint; if neither exists, choose zero. The auxiliary `rational_interval` verifies the closed-interval step. There is no density approximation and no loss of an equality face. The selected rational first coordinate and tail satisfy every original row.

To encode $Vx=z$ and $x\ge0$, use both $Vx\le z$ and $-Vx\le-z$, with $-x_j\le0$. For unrestricted equations omit the sign rows. These are internally proved reductions; no external rational-LP completeness theorem is assumed.

## Rationalizing the actual P39 witness

For every symbol and generator column, the equations $Vq=B_sv_j$ have a nonnegative real solution from the supplied lift. Rational nonnegative feasibility gives a rational solution. Assemble those columns into rational branch lifts.

For the initial vector, append the row of ones to $V$ and append $1$ to $z_0$. Solving that augmented system preserves both $V\alpha=z_0$ and $\sum_j\alpha_j=1$, including zero coefficients.

Real full row rank is represented by surjectivity of the real matrix linear map. Solve $Vq=e_j$ for each rational standard basis vector using unrestricted rational feasibility. The columns give the rational right inverse $R$. Thus requiring $R$ in the enumerated witness does not strengthen the completeness hypothesis.

## What is enumerated and checked

`Candidate r s` is a dependent pair of a natural width $m$ and four rational data blocks:

- $V\in\mathbb Q^{r\times m}$;
- $A_t\in\mathbb Q^{m\times m}$ for each of the $s$ symbols;
- $\alpha\in\mathbb Q^m$;
- $R\in\mathbb Q^{m\times r}$.

The computable `Encodable` instance uses the standard exact rational, finite-vector, product and dependent-pair encodings. `Encodable.decode (Encodable.encode c) = some c` supplies exhaustive coverage of every width and all entries. This is dovetailing over the whole witness, not an inner unbounded search that could block on one infeasible generator matrix.

`Valid` checks exactly

$$\lambda V=\mathbf1^\top,\quad VR=I,\quad B_tV=VA_t,\quad A_t\ge0,$$
$$\alpha\ge0,\quad \mathbf1^\top\alpha=1,\quad V\alpha=z_0.$$

Its decision procedure uses rational arithmetic and finite equalities/sign tests. The supplied model's mass identities are separate input hypotheses for the probability conclusion, as in P45. `rational_mass_identity` explicitly converts the rational column identities to P39's real functional identity.

`checkCode k` decodes one candidate and filters it by `Valid`. `search N` inspects natural codes below $N$, returning the first accepted candidate. Zero fuel returns `none`. Once it returns a candidate, increasing fuel preserves that exact result. For every valid candidate $c$, fuel $\operatorname{encode}(c)+1$ has found some valid candidate, possibly an earlier one. These are proved universal statements. The procedure is exposed as a terminating finite-fuel function; increasing fuel implements the unbounded semidecision procedure. No nonterminating Lean definition or classical choice is hidden in the executable search.

`none` means only “no accepted code in this prefix.” `search_no_certificate` proves the valid forward implication that absence of every rational certificate makes every prefix fail; the converse is not inferred from one prefix.

## Semantic soundness

Cast accepted rational entries to real entries. Matrix multiplication commutes with that cast. $VR=I$ gives real surjectivity. Normalization becomes `readout l ∘ V = mass`; intertwining becomes equality of linear-map compositions. Initial coefficients become a real prior and synthesize the supplied initial state.

Apply the inherited P39 results to obtain a closed, pointed, generating cone with strictly positive mass on nonzero elements, initial-state membership, and invariance under every branch. Exact per-action mass identities produce a nonnegative instrument and word probabilities in $[0,1]$ at every finite depth. An arbitrary action/observation-to-symbol coding is supported, with a finite observation alphabet; no injectivity of that coding is needed for the stated mass identity.

The mass readout and semantic real maps are noncomputable mathematical objects. The rational candidate decoder, checker and finite-fuel search are computable. Classical choice occurs in the existence proofs used to establish eventual success, not as an implementation of the search.

## Boundary examples and executable evidence

Eight named example theorems cover a scalar identity certificate, an allowed zero branch, rejection of a negative branch lift, rejection of a rank-deficient generator, exact decoder/checker recovery of an encoded witness, failure of zero fuel despite a valid certificate, a rational solution on a boundary face, and the distinction between total mass and branch positivity.

`scripts/RunRationalSearch.lean` executes five checks. Expected outputs are `true, true, false, true, false`: accept identity; accept zero branch; reject signed lift; decode/check the identity candidate at its exact code; find no accepted code in the first 64 codes. The last result is deliberately not a nonexistence claim. The executable outputs are checked by both complete verification runs. They do not claim a practical search benchmark or a bound on witness code size.

Four new isolated negative controls try to turn bounded failure into impossibility, require strictly positive branch lifts, accept a signed lift, or omit the rank requirement. The verifier requires real proof diagnostics, not missing imports or timeouts.

## Development repairs and provenance

The first broad `Mathlib` import was narrowed to explicit dependencies. Elimination division identities and sign orientations were repaired; the pinned release's deprecated `if_pos` name was replaced. Dependent witness unfolding and an explicit rational Boolean order decision were needed to synthesize the computable checker. Direct kernel reduction of the matrix examples stalled on opaque arithmetic; their proofs use ordinary exact simplification, while compiled execution is checked separately. The runtime example needed explicit dimensions at the untyped natural-code call. One premature example invocation failed because its imported module had not yet compiled; it is a development failure, not a negative-control success.

The first cumulative preflight rejected the ordinary English word “admit” in a comment because it matched the prohibited-token scanner; the comment was changed without changing the theorem. A metadata-script replacement briefly turned the inherited file count 74 into 44; the consistency gate caught it, and it was repaired. All retained compiler diagnostics and snapshots distinguish failed development attempts from accepted proof evidence.

The predecessor roadmap's standalone `remaining_count` was stale at 57 even though its lists and coverage correctly described 52. This release sets it to the new exact value 51 and adds a gate comparing the field with the exhaustive list. Historical files and predecessor ZIP remain unchanged.

## Reproducibility and limits

Use `README.md` for the pinned verification commands. Counts are source inventory metrics, not mathematical novelty or difficulty measures. Self-review plus Lean kernel acceptance is not an independent referee, a second proof assistant or an exhaustive replay of all upstream Mathlib. The archive manifest and external fresh-extraction receipt identify the delivered bytes. The original source and proof register are not edited by this formalization.
