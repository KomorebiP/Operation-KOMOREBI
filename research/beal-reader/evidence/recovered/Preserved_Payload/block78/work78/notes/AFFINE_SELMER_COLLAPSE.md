# B78.3. What happens to the Block 77 affine Selmer stages

This note combines B77.2 with B78.2. It isolates what pure cohomological local
matching can and cannot obstruct.

## Stage P

Fix any global solution p0 of

    dp0=-alpha cup beta.

Such a p0 exists by the inherited cup-zero theorem. Let S be any finite set of
places and, for each v in S, choose a local solution p_v of the same first-stage
equation satisfying the desired local geometric condition. Then

    z_v=p_v-p0|_v

is a k-valued local 1-cocycle. By B78.2a there is z in H^1(K,k) with z|_v=z_v
for every v in S. Because k has trivial action there are no local coboundaries.
Thus

    p=p0+z

matches the chosen local cochains EXACTLY at every place of S.

In particular, all finitely many toric hyperplanes from B78.1 can be matched
simultaneously, provided each is locally nonempty. The theorem can also leave p
unchanged at an arbitrary additional finite set T.

## Stage Q

Fix such a p. Suppose the local secondary H^2 class vanishes at every place.
Block 77's localization theorem then gives one global q0 with

    d_chi q0=R_p.

Choose at a finite set S local solutions q_v satisfying the desired local
conditions. The differences

    z_v=q_v-q0|_v

are local k(chi)-cocycles. By B78.2b their cohomology classes are the restrictions
of one global z in H^1(K,k(chi)). Hence q=q0+z realizes every chosen local
STRICT-EQUIVALENCE class.

A local coboundary in k(chi) is exactly the change induced at first order by a
strict upper conjugation I+7y E12. Consequently any local condition invariant
under that strict equivalence -- in particular trace conditions and the labelled
mixed-trace value -- can be matched at finitely many places once it is locally
attainable.

## Consequence

There is no finite-place affine H^1 localization obstruction for the modules
that occur in the Block 77 P and Q stages if auxiliary ramification is allowed.
The nonhomogeneous fixed-seven target is stronger than Block 70's homogeneous
Frobenius sieve, but it is still one finitely prescribed local cohomological
condition and therefore is not, by itself, a global Selmer obstruction.

This does NOT say that an actual Frey deformation exists. The global correction
provided by localization may ramify at new places, and the actual integral frame
may impose representative-sensitive constraints not captured by strict local
equivalence.
