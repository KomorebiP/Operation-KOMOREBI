# Komorebi p-adic program — Block 32 checked release

Goal I / phase D: finite-module cyclic presentations, intrinsic invariant-factor
signatures, and exact digit-system transport on the correlated reachable module.

Start with REPORT.md. RESULTS.json and results/final_*.json/log contain the fresh
verification. MATHEMATICS.md gives the argument. PROOF_BOUNDARY.md states exactly
what is and is not proved. REPRODUCE.md gives retained-evidence and fresh-build
commands. CONTINUE_HERE.md records the next obligation.

The canonical object here is the exponent multiset, not a chosen basis or literal
transition matrix. The number of states is unchanged from Block31. Observational
minimization is the next separate target.

Five new modules reside in lean/KomorebiPadic:
FiniteModulePresentation, InvariantFactorSignature, CyclicPresentationDynamics,
PresentedReachableMask, and PresentationExamples.

The exact original checked Block31 release is preserved under predecessor/.
No runtime or dependency cache is embedded. Compiled project objects are evidence
for the stated exact Lean pin, not portable across different Lean versions.
