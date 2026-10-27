# External and inherited inputs — v0.8

Pinned runtime: Lean 4.34.0-rc2, commit
6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
The compiler SHA-256 and actual source HEAD appear in v08_evidence/ENVIRONMENT.json.

25 inherited local modules are rebuilt. Their exact sources and the complete parent
archive are preserved. Their proven integer preimage, canonicity, normalization,
worklist correctness and standard first-order semantics are used explicitly.

Upstream inputs include integer Euclidean division/gcd identities, ordered-ring
arithmetic, natural powers, finite vectors, submodules and standard first-order
semantics. The new Euclidean coefficient recursion and its size/call-count bounds
are proved here from those inputs, not imported as assumed performance theorems.
The trace bound is a theorem about the literal trace functions in the Lean sources.

The classical schoolbook bit-operation model in COST_MODEL.md is explicitly a
WRITTEN cost convention; no external theorem of Lean runtime complexity is assumed.
None of these classical ingredients or their integration is assigned a historical
novelty verdict in this release. The official Mathlib Int.GCD and Int.DivMod
reference was consulted for API verification; the actual build uses the pinned local
source/cache rather than treating a current web documentation page as that pin.
