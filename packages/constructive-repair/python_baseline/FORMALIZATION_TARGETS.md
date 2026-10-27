# Lean formalization targets — proposed only, NOT COMPILED

**Tool availability check:** `lean` and `lake` executables were absent in the experiment environment. The following are proof obligations for a future portable Lean runner, not a claim of formal acceptance.

1. `free_minimal_repair_rank`: for a finite-dimensional vector space, correction map `D`, finite residual family `R`, and freely chosen `E`, prove `min_dim E = finrank (span (quotient.mk ∘ R))`. Avoid encoding the required existence as a structure field.
2. `finite_menu_repair_iff_span`: prove feasibility of all correction equations iff residual quotient span is included in the quotient span of the chosen candidate set; instantiate actual witnesses.
3. `menu_optimality_certificate`: prove a finite exhaustive enumeration returning the minimum of a declared nonnegative cost, with a predicate that rechecks every selected linear witness.
4. `conservation_no_go`: if all legal directions lie in `ker L` and some residual does not, prove no admissible correction exists.
5. `transport_obstruction_naturality`: adapt Paper III Theorem 21.3; transport residual and correction maps through a commuting square and identify induced cokernel map.
6. `transport_faithfulness_on_obstruction_span`: prove injectivity of induced cokernel map on required residual span is sufficient to infer source vanishing from target vanishing.
7. `graph_gluing_reuse`: reuse the existing Paper III/Paper XI holonomy theorems; do not rewrite proof with more generality than established.
8. `filtered_digit_correction`: ordinary Hensel lifting under derivative-unit and congruence hypotheses, or import corresponding Mathlib theorem. Do not treat a nonunit derivative as a universal obstruction.
9. `repair_contract_semantic`: explicitly declare source/target objects, domains, coefficient rings, invariants, and preservation assumptions. A purely algebraic field-level proof is not an implicit construction of an arithmetic representation.
10. `negative_controls`: where possible, formalize minimal counterexamples (coarse information loss, restricted candidate-menu failure, nonlinear first-order insufficiency) as counterexample theorems.

**Release rule:** A theorem is marked `LEAN_VERIFIED` only after the actual target source compiles with all concrete imports and the intended binders reviewed. Source presence or a textual theorem outline is not kernel acceptance.
