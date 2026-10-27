# Continue here

Read README.md, DEVELOPMENT_FAILURES.md, formalization/LEAN_STATUS.md and all six
proof notes before modifying this block. Run `python verification/verify.py` first.
This is an additive exploratory block, not an authoritative replacement for the
previous full IUT/KTG Lean project.

## Preserve

- Q/(ab)=c/R=M_c/(R_a R_b) is the correct ABC normalization.
- Q=R^{o(1)} is false; do not revive it or hide the missing ab factor.
- High weight is not high contact. Here the contact comes from an actual determinant
  Taylor cancellation, with a proved first coefficient.
- H_r(t)=det(Li_{i+j+1}(t)) has order r(r+1)/2 and is nonzero on 0<t<1.
- The depleted determinant has exact local valuation e S_{p,r}+2 E_{p,r}.
- The raw determinant has exact local valuation e r(r+1)/2 at p>3r-1.
- The explicit B_r budget supplies only a lower bound at small primes; it does not
  prove nonvanishing at all of them.
- Different period realizations are not the places of one algebraic number merely
  because they use the same formal functions.
- Rational truncation loses output-c contact at primes above its cutoff.
- The seven Lean scripts are uncompiled. Do not describe them as checked.

## Strongest legitimate next task

Try to construct an actual arithmetic realization of a nonzero contact determinant
and audit the exact local and global norm maps. Start with rank two:

    H_2(t) = Li_1(t) Li_3(t) - Li_2(t)^2.

Investigate an explicit motivic/iterated-integral realization with all local
comparison factors recorded, or a different nonzero algebraic auxiliary determinant.
Do not use an unspecified 'global gluing theorem' as an input. Do not call the
remaining problem just a local saturation issue.

Before claiming progress toward ABC, show a quantitative bound on c/R (or M_c
relative to R_a R_b), with constants uniform in the triple. Proving another local
valuation or formal transformation alone is not that bound.

A useful independent formalization task is to compile ABCJet.lean and then formalize
finite Cauchy--Binet and the residue-class energy minimum. Keep the infinite analytic
and actual arithmetic-realization obligations separate.
