# Strong Artin v0.32 — Nonsemisimple Frobenius Norm

Author: Komorebi P.  Additive continuation of the exact v0.31 Frobenius Norm Resonance archive.

Parent SHA-256: `c9c0669f3993ffff06728ea5ae1d806a3201132747ceb162701c44a45638af59`.

## Result

For a k-linear operator T in characteristic p, write S_d(T)=1+T+...+T^(d-1).
Lean proves, without semisimplicity or finite dimensionality,

    S_(p^a)(T) = (T-1)^(p^a-1).

For d=m*p^a, with m nonzero in k, on a supplied primary block T=lambda*1+N
where lambda != 0 and N is nilpotent, define

    e = p^a-1   if lambda=1;
        p^a     if lambda!=1 and lambda^m=1;
        0       otherwise.

Then

    range S_d(T) = range N^e,
    ker   S_d(T) = ker   N^e.

The proof factors the geometric-sum polynomial at lambda and proves the
remaining polynomial factor evaluates to an invertible endomorphism.
It does not cancel T-1 in an endomorphism ring.

## Actual lifting application

For the actual square-zero kernel K of a coefficient map A -> B and F in A^x,
conjugation by F induces a norm N_(F,d). An explicit additive coordinate
isomorphism K -> V intertwining conjugation with a k-linear T identifies this
actual norm with S_d(T). Thus a prescribed V0 above F^d has a Frobenius root
with the original residue iff its normalized mismatch belongs to range S_d(T).

At prime-power degree, this is range (T-1)^(p^a-1), without diagonalization.
At mixed degree on a supplied primary block it is range N^e.

The release constructs those coordinates automatically for **every invertible
residual matrix** over k, lifted to matrices over k[epsilon]/epsilon^2. No
diagonal or semisimple residual Frobenius is assumed in this construction.

## Genuine unipotent example

Over F3, take F=[[1,1],[0,1]] and T=Ad(F). Lean proves

    (T-1)^3=0,  (T-1)^2!=0,
    S_3(T)(X) = X_10 * E_01.

For any matrix e, the actual prescribed target

    (1+epsilon*e) * F_upper^3

has a cube root above F iff e is a scalar multiple of E_01.
A nonzero E_01 mismatch lifts; an E_00 mismatch does not.
This exhibits a nonzero norm with only the eigenvalue 1 and prevents reuse
of the semisimple eigenvalue-only test on a nonsemisimple action.

## Files and verification

Six additive source modules contain 37 theorem declarations, 12 definitions,
8 abbreviations and one structure (497 lines). Counts include helpers and tests,
not 37 new results about Strong Artin.

`verify.py` verifies the parent hash and unchanged dependency bytes, stages fresh
source files and object files, compiles the complete direct closure with warnings
as errors, rejects proof escapes, and audits all 58 named new constants.
See RESULT.json for actual verification status, not this prose alone.

    python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 4
    python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 4

Repeat the second command until PASS. Omitting --max-modules runs all remaining
modules. The pinned Mathlib compiled cache is reused; 21 project dependencies,
six additive modules, and a separate axiom audit are rebuilt from source.

Independent finite checks:

    python3 checks/exact_norm_checks.py

They cover 756 primary-block cases and 23,904 actual dual-number matrix-power
cases. The finite checks corroborate but do not replace the Lean proofs.

## Scope

This is one square-zero Frobenius-restriction calculation. It does not prove a
new Strong Artin case, construct an automorphic carrier, solve global arithmetic
localization, or establish compatible coefficient-tower lifting. Mixed-degree
primary-block data are explicit; no automatic Jordan-normal-form decomposition
is constructed. A Jordan block of size s has rank max(s-e,0) by the displayed
image theorem and the elementary shift calculation; the rank formula is checked
by the independent finite script but is not an additional universal Lean declaration.

See RESEARCH_BOUNDARY.md, PROOF_LEDGER.md, FAILURE_LEDGER.md and CONTINUE_HERE.md.
