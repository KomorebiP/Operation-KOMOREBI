# Verified source boundary

Mathlib revision: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
Lean revision: `6a10ac8c22beadecabdbb0919c2b50214762f91d`, version 4.34.0-rc2.
The local source hashes and actual git revision are in evidence/ENVIRONMENT.json.

Three project source files are copied byte-for-byte from the attached p-adic
Block 15 archive: FiniteGenerators.lean, PrincipalIdealGenerators.lean, and
PrimeIdealGenerators.lean. They are rebuilt here; this does not reverify all the
other p-adic modules. In particular the generic matrix proof is not conditional
on an unproved module-generator axiom.

The integer basis argument uses Mathlib's `Submodule.basisOfPid` and finite-rank
comparison. Its PID input is the integers, not the ring Z/(p^r). The residue-field
argument uses Mathlib's ZMod unit/cast properties and field dimension. These are
existing library results, not new historical claims.

Public source references consulted:
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/FreeModule/PID.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/ZMod/Basic.html

Those online pages may be newer than the pin. Compilation and exact input
interpretation use the local pinned sources above. This was an API/source check,
not a comprehensive novelty search.
