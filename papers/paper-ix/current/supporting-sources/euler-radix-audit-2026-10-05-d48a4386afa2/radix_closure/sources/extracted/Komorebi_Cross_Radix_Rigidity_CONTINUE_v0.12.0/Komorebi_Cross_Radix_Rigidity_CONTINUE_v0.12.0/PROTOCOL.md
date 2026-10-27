# Protocol — v0.12.0

- Treat v0.11 as immutable baseline; verify `SHA256_SOURCES_V110.txt` before work.
- Preserve Bell as an explicit external interface.
- Preserve the false-naive-integral-normal-form obstruction.
- The rational/complex shell identification is now CLOSED; do not re-prove it.
- For arithmetic integral-shell work, keep distinct:
  1. primitive complex projector `P_c`,
  2. exact denominator `D_c`,
  3. cleared integer numerator `N_c`,
  4. good lattice `L_c`,
  5. residual finite defect,
  6. Smith/Fitting data,
  7. p-adic cancellation hypotheses that may force membership in `L_c`.
- Never infer good-lattice membership from support alone; v0.10 contains a negative control.
- Arithmetic cancellation results may enter only with their declared p-adic/Amice hypotheses.
- Every new Lean claim must pass `-DwarningAsError=true`, placeholder scan, and an axiom audit.
