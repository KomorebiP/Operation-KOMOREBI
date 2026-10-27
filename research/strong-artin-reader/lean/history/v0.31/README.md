# Strong Artin v0.31 — Frobenius norm resonance

Author: Komorebi P.
Evidence: Lean-checked as written; see RESULT.json for the exact replay scope.
Parent: `Strong_Artin_Lean_v0.30.0_Unramified_Procyclic_Lifting_Checked.zip`
Parent SHA-256: `b1daa98ca39e924aa46aa2afa176acb3c947df1e94b96873fbbbbe17af9a0be4`

## What changed

v0.30 constructed the actual norm-localization map and its mismatch class, but
left its image to be determined. This release computes that image whenever the
actual square-zero kernel action admits the explicit diagonal coordinates below.
It constructs those coordinates for genuine matrix rings over dual numbers,
proves positive and negative prescribed-restriction results, and transports the
criterion to the actual inherited continuous local-gauge obstruction.
No Strong Artin theorem, global Selmer vanishing, or automorphic carrier is claimed.

## Exact input

Let q:A -> B be a square-zero ring map, let K=ker(q) be the actual additive ring
kernel, and let F be an invertible upper-ring Frobenius. The inherited Datum
supplies the kernel action and exact square-zero power formulas.

A `FrobeniusSpectralCoordinates D F k I` consists of an additive equivalence

    E : K ≃+ (I -> k)

and scalars lambda_i in a field k, with the proved identity

    E(Ad(F)x)_i = lambda_i E(x)_i.

This is a complete diagonalization of the ACTUAL kernel action, not an arbitrary
list of eigenvalues. The theorem does not infer it for a general nonsemisimple
residual image. An actual constructor is supplied for matrices over k[epsilon]/epsilon^2.

## Single restriction

Write s_d(a)=1+a+...+a^(d-1). The exact norm satisfies

    E(N_(F,d)x)_i = s_d(lambda_i) E(x)_i.

For a prescribed V with q(V)=q(F^d), set e=(V-F^d)F^(-d) in K. Then

    exists F' with q(F')=q(F) and F'^d=V
      iff E(e)_i=0 for every i with s_d(lambda_i)=0.

One independent local kernel conjugator does not enlarge this set: it can be
absorbed into the chosen global F'. This absorption is for ONE restriction, not
an arbitrary family with different local conjugators.

The exact resonance test is

    s_d(a)=0 iff (a=1 and d=0 in k) or (a!=1 and a^d=1).

When all multipliers are nonzero, every compatible prescribed V has a strict root.

## Defining characteristic

For prime p=char(k),

    s_p(a)=(a-1)^(p-1),

so the image condition is precisely vanishing of mismatch coordinates with
lambda_i=1. The theorem is NOT universal vanishing of the prescribed-restriction
obstruction.

For diagonal matrix Frobenius diag(alpha_i) over k[epsilon]/epsilon^2, the actual
kernel coordinates are epsilon matrix entries and lambda_(i,j)=alpha_i/alpha_j.
Thus prescribed p-th powers lift iff every mismatch entry inside a repeated-
eigenvalue block vanishes. A trace-zero condition alone is insufficient.

For d prime to the coefficient characteristic, every prescription lifts if taking
d-th powers creates no new eigenvalue collisions. Degree invertibility alone
is insufficient. In every positive matrix rank and characteristic p, the release
constructs an obstructed p-th-power prescription, even for diagonal Frobenius.

## Simultaneous restrictions

For degrees d_l and mismatch coordinates e_(l,i), local correction is

    s_(d_l)(lambda_i) (x_i+(1-lambda_i)z_(l,i)).

The complete criterion is:

1. For lambda_i!=1, e_(l,i)=0 at every resonant local degree.
2. For lambda_i=1, there is ONE a_i with e_(l,i)=d_l*a_i for every l.

The first condition is local. The second is the remaining shared-global-correction
condition. The criterion is proved for v0.30's actual matching cokernel class and
then for v0.29's actual continuous local-gauge class under procyclic degree maps.
No unidentified comparison between two abstract H1 objects is assumed.

## Continuous positive theorem

For finite discrete square-zero coefficients and the genuine profinite Zhat, a
nonresonant spectral model yields a continuous representation lift whose
restriction along the specified degree map is EXACTLY the prescribed continuous
local representation. This is stronger than merely asserting conjugacy at its
generator.

## Checked controls

All matrix examples are over F3[epsilon]/epsilon^2.

- F=diag(1,-1), d=2: an off-diagonal mismatch obstructs, although 2 is invertible.
- The same F, d=3: an off-diagonal mismatch DOES lift, via the general theorem.
- The same F, d=5: EVERY compatible prescription lifts, via the general theorem.
- F=I, d=3: a nonzero off-diagonal trace-zero mismatch obstructs.
- F=I, degrees 1 and 2: each prescription individually lifts, but mismatches
  0 and E00 cannot arise from one shared Frobenius, even up to local kernel conjugacy.
  The actual inherited matching class is proved nonzero.

## Verification

Pinned Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Pinned Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Warnings as errors. No sorry/admit/custom axiom/custom opaque/native_decide/unsafe
in active source. The seven new modules contain 41 theorems, 15 definitions,
6 abbreviations, 1 structure, and 668 lines; 63 explicitly named constants are
axiom-audited. Generated structure fields/constructors are not counted separately.
The direct replay compiles 28 unchanged dependencies and 7 new sources plus the
audit module. The pinned Mathlib object cache is reused. No all-history replay or
independent specialist review is claimed.

Run, in bounded batches:

    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 8
    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 8

Repeat the second command until PASS. Source and already-recorded output hashes
are checked before resume. Then run:

    python3 checks/exact_norm_checks.py

The independent script exhausts 21 diagonal 2x2 residual matrices over F2,F3,F5,
degrees 0 through 6, and all square-zero lifts: 72,380 actual dual-number power
checks and 147 full attainable-image comparisons. These finite checks corroborate,
but do not replace, the general Lean proof.
