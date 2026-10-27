# Local-surjectivity recovery evidence

The unpublished source and its previous development logs were removed by automated
workspace maintenance. This source was reconstructed from the preserved task
summary and the restored earlier proof modules. These are new recovery checks,
not claims that the previous source bytes or logs were recovered.

The recovered module contains one definition and six theorems. It proves compactness
of actual residue balls, convergence of canonical integer truncations, invariance
of the actual Jacobian under a constant output shift, existence of preimages for
integer targets, and then existence for arbitrary p-adic targets by closedness of
the compact image. No compatibility of arbitrarily selected preimages is assumed.

`attempt_01.log`: Lean elaborated all seven declarations with the standard three
axioms, but the warning-as-error gate rejected the deprecated name
`Set.setOf_forall`. It was replaced with `Set.ofPred_forall`.

`attempt_02.log`: passed with Lean 4.34.0-rc2, one thread, warning-as-error, default
heartbeat limits, and the pinned runtime. All seven declarations use only
`propext`, `Classical.choice`, and `Quot.sound`.

Frozen source SHA-256:
`c4ddf4985f7739b5e8555d103c85e131524d7c04d855bbbe94826ba58824c937`.

The compiled artifacts were written to the shared recovery build directory and
are not intended for inclusion in the source release.
