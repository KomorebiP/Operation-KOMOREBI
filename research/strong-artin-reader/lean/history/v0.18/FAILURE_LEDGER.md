# Failure ledger — Strong Artin Lean v0.18

All entries below are proof-engineering or verification failures. None is evidence against the mathematical claims, and none was counted as a pass.

## F1. Portable-kit command attempted dependency repair

An early use of the kit's broad `run.sh check` path caused Lake to remove the pinned mathlib directory and attempt an online clone. Internet access was unavailable. The portable kit was restored from its verified archive, and all subsequent checks used direct `lake env lean` compilation without invoking dependency repair.

## F2. Initial cyclic-H¹ surjectivity route lacked a direct epi instance

The first draft tried to infer surjectivity of the exposed odd cyclic cohomology projection directly. Lean did not have the required instance in that form. The proof was repaired by factoring through the short-complex homology projection, whose epimorphism is available, and transporting through Mathlib's cyclic cohomology isomorphism.

## F3. Frobenius range comparison needed explicit signs and types

The first range-equality draft left matrix-linear-map types underdetermined and obscured the sign difference between `ρ(g)-1` and `1-Ad(F)`. The final proof uses `-Y` explicitly in both directions and supplies the full linear-map types.

## F4. First tame-pairing draft omitted the trace-probe namespace

`traceProbe` was initially out of scope. The namespace import was added; no statement changed.

## F5. One-dimensional normalization API errors

The first draft used the wrong namespace for dual finrank, attempted a malformed scalar-injectivity expression, and had an unused finite-dimensional section variable. The final proof uses `Subspace.dual_finrank_eq`, `smul_eq_zero`, and no unnecessary finite-dimensional hypothesis.

## F6. First Tate-boundary draft omitted the centralizer namespace

`frobeniusCentralizer` was initially unresolved, producing metavariables and downstream errors. Opening `LocalFrobeniusPerfectPairing` resolved the intended type. A nonexistent `ne_congr` helper was replaced by direct rewriting.

## F7. Full wrapper replay exceeded the execution ceiling

The fresh all-in-one verifier compiled the five inherited dependencies and four new modules, then exceeded the outer 30-minute execution limit while beginning `OneDimensionalPairingNormalization`. No theorem error or `sorryAx` appeared. The final two modules were compiled separately against the same replay `olean` directory and source roots, and both returned exit code zero. The timed-out wrapper is not treated as a completed replay; the recorded split-batch 11-module closure is authoritative.
