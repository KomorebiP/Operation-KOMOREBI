# Continue with Block 78

Use `Komorebi_Beal_Block77_Secondary_Adjoint_Selmer_v7.7.0.zip` as the sole
execution checkpoint.  Preserve the exact Block 76 archive and all nested
history.  Read README, work77/TARGET_CONTRACT.md, REPORT.md, PROOF_BOUNDARY.md,
THEOREM_INDEX.md, GAP_LEDGER.md, every work77/notes file, source records,
DEVELOPMENT_FAILURES.md and VERIFICATION.md.  Keep bytecode disabled and run:

    python -B verify.py --report ../Block77_Replay.json

`--replay-predecessor` adds only the immediate Block 76 default verifier.

## Authoritative new boundary

- The Block73 q-equation has secondary class `[mu_p]`, where
  `mu_p=alpha cup(p-alpha beta)-p cup alpha` and `dp=-alpha cup beta`.
- `R_p+d_chi(alpha p)=mu_p` exactly, so q exists for fixed p iff `[mu_p]=0`.
- Changing p by z changes the class by `2 alpha cup z`; the invariant is an
  affine obstruction coset, not one canonical H2 class.
- Localization `H2(K,k(chi))->prod H2(K_v,k(chi))` is injective.  For fixed p,
  there is no hidden global H2 obstruction after all local classes vanish.
- The remaining problem is affine Selmer matching for ONE common p and q.
- The fixed-seven period/mixed-trace value is a nonhomogeneous local q-condition.
- `G_(Q7(sqrt5))(7)` is free pro-7 of rank3; there is no hidden local Demushkin
  relation at seven that will determine the probe.
- Cup-zero alone does NOT imply q-solvability: preserve the U3(F7) negative
  control.
- No one of the eight bounded patterns is eliminated.

## Next target

Construct the actual local affine conditions `P_v^geom` and `Q_v^geom` for the
nine toric support places plus the fixed places.  Compute the global localization
map or its Poitou-Tate dual.  Test whether the fixed-seven affine target lies in
the resulting q-Selmer image for each of the four support patterns.

Do not substitute unconstrained standard Massey vanishing for this local
matching problem.  Do not assign p or q independently at each place.  No new
Lean proof or independent reviewer is in Block77.
