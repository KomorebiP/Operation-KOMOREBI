# Block 04 — Quantitative approximate sufficiency

**Komorebi P. · Sufficient Resolution v0.4.0 · 13 September 2026**

This block adds 82 theorem declarations across six production modules. Counts include
helper identities and exact examples. Historical priority or novelty is not asserted.

## 1. Contract and conventions

Let `q : X → Z` be a linear state representation, `T_i : X → X` the true operations,
`U_i : Z → Z` the candidate reduced operations, and `O : X → Y`, `V : Z → Y` the two
readouts. Words are chronological: `i :: w` applies `T_i` first and then `w`.
For `w = [i_1,...,i_n]`, therefore `T_w = T_{i_n} ... T_{i_1}`.

The algebraic identities hold for commutative-ring modules. Quantitative results use
continuous linear maps over a nontrivially normed field. Neither finite dimension,
completeness, a finite alphabet, invertibility nor surjectivity of q is assumed.
All norms are whole-map operator norms. A residual measured on finitely many sample
states does not satisfy a whole-map norm hypothesis merely by passing those samples.

## 2. Exact error transport

Define

    δ_i = q T_i − U_i q,
    E_w = q T_w − U_w q.

Then

    E_[] = 0,
    E_(i::w) = E_w T_i + U_w δ_i,
    E_(u++v) = E_v T_u + U_v E_u.

Equivalently,

    E_w = Σ_(j=1..n) U_(i_(j+1)..i_n) δ_(i_j) T_(i_1..i_(j−1)).

The source implements this finite sum through `transportTerms`, with exactly one
term for each letter, avoiding partial list indexing and default letters.

Checked declarations in `ApproximateAlgebra`:
- `wordDefect_cons`, `wordDefect_append`, `wordDefect_eq_sum`.
- `transportTerms_length`, `wordDefect_eq_zero_of_steps`.
- `output_defect_decomposition`, `wordDefect_two_stage`.

The analytic word and defect are explicitly identified with the existing algebraic
word and defect by `ApproximateBounds.word_toLinearMap` and
`ApproximateBounds.wordError_toLinearMap`.

## 3. Heterogeneous, operation-specific bounds

Suppose each letter has nonnegative bounds

    ||T_i|| ≤ a_i,   ||U_i|| ≤ b_i,   ||δ_i|| ≤ ε_i.

Define A_w and B_w as the products of a_i and b_i along the word, with empty product 1.
The defect budget satisfies

    D_[] = 0,
    D_(i::w) = D_w a_i + B_w ε_i.

Then

    ||T_w|| ≤ A_w,
    ||U_w|| ≤ B_w,
    ||E_w|| ≤ D_w.

The budget itself satisfies the exact concatenation identity

    D_(u++v) = D_v A_u + B_v D_u.

If η ≥ ||O − Vq||, then

    ||O T_w − V U_w q|| ≤ η A_w + ||V|| D_w.

The two terms represent readout mismatch and propagated dynamical mismatch. Neither
is silently dropped. `norm_state_error_le` also covers arbitrary reduced initial
state z:

    ||q T_w x − U_w z|| ≤ D_w ||x|| + B_w ||qx − z||.

Main declarations in `ApproximateBounds`:
`norm_wordError_le_budget`, `norm_outputError_le`, `norm_state_error_le`,
`budget_append`, `outputError_decomposition`.

## 4. Uniform growth and the exact two-rate response

For nonnegative uniform bounds a,b,ε, let

    H_0(a,b) = 0,
    H_(n+1)(a,b) = a H_n(a,b) + b^n.

The source proves

    H_n = Σ_(j=0..n−1) a^j b^(n−1−j),
    (a−b) H_n = a^n − b^n,
    H_n(a,b) = H_n(b,a),
    H_(n+1) = b H_n + a^n.

When a ≠ b,

    H_n = (a^n − b^n)/(a−b).

For equal rates, the denominator-free formula is

    H_(n+1)(a,a) = (n+1) a^n.

These formulas include zero rates. The empty-word case is handled separately as H_0=0.

The main all-word error estimate, n = length(w), is

    ||E_w|| ≤ ε H_n(a,b),
    ||O T_w − V U_w q|| ≤ η a^n + ||V|| ε H_n(a,b).

Checked declarations:
- `ScalarBudgets.response_eq_sum`, `response_mul_sub`, `response_of_ne`.
- `ScalarBudgets.response_same_succ`, `response_nonexpansive`, `response_uniform`.
- `StableApproximation.norm_wordError_uniform`, `norm_outputError_uniform`.

## 5. Nonexpansive and contractive regimes

If all true and reduced operations have norm at most 1,

    ||E_w|| ≤ n ε,
    ||O T_w − V U_w q|| ≤ η + ||V|| n ε.

This is an upper bound, not a claim that every nonexpansive model has unbounded error.

If the true operations have norm at most 1 and all reduced operations have norm at
most b, where 0 ≤ b < 1, then the bound is uniform over every finite word:

    ||E_w|| ≤ ε/(1−b),
    ||O T_w − V U_w q|| ≤ η + ||V|| ε/(1−b).

For arbitrary x and initial reduced state z,

    ||O T_w x − V U_w z||
      ≤ (η + ||V|| ε/(1−b)) ||x|| + ||V|| b^n ||qx−z||.

Thus initialization error has an explicit b^n factor. The theorem is not restricted
to one repeated operation. A common operator-norm bound for the allowed operations
is the hypothesis; individual spectral-radius estimates are not substituted for it.

Checked declarations in `StableApproximation`:
`norm_wordError_nonexpansive`, `norm_outputError_nonexpansive`,
`norm_wordError_contractive`, `norm_outputError_contractive`,
`norm_output_initial_contractive`, `norm_wordError_same_rate`.

## 6. Approximate behavioral sufficiency

If qx=qy and ||O T_w − V U_w q|| ≤ E, then

    ||O T_w x − O T_w y|| ≤ E ||x−y||.

This does not declare a new approximate minimal quotient. It bounds the future
observational effect of distinctions discarded by a given representation q.

Checked declaration: `StableApproximation.same_coarse_future_bound`.

## 7. Multilevel models and conditioning

For a second representation p : Z → W and operations S_i,

    E_w(pq;T,S) = p E_w(q;T,U) + E_w(p;U,S) q.

Hence stage errors ε1,ε2 imply

    ||E_w(pq;T,S)|| ≤ ||p|| ε1 + ε2 ||q||.

Readout mismatches compose as

    O − Hpq = (O−Vq) + (V−Hp)q.

These are proved at whole-word and one-step level, without an orthogonality assumption.

For a split coordinate embedding S : Z → W, J : W → Z with JS=id, let

    q' = Sq,   U'_i = S U_i J,   V' = VJ.

Then

    E'_w = S E_w,
    ||E'_w|| ≤ ||S|| ||E_w||,
    ||U'_i|| ≤ ||S|| ||U_i|| ||J||,
    O T_w − V' U'_w q' = O T_w − V U_w q.

The actual represented output is unchanged, while a norm-based certificate may
worsen under poorly conditioned coordinates. Surjectivity of S onto W is not
assumed; the statement concerns the embedded states.

Main declarations in `ApproximateComposition`:
`wordError_two_stage`, `norm_wordError_two_stage`, `norm_stepError_two_stage`,
`norm_readout_two_stage`, `reencode_wordError`, `norm_reencode`, `reencode_outputError`.

## 8. Exact sharpness and failure boundary

For real scalar maps T=a, U=b, q=1 with a≥b≥0,

    ||E_w|| = (a−b) H_n(a,b).

Thus the general two-rate bound is attained by actual operators, not just a scalar
majorant unrelated to a realizable model.

For every ε>0, take T=1+ε, U=1, q=1. Lean proves

    ||δ|| = ε,
    ||E_n|| = (1+ε)^n − 1 ≥ n ε,
    for every B ∈ R, there exists n with ||E_n|| > B.

This refutes uniform error control from one-step smallness alone. It does not refute
the stability theorem: this true operator violates its nonexpansive hypothesis.

For 0≤b≤1, the stable example T=1,U=b satisfies ||E_n||=1−b^n exactly.

Checked declarations in `ApproximateExamples`:
`sharp_response`, `unstable_step_exact`, `unstable_word_lower`,
`unstable_error_unbounded`, `stable_scalar_exact`.

## 9. Executable rational controls

    python scripts/approximate_certificate.py \
      --input examples/approximate_model_input.json \
      --output bounds.json

The evaluator uses exact rational matrices and the induced infinity norm, reports
actual finite-word discrepancies and certified envelope values, and rejects floats
and invalid shapes. It does not infer a whole-map norm from sampled trajectories.

Controls passed 7,509 exact assertions across 30 systems and 370 words, plus ten
rejected invalid/underestimated inputs. The suite compares the recursive envelope
against independently assembled prefix/injection/suffix sums, checks noncommuting
word order, zero dimensions, multilevel error, initial mismatch, re-encoding and
scalar identities. General bounds are Lean proofs; the Python executable is not
formally verified or extracted from Lean.

## 10. Scope still open

No continuous-time memory identity, noisy-data identification theorem, approximate
minimum-dimension theorem, automatically discovered common stable norm, positive
realization theorem, nonlinear descent theorem, or arithmetic existence theorem is
established here. Known continuous linear operators and explicit whole-map norm
hypotheses are the current contract.

The analytic contracts require a bounded realization of q,T,U,O,V. They do not
automatically put a canonical norm on every prior abstract algebraic quotient.
