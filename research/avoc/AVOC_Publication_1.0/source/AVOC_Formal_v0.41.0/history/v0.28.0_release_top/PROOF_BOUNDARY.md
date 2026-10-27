# AVOC v0.28.0 — exact scope

## Proved in the new block

- Ring-valued dimension-typed affine coefficient semantics, composition, identity and sum.
- Equality of affine coefficients iff equality on all inputs.
- Complete zero-and-basis probe test; a mismatching affine pair differs on one of these designated probes.
- Exact normalization of all programs built from declared affine primitives, identity, sequencing and sum.
- Executable coefficient checker soundness/completeness for those programs.
- Equivalence and additive-cost monotonicity under the supplied typed one-hole contexts.
- A dimension-indexed weighted semantic lower-certificate theorem; an attaining witness is globally minimum under its certificate hypotheses.
- Dense fusion correctness; a per-call tariff guard never selects a more expensive execution.
- Compile-once/deploy-many comparison conditional on the declared lifecycle inequality.
- Exact GF(5) positive and negative examples, including zero dimensions, omitted-zero-probe failure, nonlinear counterexample, and harmful dense fusion.
- A decoded `Compiled` object has both an actual parse witness and an all-input signature correctness proof.

## Not claimed

1. No general cheapest affine factorization, optimal sparse/dense decision algorithm, optimal circuit/DAG implementation, or tight all-affine cost table is supplied. Canonical coefficients are exact semantics, not a minimum-cost execution plan.
2. The typed lower-certificate theorem requires its lower inequalities and an attaining witness. It does not inherit the Bool3 finite global optimum merely by changing the semantic domain.
3. The runtime uses exact GF(5); it does not compare floating-point implementations, effectful programs, nonlinear operations, or arbitrary Lean/Python/machine code. The mathematical theorem is broader: any ring and arbitrary natural dimensions.
4. Scalar-operation tariffs are declared dense-algorithm models. They exclude allocation, copying, sparse shortcuts, rational/integer bit complexity, parsing, table comparisons, checking, source hashes, process startup, IO and physical runtime. A lower tariff is not a measured speedup.
5. Compilation is not free. The analyzer computes normal forms even when its eventual fusion recommendation is negative. This release does not refund that exploration cost or prove net-positive optimization search.
6. The wrapper is read-only. No persistent affine library import, durable promotion, candidate generation, general live research backend or multi-generation improvement experiment is added.
7. Runtime parser shape checks and dependent construction are executed and tested. The source theorem concerns the decoded AST; complete Python/JSON/filesystem refinement and semantic correspondence to natural-language intent remain outside scope.
8. Finite testing validates the tested implementation paths. General affine and typed-program conclusions are separately proved in Lean, not inferred from random tests.
9. Mathlib matrix identities are existing mathematics and dependencies. No historical novelty claim is made for affine composition, basis determination or matrix normalization.
10. Lean's kernel, compiler/interpreter, installed Std/mathlib caches, Python and the host remain trusted. The caches were pinned, not rebuilt from all sources. The previous runtime, crash, store and payment suites are retained as historical evidence and were not rerun.
11. The independent scan distinguishes the legacy `.admit` action constructor and `| admit =>` cases from the forbidden proof tactic. The full per-theorem axiom audit supplies a separate check.

## Fresh verification

135/135 inherited non-audit modules byte-identical; 156/156 final local targets passed; 1,499/1,499 axiom reports; 75/75 substantive negative rejections (one type-level test); 1,137 executed exact-field test requests. No new project axiom, proof placeholder, native-evaluation axiom or unsafe declaration was found.
