# Exact prior and external inputs

## Frozen predecessor

Model-Theory Normalization v0.1, SHA-256
`e3250cda82983f5f531f640e880399bd60c07569db04c33e2e33631c3d5e4881`.
Its original ZIP is retained under history/. All six copied mathematical source
modules and observational_logic.py are byte-identical. The entire historical
representation-calculus/p-adic corpus is not rerun by this release.

## Compiler and Mathlib

Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
The compiler version and actual repository revision were checked locally. Source
hashes for the used model-theory API files are recorded separately.

Mathlib/ModelTheory/Basic.lean supplies Language and Structure.
Mathlib/ModelTheory/Syntax.lean supplies Term, BoundedFormula and Formula.
Mathlib/ModelTheory/Semantics.lean supplies the actual standard satisfaction
relation, connective equations and appended-bound-variable quantifier semantics.
Mathlib/ModelTheory/Complexity.lean supplies IsAtomic and IsQF and their closure
lemmas. Mathlib/ModelTheory/Definability.lean supplies Set.Definable and the empty-
parameter characterization by an actual formula.

The new translation does not take quantifier elimination, saturation, elementary
preservation or the desired satisfaction equivalence as an external theorem.
Ordinary Sum-tag injectivity and Fin environment lemmas complete its local proof.
The compiled dependency cache is reused, as disclosed. Only local project modules
are cold rebuilt in the final audit. Runtime and cache bytes are not redistributed.

## Public source check

The official Mathlib documentation was opened on 2026-09-21:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Semantics.html
https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Syntax.html

It documents actual realization and locally nameless bound-variable levels.
Those moving pages are orientation and terminology sources. The accepted proofs
use the local pinned revision rather than assuming that online documentation is
identical. A direct raw-GitHub request from the container failed DNS resolution;
no remote raw source was used to replace the pinned local files.

No PDF, commercial publication, priority search, external referee or new named
model-theoretic theorem is needed for or claimed by this block.
