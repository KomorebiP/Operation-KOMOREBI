# CONTINUE HERE — Certified v0.12.0 State

## Authoritative state

v0.12.0 extends v0.11.0 without changing any of the 50 v0.11 Lean source files.

New modules:
- `CrossRadixCyclotomicShellScalarExtension.lean`
- `CrossRadixV12AxiomAudit.lean`

## Closed in v0.12

1. Complex subgroup Reynolds numerator equals the coordinatewise scalar extension of the
   saved integral subgroup numerator on integer packets.
2. The active Möbius shell mask is exactly the zero-trimmed sum of Reynolds width masks.
3. Every active denominator share cancels its subgroup width over `ℂ`.
4. The complex scalar extension of the actual v0.11 cleared shell numerator is exactly
   `D_c` times the certified DFT primitive-shell projector.
5. On integer packets,
   `iota(N_c x) = D_c * P_c(iota x)`.
6. Rational reconstruction:
   `P_c(iota x) = D_c^{-1} * iota(N_c x)`.
7. Exact integral-preservation characterization:
   `x ∈ L_c` iff `P_c(iota x)` is the scalar embedding of an integer residue packet.

## Strongest next theorem

Transfer a declared weighted p-adic cyclotomic trace-cancellation class into the now
identified shell projector and prove good-lattice membership `x ∈ L_c` from explicit
valuation-surplus hypotheses. Then identify the resulting p-primary defect/Smith data and
determine when the arithmetic cancellation surplus kills the shell defect completely.
