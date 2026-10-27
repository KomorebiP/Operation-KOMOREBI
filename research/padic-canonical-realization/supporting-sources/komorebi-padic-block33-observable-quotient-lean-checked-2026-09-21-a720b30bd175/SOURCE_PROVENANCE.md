# Source and dependency provenance

The exact input predecessor archive is authenticated by PREDECESSOR_ARCHIVE.json.
All inherited mathematical source hashes appear in PREDECESSOR_SOURCE_HASHES.json;
only the root import list changes. predecessor/Block32_Checked.zip is byte-identical
to the checked input. Its retained predecessor archives preserve earlier releases.

The new proofs use the attached pinned mathlib source, particularly its quotient
mapQ, liftQ, mkQ and quotient-cardinality interfaces, plus Block31's finite
p-cardinality lemmas. The exact revision is in lake-manifest.json. Current official
API documentation was consulted as navigation only; the pinned source and the
actual compiler were authoritative:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Quotient/Basic.html
https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Quotient/Defs.html

No novelty or priority claim is made for the classical observability construction.
The new contribution recorded here is its integration and formal checking in this
particular arithmetic program, with explicit finite-ring hypotheses and boundaries.
