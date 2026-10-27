# Block 43 failure ledger

The following development failures were excluded from verification evidence.

1. The first `β` linearity proof used `rfl`. Negative coordinates reduced to addition in the opposite order. It was repaired with coordinate simplification followed by the additive-group normalizer.
2. The first operator-residual proof expanded coordinates and left an inconsistent normal form. It was replaced by a direct module identity in the continuous-linear-map space.
3. Simplification of the zero-time scaling theorem did not close equality of continuous linear maps. Extensionality reduced it to pointwise scalar action.
4. The first exponential-rate proof lacked the restricted `NormedAlgebra ℚ` instance required by the generic Banach-algebra exponential API. The standard scalar-restriction instance was installed locally.
5. A nonexistent `Tendsto.clm_apply` projection was attempted. The proof was rebuilt from the already checked `O(h²)` action residual.
6. The generic scalar-commutation instance required by `Commute.smul_left` was unavailable for endomorphism composition. Commutation of two scalar multiples of one generator was proved extensionally.
7. Direct audit invocations have substantial startup cost in this pinned project. Only terminal return codes are accepted. Polls, partial logs, and interrupted calls are not classified as passes.
