# Claim register

C01–C08 remain the closed mathematical scope in version 1.2.0. C01, the maintained NCT degree dependency, and the C02 lower-bound component receive formal verification. The rest of C02 is not marked Lean proved. Older archives are historical evidence, not automatic additions to this register. “Written” means a supplied self-reviewed argument; “finite” means execution in the exact range stated.

## C01 — Exact cut-comparison cover

**Statement.** For every restored classical oracle and every cut, H_i<=f and OR_i H_i=f.

**Proof.** [FOUNDATIONS.md](FOUNDATIONS.md), section F2; [Lean Block 01](formalization/LEAN_BLOCK_01.md). **Status:** LEAN, FINITE and WRITTEN.

**Lean.** `CircuitObstructions.complete_safe_cover` and `CircuitObstructions.canonical_complete_safe_cover`; pinned toolchain 4.34.0-rc2. Supporting declarations are not additional maintained claim groups.

**Computation.** All 276 functions through three inputs, with explicitly constructed restored circuits.

**Boundary.** No universal circuit-size lower bound follows solely from packet count.

## C02 — Complete-cover lower bound and dual certificates

**Statement.** T>=max(0,deg(f)-1,2 beta*(f)-3), with exact evaluation-span characterization of beta_v.

**Proof.** [THEORY.md](THEORY.md), section 1; [Lean Block 02](formalization/LEAN_BLOCK_02.md). **Status:** PARTIAL LEAN, FINITE and WRITTEN.

**Lean subset.** `restored_degree_and_cover_bound` proves a degree-(T+1) polynomial certificate and `2 * betaStar f <= T+3`. Existence and least-bound properties of beta and betaStar, and `betaStar<=n`, are proved. The evaluation-span dual, affine input invariance, and general monotone ideal are not formalized.

**Computation.** Full four-input profile table; independent rank checks only on the documented 765 cases.

**Boundary.** beta*<=n is itself formalized. This does not yield a superpolynomial lower bound; the dual-certificate claims keep their distinct status.

## C03 — Unbalanced-OR calibration

**Statement.** For k>=2, F_k=ab OR product(z_i): max affine alpha_1=3 and beta*=k+1.

**Proof.** [THEORY.md](THEORY.md), section 2. **Status:** FINITE and WRITTEN.

**Computation.** Full designated family tables through nine inputs; all affine masks only through eight.

**Boundary.** Easy linear-size family; no exact optimum claimed when lower and upper bounds differ.

## C04 — Optimal small restored oracles

**Statement.** The complete-cover bound is attained by explicit classical implementations for all functions on one, two, or three inputs.

**Proof.** [THEORY.md](THEORY.md), section 2. **Status:** FINITE and WRITTEN.

**Computation.** All 276 functions; 28 zero-, 120 one-, and 128 three-Toffoli implementations.

**Boundary.** Optimality combines the written lower bound and constructed witnesses; not exhaustive circuit search.

## C05 — Projection cost and safety counterexample

**Statement.** A family with n=2^m-2 has T(P_m)=2m-3 and T([P_m]_2)=n/2; the extracted grade can be unsafe.

**Proof.** [THEORY.md](THEORY.md), section 3. **Status:** COUNTEREXAMPLE, FINITE and WRITTEN.

**Computation.** Ranks and pair coefficients through m=10; full truth tables only m=2,3,4.

**Boundary.** Exponential in m, linear in n; not an exponential total-gate separation.

## C06 — Faithful flat gluing dimension

**Statement.** A linear multiplicative witness-algebra map retaining every primitive witness idempotent has target dimension at least 2^m.

**Proof.** [THEORY.md](THEORY.md), section 4. **Status:** FINITE controls and WRITTEN.

**Computation.** Small scalar-map controls; the universal argument is orthogonal-idempotent independence.

**Boundary.** Restricted fixed-summary theorem; dimension is not arbitrary circuit cost.

## C07 — Weighted witness fingerprint

**Statement.** Distinct witness monomials give an exact nonzero/satisfiable equivalence and Boolean top-coefficient identity.

**Proof.** [THEORY.md](THEORY.md), section 5. **Status:** FINITE and WRITTEN; algorithmic implication CONDITIONAL.

**Computation.** All designated verifiers through three witness bits; exact GF16 evaluation and specified extraction grids.

**Boundary.** Implemented evaluator is exponential. An efficient evaluator would give the stated randomized implication, not a deterministic P=NP proof.

## C08 — Overlap obstruction to multiplicative trace

**Statement.** The weighted trace multiplies on disjoint variables and fails on the displayed overlapping one-bit predicates.

**Proof.** [THEORY.md](THEORY.md), section 5. **Status:** COUNTEREXAMPLE, FINITE and WRITTEN.

**Computation.** Exact GF16 counterexamples and 4,096 disjoint controls.

**Boundary.** Does not exclude context-dependent nonlinear algorithms.

Machine-readable form: [claims.json](claims.json). Finite output records are in `evidence/baseline/`; the release replay is documented in `evidence/closure/`.
