# Lean guide — Information Realization v0.4.0

## 1. Read the definitions before the theorem names

`Sufficient r f` means that two states with the same observation have the same task answer. `Decodes r f g` means `g (r x) = f x` on every state. `Repair r f u h g` means `g (r x, h (u x)) = f x` on every state: the encoder h receives only u(x).

These are pointwise statements, not statements about an unstated prior or high-probability support. An image decoder is defined only on actually attainable observations. Extending it to the full codomain explicitly assumes a nonempty task type, avoiding the empty-domain/codomain gap.

## 2. Recovery and access

`KomorebiInformation.sufficient_iff_image_decoder` is the basic factorization equivalence. `sufficient_iff_no_obstruction` identifies exactly when no colliding pair with different task answers exists. `inaccessible_pair_rejects_every_code` says a joint observation/access collision defeats every permitted encoder and decoder.

`repair_alphabet_lower_bound` accepts task-distinct representatives from one observation fiber. It constructs an injection from these representatives into the message alphabet. The only finiteness needed by that statement is finiteness of the representative and message types.

## 3. Linear feasibility and optimality

The namespace `KomorebiInformation.Linear` uses genuine Mathlib `LinearMap`s, submodules, kernels, ranges, quotients, dimension, and finite cardinality.

`exists_linear_decoder_iff_kernel` proves that a task factors linearly through an observation iff it vanishes on the observation kernel. The proof uses the first isomorphism theorem and extension from a subspace. It does not require a finite-dimensional ambient space for existence.

`access_feasibility` specializes this to the stacked observation and accessible helper data. `arbitrary_repair_implies_kernel` proves that even a nonlinear encoding scheme cannot circumvent that kernel condition. `not_feasible_iff_witness` supplies an explicit nonzero-task vector in the joint kernel when inclusion fails.

`ObstructionSpace R F` is `(F.domRestrict R.ker).range`, which is the genuine subspace F(ker R). `fiber_task_difference_iff` proves that task answers in the fiber through x0 differ from F(x0) by exactly that space.

`optimal_obstruction_space_repair` proves existence of H and G with the following fully typed shape:

```lean
H : E →ₗ[K] ObstructionSpace R F
G : O × ObstructionSpace R F →ₗ[K] Y
G.comp (R.prod (H.comp U)) = F
```

H is obtained by factoring F restricted to ker R through U restricted to ker R, with codomain restricted to F(ker R), then extending to E. The difference F − inclusion ∘ H ∘ U vanishes on ker R and therefore factors through R. The decoder adds these two contributions.

`obstruction_card_le_any_repair` compares this attainable alphabet with **every** finite message type and every nonlinear helper/decoder pair. `obstruction_space_card` turns its cardinality into q^d. `obstruction_finrank_eq_rank_increment` proves d equals the range-rank increment of the stacked map, using rank-nullity and an explicit kernel equivalence.

This gives the exact access-aware linear theorem at the level of linear maps and subspaces. An explicit coordinate-basis API producing a matrix with exactly d rows is not included in this block. A d-dimensional subspace is used as the optimal message type instead. Its cardinality and dimension are kernel-checked, not inferred from Python.

The existence proof uses classical subspace extension. It is not a verification that the Python row-reduction program computes H correctly. `repair_certificate_sound` proves what a correctly typed H,G equality implies, but a parser/exporter taking every Python matrix certificate into that type is still a separate obligation.

## 4. Canonical predictive information

`Predictive.run T w x` applies a list of actions in chronological order. `OperationalEq T r x y` means every finite action word yields the same observation for x and y. `InfoSpace T r` is the actual quotient by that equivalence relation, not a postulated abstract type.

The quotient's observation and action are constructed by `Quotient.lift` and `Quotient.map`. Their well-definedness is proved from operational equivalence. Any other representation with an observation decoder and an induced map for each action refines this quotient; `canonical_factorization` supplies the factor map on its image.

The universal statement covers arbitrary finite action words. It does not establish the runtime or finite stabilization bound of the Python partition/subspace closure algorithms. The existing word simulation lemmas are the foundation for that next port.

## 5. Haar: exact finite example and symbolic generalization

The source is `Fin 4 → K`. Observation, detail, shift, one-coordinate message, and decoder are explicitly defined. The general field hypothesis is supplied at the namespace level, and inverse formulas additionally require `(2 : K) ≠ 0`.

For sums s0,s1 and details d0,d1, the supplement is c = d1−d0. The decoder returns `(s0+s1+c)/2` and `(s0+s1−c)/2`. `next_output_repair` proves this symbolic identity by field/ring normalization, producing proof terms checked by Lean.

`closed` stores (s0,s1,c), and `closedStep` updates it by

```
((s0+s1+c)/2, (s0+s1-c)/2, s1-s0).
```

`closed_semiconjugacy` proves closure. `coarse_predicts_all_times` quantifies over every n and every input state. `predictive_is_not_source_reconstruction` proves failure of source recovery using the nonzero invisible direction (1,−1,1,−1).

`next_output_alphabet_lower_bound` injects field elements into every correct message alphabet using the family (0,0,t,−t), whose initial sums agree and whose next outputs differ. Together with `helper_repair_correct`, it proves the one-field-coordinate message is optimal in the finite-field case.

The concrete GF(5) calculation and the GF(2) collision use ordinary `decide`, not `native_decide`. The first negative mutated-decoder attempt stalled at a field-inverse decision instance. The final fixture uses the explicit inverse 3 in GF(5), and the compiler reports that the altered formula is false.

## 6. Replaying and auditing

Run `tools/verify.py --kit ...`. `lean/Audit.lean` contains a live `#check` and `#print axioms` for every named theorem. The verifier rejects missing audit coverage and every axiom outside its three-name allowlist. It also independently scans production source for proof escapes.

The compiler binary and imported Mathlib cache come from the pinned restored toolchain. They were not independently rebuilt or verified by an external Lean kernel in this block. This is normal kernel-checked Lean verification with disclosed dependencies, not a new proof of the compiler's own correctness.
