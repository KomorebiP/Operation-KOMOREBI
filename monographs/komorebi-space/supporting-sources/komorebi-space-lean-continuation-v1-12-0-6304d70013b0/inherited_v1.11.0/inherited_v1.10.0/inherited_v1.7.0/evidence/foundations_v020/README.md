# Komorebi Space Theory — v0.20.0

**Komorebi P.**

The quantitative realization model now permits known bounded invertible transports which are not isometries. Exact families still correspond to the common holonomy-fixed anchor space, now by a continuous linear equivalence rather than an isometry. Path errors are bounded by transported gain sums. For finite-dimensional real inner-product fibers, the existing kernel projection yields a constructed exact ambient repair with a bound incorporating route amplification, normalization, restoration and holonomy conditioning.

The scalar-chain example retains the nonzero anchor 7, has directed-edge residual norm 1, and has exact repair error 2^n-1. It refutes extending the former route-length estimate or nonexpansiveness conclusion without their isometry hypotheses.

Inventory: **122 proof modules, 1,299 named theorem declarations, 696 indexed constructions**. Five new modules add 92 theorems and 42 constructions. All 117 preceding proof modules are preserved unchanged. Counts include structural and auxiliary declarations, not independent discoveries.

## Main checked declarations

```lean
KomorebiSpace.AmplifiedTransport.Connection.walkSum_defect
KomorebiSpace.AmplifiedTransport.Connection.walk_error
KomorebiSpace.AmplifiedTransport.Rooted.parameterEquiv
KomorebiSpace.AmplifiedTransport.Rooted.orthogonalRepair_error
KomorebiSpace.AmplifiedTransport.Rooted.finite_dimensional_ambient_repair
KomorebiSpace.AmplifiedTransport.Examples.exponential_amplification
KomorebiSpace.AmplifiedTransport.Examples.length_only_bound_false
```

Read `docs/AMPLIFIED_TRANSPORT_RECONSTRUCTION.md` for the exact mathematics and scope. `docs/THEOREM_INDEX.md` indexes the cumulative named statements. The retained PDF in the documentation is the historical v0.13 rundown, not an updated v0.20 exposition.

## Verification strategy

The v0.19 baseline was independently rebuilt from all 117 module sources in this continuation. The current v0.20 verification compiles the entire 122-module project and its root, then audits all named theorem and construction dependencies and runs three negative controls. The external delivery receipt reports actual completion and records the fresh final-archive replay separately.

The fresh-archive replay uses the independently rebuilt, hash-validated 117 baseline modules and freshly compiles the five additions plus the cumulative root. It repeats the complete axiom inventories and negative controls. It must not be described as a second full clean cumulative v0.20 compilation.

## Reproduce a complete source build

Use Lean 4.34.0-rc2 and mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` in the established portable runtime. The runtime and dependency cache are not included.

```bash
python3 scripts/check_hashes.py
python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --audit-dir audit/my_full_replay --timeout 150
python3 scripts/audit_constructions.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --audit-dir audit/my_constructions
python3 checks/computation/nonisometric_exact.py --output audit/my_nonisometric_check.json
```

The optional `scripts/replay_amplified_extension.py` implements the documented baseline-reuse replay. It requires the baseline source directory and a successful full baseline verification report, and verifies reused source and compiled hashes before loading them.

## Limits

The connection is known, linear and boundedly invertible. Global repair of arbitrary anchors uses a finite-dimensional inner-product fiber, but not an inner-product norm on vertex or edge products. The preserved information is the feasible projected anchor, not an inadmissible full anchor. No uniform bound over arbitrary connections, global best approximation in the maximum norm, unknown-connection estimation, nonlinear reconstruction, executable certified SVD, or normed descent for an arbitrary stack is inferred.

Positive library sources contain no admitted proofs or custom axioms. The intentionally invalid tests are excluded from library imports. Allowed standard axioms are `propext`, `Classical.choice`, and `Quot.sound`. The Lean compiler and pinned imported dependency cache remain trusted. Exact finite tests and hash manifests supplement but do not replace the universal proof terms.
