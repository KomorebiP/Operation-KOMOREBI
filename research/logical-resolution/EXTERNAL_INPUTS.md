# External inputs and attribution

Lean 4.34.0-rc2 commit `6a10ac8c22beadecabdbb0919c2b50214762f91d` and Mathlib
commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` are the build inputs. The
restored dependency source files were checked against their tracked Git index;
SHA-256 and Git blob records appear in `source_records/MATHLIB_INPUT.json`.
The local compiled dependency cache is used. Mathlib itself was not cold-rebuilt.

Mathlib's Syntax supplies actual Language.Term, BoundedFormula, Formula, Boolean
and quantifier constructors. Semantics supplies Structure, term realization,
bounded formula Realize and the realization equations for not/inf/ex. Complexity
supplies the standard IsQF predicate and its constructors. The new translation
proves its own satisfaction theorem over those genuine APIs.

Documentation inspected September 21, 2026:

- https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Syntax.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Semantics.html

These rolling docs are explanatory pointers, not substitutes for the pinned build
source. Syntax explicitly uses locally nameless free variables and bound de
Bruijn levels, with the latest quantified variable at the last level. The source
custom fragment uses index zero for its newest variable, requiring our proved
binder assignment map.

The finite-rank back-and-forth method and the fiber-invariance criterion are
classical model-theoretic and quotient constructions. The project implements and
composes them for its specified observation/operation profile. No claim of new
abstract model theory, general first-order quantifier elimination, or historical
priority follows from the compiler checks or this bounded source verification.
