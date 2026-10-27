# Beal research, Block 77
## Secondary adjoint obstruction and affine Selmer reduction

Release 7.7.0, 21 September 2026.

The unresolved Block 73 `q` equation has now been identified exactly as a
symmetric twisted triple-Massey-type obstruction.  For a fixed first-stage
cochain `p`, its H^2 class satisfies a local-global principle.  Consequently the
main remaining problem is not a mysterious extra global H^2 class: it is whether
one common global adjoint deformation can meet all of the required local affine
conditions, especially the fixed-seven period target.

No one of the eight bounded depth-one patterns is eliminated.

## Main identities

With `dp=-alpha cup beta`, put `s=alpha beta`.  Then

    ds=-(alpha cup beta + beta cup alpha).

The defining system

    D12=-p,    D23=p-s

has Massey cocycle

    mu_p=alpha cup(p-s)-p cup alpha.

If `R_p` is the right side of the actual q-equation, then

    R_p + d_chi(alpha p)=mu_p.

Hence `[R_p]=[mu_p]`.  Changing `p` by `z in Z^1(K,k)` changes the class by
`2[alpha] cup[z]`; the choice-independent object is the affine coset

    [mu_p]+2[alpha] cup H^1(K,k).

The Heisenberg control proves cup-zero alone does not imply q-solvability.

## Local-global theorem

Localization on `H^2(K,k(chi))` is injective.  Restriction to `K(zeta_7)` is
injective by restriction-corestriction of degree six; over that field the module
is two trivial F7 copies and Brauer-Hasse-Noether gives the local-global
injection.  Thus, for one fixed global `p`, q exists globally iff its secondary
class vanishes at every completion.

The remaining matching of prescribed local q-values is an affine H^1/Selmer
problem.  The fixed-seven mixed trace is a nonhomogeneous local target, so this
is a stronger type of information than the homogeneous finite Frobenius sieve
shown insufficient in Block 70.

## Local seven-adic boundary

`Q_7(sqrt(5))` does not contain `zeta_7`.  Shafarevich's theorem therefore makes
its maximal pro-seven Galois group free of rank three.  Together with the
already established Kummer basis `[phi],[3],[7]`, this shows that there is no
unexploited local Demushkin relation that can determine the mixed trace.  The
missing constraint must come from global arithmetic matching or the integral
Frey geometry.

## Literature context

The 2026 strong Massey-vanishing theorem of
Maire--Minac--Ramakrishna--Tan applies to ordinary mod-7 Massey products over
`K=Q(sqrt(5))`.  It is not used to solve the twisted F49-valued local deformation
problem.  It reinforces the project boundary: abstract Massey vanishing and the
existence of one defining system are weaker than existence of the one defining
system compatible with all actual local data.

## Remaining obligation

Build the actual local affine conditions for `p` and `q`, compute the relevant
localization/Selmer image (or its Poitou-Tate dual), and test the fixed-seven
affine target for the four support patterns.  A zero result would eliminate all
eight coefficient-conjugate tuples; a nonzero result would explicitly
parameterize the remaining global adjoint deformations.

Unrestricted conductor and higher depth, the minus component, independent
upstream proof acceptance, the CM/higher-Hilbert branches, the complete
signature, and full Beal remain separate obligations.
