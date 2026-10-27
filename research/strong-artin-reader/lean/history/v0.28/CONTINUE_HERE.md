# Continue from v0.28

Canonical base: `Strong_Artin_Lean_v0.27.0_Continuous_Obstruction_FiniteQuotient_Checked.zip`, SHA-256 `4c295925c15e3047d8fd5ebad97744911e2ae79f07e72ae0b080cb8e5af05d56`.
This release is on the audited continuous representation-H2 branch. Do not replace its base with
another same-numbered archive or silently merge the historical polynomial/cotangent branches.

Read README.md, RESEARCH_BOUNDARY.md, and RESEARCH_CHECKLIST.md completely before extending.

Strongest closed results:

1. Actual continuous simultaneous local prescriptions along arbitrary continuous group maps
   lift literally iff an explicit constrained degree-two class vanishes.
2. After the absolute multiplication defect has a primitive, the exact remaining obstruction is
   in coker(Z1_cont(global) -> product Z1_cont(local)), independent of that primitive.
3. Under finite quotient/local-group order invertibility, one global lift matches all prescribed
   finite local lifts up to independently constructed 1+kernel conjugators.
4. Pairwise extendability and overlap compatibility do not guarantee simultaneous extendability.
5. Literal and up-to-local-conjugacy deformation problems are demonstrably different, even in
   the order-invertible sector.

Next meaningful work: construct the continuous constrained obstruction including local gauge
terms or another precise arithmetic local deformation condition, then prove vanishing of its
particular class in one actual arithmetic case. Do not just assume surjectivity of localization.
The strict cokernel uses Z1, not H1; a quotient by local coboundaries changes the problem.

Replay with verify.py --kit PATH --max-modules 8, then --resume in bounded batches until PASS.
Do not count PARTIAL or an interrupted wrapper as a complete pass. Preserve zero proof escapes,
warnings-as-errors, explicit source hashes and the direct verification scope.
