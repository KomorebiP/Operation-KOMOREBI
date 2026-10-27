# Continue with Block 79

Use `Komorebi_Beal_Block78_Finite_Local_Flexibility_v7.8.0.zip` as the sole
execution checkpoint. Preserve the exact Block77 predecessor archive and nested
history. Read README, work78/TARGET_CONTRACT.md, REPORT.md, PROOF_BOUNDARY.md,
THEOREM_INDEX.md, GAP_LEDGER.md, all notes, source records, failures and
verification records. Keep bytecode disabled and run:

    python -B verify.py --report ../Block78_Replay.json

## Authoritative new boundary

- At each depth-one beta-supporting toric place, with c=beta(T)!=0,
  b=beta(F), h=(Q-1)/7 mod7, the first-stage cochain obeys

      c p(F)-b p(T)=-h c.

  This is invariant under changing the Frobenius lift and defines a nonempty
  first-order affine hyperplane.
- For K=Q(sqrt5), finite localization is surjective for BOTH H1(K,k) and
  H1(K,k(chi)). Neukirch condition (c) applies: the relevant dual splitting
  groups are C6 and1, with H1 zero.
- Therefore finitely many local Stage-P conditions can be matched exactly, and
  finitely many strict-equivalence-invariant Stage-Q conditions can be matched
  once the Block77 H2 obstruction vanishes locally.
- This does NOT control ramification outside the prescribed finite sets.
- No one of the eight bounded patterns is eliminated.

## Next target

Classify where the ACTUAL adjoint corrections p and q are allowed to ramify at
beta-unramified bad primes. Derive the local conditions there from the same Frey
toric/period representation. Then either:

1. obtain a justified finite/full ramification set Sigma and compute the
   restricted Selmer/Poitou-Tate cokernel; or
2. derive a support-uniform integral relation that prevents the auxiliary
   ramification used by unrestricted localization.

Do not use unrestricted H1 surjectivity as if it preserved unramifiedness at all
other places. Do not claim exact framed q matching from cohomology-class matching.
The eight bounded patterns, unrestricted support/depth, minus component,
independent upstream review, CM/higher Hilbert branches, full signature and Beal
remain open.
