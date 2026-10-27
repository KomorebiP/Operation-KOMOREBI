# Beal research, Block 75
## Global integral semilinearity and endpoint compatibility

Version 7.5.0. 21 September 2026.

A previously missing comparison is now proved: the actual natural Tate lattice and
its opposite stable-lattice endpoint admit a GLOBAL INTEGRAL coefficient-semilinear
intertwiner induced by a specific isomorphism of conjugate curves. The argument
holds at every positive actual depth under G1–G3. The normalized integral frame
additionally uses G4, the inherited split toric geometry at seven.

All eight bounded patterns remain. No actual numerical mixed trace, candidate
integral Galois image, or global solution of the adjoint equations is produced.
The entire reducible branch, full signature, and Beal remain unresolved.

## 1. Main integral theorem

Let O=Z7[w]/(w^2-5), sigma(w)=-w, and let rho be the ACTUAL natural representation
with nonzero natural unit coefficient and nonzero opposite endpoint class. There
is an actual integral operator U=C sigma, with C in GL2(O), such that

    rho(j g j^-1)=C sigma(rho(g)) C^-1,
    C sigma(C)=-rho(j^2),
    C21 in7^n O,

for every g in G_K. It preserves the natural endpoint, the opposite endpoint, and
the entire stable-lattice segment. This is stronger than equality of residual
cohomology classes. It does not identify the base sqrt5 with coefficient w.

## 2. The mechanism

For delta=9-3phi, delta^iota=phi^2 delta. The actual map from the conjugate curve is
(x,y)->(x,y/phi). Applying it to Jacobians and their torsion gives an actual
unimodular Z7-linear Tate operator U. Its square is -rho(j^2), not +rho(j^2).

The separated residual characters give integral eigenprojectors. In an eigenframe,
all stable lattices form the segment L_i=O e1+7^i O e2, 0<=i<=n. The two nonsplit
orientations identify its endpoints uniquely. The argument also proves absolute
irreducibility from the nonzero upper and lower entry ideals.

An ordinary E-linear intertwiner between rho and rho^j would preserve the natural
endpoint up to homothety, hence make the normalized natural classes(u,r,1) and
(-u,r,1) proportional. The final coordinate fixes the proportionality to1, forcing
u=0, contrary to the retained arithmetic nonvanishing theorem. Thus the ordinary
intertwiner space vanishes. Projecting the ACTUAL geometric U into its E-linear
and sigma-semilinear parts forces it to be purely semilinear. Its actual integral
origin, followed by endpoint uniqueness, supplies the asserted integral comparison.

This proof does not assume the old semilinear cohomology theorem. Under its stated
inputs it also gives a separate proof of u^7=-u, r inF7 and j[beta]=sigma[beta].

## 3. A compatible choice and exact normal form

The inherited local Kummer basis phi,3,7 gives a tower containing all7-power torsion
of the actual split toric Jacobian at seven. A compatible automorphism conjugates
phi, fixes the roots of unity and the roots of3,7, and sends a chosen root ofphi to
minus its inverse. Its square fixes the entire tower. A lift j to the local absolute
Galois group therefore satisfies rho(j^2)=I, although j need not square to1 there.

Consequently U^2=-I. The COEFFICIENT unit eta=(1+w)/2 has norm-1, so V=eta^-1 U is
an integral semilinear involution. Its plus/minus Z7-lattices are exchanged by w.
An integral basis of its plus lattice, adapted to the opposite endpoint, gives

    rho(j g j^-1)=sigma(rho(g))

in ONE global endpoint-preserving integral frame, at every precision. This is an
existential normal form. The frame has not been numerically constructed for the
unknown candidates. Its plus lattice need not be G_K-stable, so it is not ordinary
rank-two Q7 descent. No algebraic realization of the coefficient normalization as
a polarized-variety descent datum is claimed.

## 4. Consequences for the current deformation problem

The actual diagonal characters obey j a_n=sigma a_n, j d_n=sigma d_n, and
j eta_n=sigma eta_n at their full available precision. The exact rank-two trace
obeys T(j g j^-1)=sigma T(g) for every word.

In the normalized frame an auxiliary triangular reference can be chosen with the
same strict symmetry. The ACTUAL nontriangular expression remains
rho=(I+7X)rho0, X=[[p,q],[beta,-p]]. Its coupled cocycle equations are retained,
with additional pointwise covariance X(j g j^-1)=sigma X(g). This does not solve
those equations or replace them by independent Kummer classes.

For the fixed-seven uniformizer probe, the conjugate probe has the same valuation
values. Thus the mixed trace satisfies

    Delta(tau,j g j^-1)=sigma Delta(tau,g).

The previous formula Delta/49=nu7 beta(g) already has this property, because nu7
is rational modulo7. The symmetry does NOT determine nu7 or the missing mixed
trace numerically. The labels must still come from one actual global deformation.

## 5. Nonempty controls and nonclosure

All eight frozen tuples retain their supports and local A/C0 conditions unchanged.
There are1440 finite matrix packets with the new integral comparison, the correct
minus sign, endpoint preservation, and the prescribed mixed-trace formula. Every
packet has nonrational intertwiner entries in its chosen frame. They cover depths
1 through6, c=1,2,7,8,49, both orientations, and three seeds for each pattern.

They are positive MATRIX controls, not representations of the arithmetic Galois
group or Frey realizations. They show why the new structural theorem alone does
not eliminate the patterns. The explicit trace2+7w of U(w)L(7) also disproves the
shortcut from integral semilinearity to an ordinary Q7-valued representation.

## 6. Finite checks

Two implementations import no arithmetic from one another. The primary uses an
omega coefficient basis and2-by-2 arithmetic. The secondary uses theta^2=theta+1,
4-by-4 Z/7^m matrices, separately enumerated F7-linear maps, and Gauss-Jordan inversion.
They agree on the full certificate and its deterministic matrix-set hashes.

|Check|Coverage|
|---|---:|
|All F7-linear endomorphisms of F49|2401|
|Nonzero normalized natural coefficient directions|2304|
|Segment vertices at depths1–8|44|
|Projective-line stability tests|2200|
|Norm-minus-one units modulo7 and49|8 and56|
|Positive integral/semilinear matrix packets|1440|
|Packets with nonrational intertwiner entries|1440|
|Residual patterns eliminated|0|

The original Block74 default replay was observed before development. The final
fresh archive replay and integrity audit are recorded separately outside the
immutable package. Finite checks do not prove the inherited geometry or provide
external mathematical acceptance. No new point counts, Lean, or external reviewer.

## 7. Remaining target

The existence of an integral semilinear comparison of both endpoints is closed
under G1–G4. The numerical realization problem is not. A next global adjoint or
labelled-word calculation can impose this symmetry in one frame, but must still
solve the coupled p,q equations with their actual local conditions, or determine a
mixed trace incompatible with the fixed-seven period value. Arbitrary conductor,
higher depth, the two twists, CM/higher Hilbert branches and full Beal remain open.
