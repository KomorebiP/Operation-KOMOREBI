# Python correspondence routes

Base: SF-LEAN-B18 on repository f49e00d6088bbc8dca4f8a3a70b232db1eea085b.
Target and acceptance boundary are fixed in TARGET.md. No independent or
parallel agent was used. Source and proof hashes are in the final manifests.

## R19.1: general Python semantics

Mechanism: interpret an unrestricted Python AST and prove whole-language
operational correspondence. The initial grammar inspection found nested
comprehensions/generators, mutable lists, calls, exceptions, type tests and
dictionaries. A general implementation would require substantial unrelated
language support. This route was not exhausted or refuted. It is deferred;
resume it if the objective is to remove the trusted closed-fragment translation
boundary, starting with the exact six-function closure and an explicit
expression/statement interpreter. It is not required by the conditional target.

## R19.2: source-bound imperative refinement

Mechanism: check the full selected source shape, translate arithmetic and
literal data, and prove the resulting imperative operational model refines the
typed specification. The central discriminators are eager shared products,
safe array indices, a pre-append step guard, reverse iteration and all seven
dictionary fields. The binder and complete source hashes fail closed on change.

Artifacts: lean/CoupledPythonSource.lean, lean/CoupledPythonRefinement.lean,
tools/bind_python_source.py, its patterns/template, and the final replay receipt.
The array/fold route was pursued through a bidirectional outcome theorem,
termination/determinism in the mathematical model, type-tagged raw preparation,
and real/complex enclosure composition. Result: proved operational-model
refinement and conditional actual-source correctness with the named TCB.
No remaining loop, normalization or dictionary lemma is deferred in this scope.

Development issues were local syntax, simplifier and dependent-elimination
repairs. In particular, unfolding list enumeration too eagerly obscured safe
array access; explicit index lemmas resolved it. A raw outcome equality needed
generalization before case analysis. These are failed proof scripts, not
counterexamples to the target. Their logs remain labeled development evidence.

## R19.3: individual-result certificate validation

Mechanism: validate each returned result with an independent exact checker or
kernel certificate. This could give a useful fail-closed deployed adapter, but
does not itself establish the original source's universal refinement. It was
not used to claim the present target. It remains a possible deployment route;
resume by fixing a result/witness schema and a kernel-verifiable validator if
individual-call certification is requested. No production wrapper was changed.

## R19.4: counterexample/mutation stress test

Executed 24 named source mutations with whole-file pin rejection disabled, plus
five false Lean claims. This distinguishes arithmetic/source-shape binding from
a checksum-only guard and catches missing premises and changed conventions.
All required rejections are recorded in the final receipt. The finite test
does not establish trusted-translator correctness for all possible programs.

The phase closes at the same checkpoint as its assessment. There is no delayed
or active mathematical run after accepted replay. The general-semantics and
per-call-validator alternatives remain deferred, with the explicit resumption
conditions above; neither has been labeled impossible or exhausted.
