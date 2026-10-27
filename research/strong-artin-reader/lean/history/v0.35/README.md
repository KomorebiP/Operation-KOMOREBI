# Strong Artin Lean v0.35 — Compatible Frobenius Towers and p-adic Roots

Author: Komorebi P.

Exact parent: `Strong_Artin_Lean_v0.34.0_Mixed_Characteristic_Kernel_Checked.zip`
Parent SHA-256: `897746a6d7928e5a9cb11014fcc09aca957d03b47644f4960fe1317cf5be304a`

## Result

The positive coefficient-tower problem is solved under one residual nonresonance condition. The condition is checked only modulo p, not assumed anew as obstruction vanishing at every higher level. The compatible matrices and their inverses are assembled into an actual matrix unit over Mathlib's `PadicInt p`.

Let p be prime, let n be a finite index type, let Fbar be in GL_n(F_p), and let d be a natural number. Put

    T = Ad(Fbar),   S_d(T) = 1 + T + ... + T^(d-1).

Assume S_d(T) is bijective. For a compatible target family

    U_r in GL_n(Z/p^(r+1)),   U_0 = Fbar^d,

there exists exactly one family F_r satisfying

    F_0 = Fbar,
    F_(r+1) reduces to F_r,
    F_r^d = U_r  for every r.

In particular, for an actual U in GL_n(Z_p) with residue Fbar^d, there is exactly one F in GL_n(Z_p) with residue Fbar and F^d = U.

Main declarations:

- `FrobeniusTower.exists_unique_compatible_root_tower`
- `FrobeniusTower.exists_unique_padic_frobenius_root`

All names have prefix `Komorebi.StrongArtin`.

## Substantive sufficient condition

If Ad(Fbar)-1 is nilpotent and d is nonzero modulo p, then S_d(Ad(Fbar)) is bijective. This permits nonsemisimple residual Frobenius. It does not require invertibility of the residual image order.

The proof evaluates the norm polynomial at a nilpotent primary operator. Its value at the eigenvalue 1 is d, a unit. The inherited nilpotent-polynomial theorem then gives an invertible operator.

Thus every p-adic matrix U congruent to the identity has exactly one d-th root congruent to the identity whenever p does not divide d. A second specialization is proved for the nontrivial 2x2 unipotent Frobenius over F_3, for all compatible 3-adic square targets.

## Simultaneous prescribed restrictions

For an arbitrary indexed family d_i and U_i with residue U_i = Fbar^(d_i), choose a pivot i0. Assume nonresonance for degree d_i0 on Fbar and on every Fbar^(d_i). Then a unique shared p-adic Frobenius with F^(d_i)=U_i exists exactly when

    U_i^(d_i0) = U_i0^(d_i) for every i.

These are exact identities in the p-adic matrix group. They are not merely residual congruences or independent root-existence assumptions. Necessity is immediate from a common root; sufficiency uses the pivot root and injectivity of its degree power map in every compared residue fibre.

On the identity residue fibre, the hypotheses reduce to one prime-to-p pivot degree. The other degrees may be divisible by p. The target compatibility identities remain necessary.

## How the tower is constructed

1. The v0.34 actual mixed-characteristic kernel coordinates convert the square-zero Frobenius norm to the residual operator S_d(T).
2. Surjectivity supplies a root of the original prescribed power equation at the next level.
3. Injectivity proves that this root is unique within its required reduction fibre.
4. The adjoint action depends only on Fbar, so the same norm hypothesis persists at every stage.
5. Induction gives a unique root in the fixed Fbar fibre at every coefficient level.
6. Uniqueness forces the roots to reduce compatibly.
7. Compatible integer representatives give genuine `PadicInt` limits entry by entry. Their compatible inverses also converge and are verified to multiply to the identity by reduction at every level.
8. Equality of all reductions proves the exact p-adic power equation and its uniqueness.

The internally recursive modulus is proved equal to p^(r+1). It is used only to make the previously checked Z/(mp) -> Z/m transition definitionally available.

## Negative control: a resonant branch can stop

The target equation X^3=1 has the partial branch

    X = 1 mod 3,   X = 4 mod 9.

That branch is valid modulo 9, but none of 4, 13, 22 has cube 1 modulo 27. Lean proves no 3-adic cube root of 1 can reduce to 4 modulo 9. It also proves that the different full root X=1 exists.

This separates failure of a chosen branch from failure of the target itself, and refutes the claim that every successful finite-level choice can continue. The nonresonance condition is not omitted.

## Verification

Pinned Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Pinned Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Run in bounded batches:

```bash
python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 8
python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 8
# Repeat --resume until status is PASS.
python3 checks/exact_tower.py
```

There are 22 unchanged parent dependencies and 8 new source modules, followed by an axiom-audit module. The 68 explicitly named constants comprise 47 theorems, 16 definitions and 5 abbreviations. There is one additional anonymous modulus-nonzero instance. These counts include helper results and examples. The source total is 619 new lines.

Warnings are errors. Prohibited proof escapes and custom axioms are rejected. The all-named-constant axiom audit permits only propext, Classical.choice and Quot.sound. The pinned Mathlib compiled cache is reused. This is self-review plus Lean kernel checking, not an independent-kernel or all-historical-branch audit.

## Boundaries

No Strong Artin or new automorphic realization is claimed. The theorem does not prove general resonant tower existence, global Galois/Hecke compatibility, automorphic carrier existence, arbitrary local gauge-tower matching, or automatic ramified-DVR generalization. It constructs a p-adic Frobenius matrix; no new theorem converting it into an arithmetic local Galois representation is claimed in this release.

The proof mechanism is the nonarchimedean implicit-function/Hensel mechanism for the matrix power map, formally integrated with the audited norm obstruction. Historical novelty is not asserted.
