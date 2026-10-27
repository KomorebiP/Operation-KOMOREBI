# Komorebi Cross-Radix Rigidity — v0.12.0

This checkpoint closes the rational/complex identification of the v0.11 integral
cyclotomic-shell lattice.

For primitive shell label `c | T` with exact denominator `D_c`, the new scalar-extension
module proves that the cleared integer Möbius/Reynolds numerator extends to

`D_c * P_c`,

where `P_c` is the already-certified primitive DFT shell projector.

On integer packets `x`, Lean proves

`iota(N_c x) = D_c * P_c(iota x)`

and hence

`P_c(iota x) = D_c^{-1} * iota(N_c x)`.

Most importantly, the v0.11 good lattice is now characterized intrinsically as exactly
the integer packets whose primitive complex shell projection is again integral.

See `SCALAR_EXTENSION_BRIDGE.md`, `CONTINUE_HERE.md`, and `PROOF_BOUNDARIES.md`.
