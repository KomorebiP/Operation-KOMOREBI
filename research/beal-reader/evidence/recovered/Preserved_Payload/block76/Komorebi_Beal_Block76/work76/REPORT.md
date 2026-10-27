# Beal research, Block 76
## Exact cyclotomic image at depth one

Release7.6.0,21 September2026. The determinant-one image over the FULL cyclotomic
tower is now determined exactly at actual depth one, under the retained actual
representation hypotheses. It contains the full second principal congruence
subgroup. For all eight retained patterns the group is the same J_F7.

The arithmetic quotient map, local decomposition-group embeddings, the global
adjoint p,q solution and the labelled fixed-seven mixed trace remain unknown.
None of the eight patterns is eliminated. No actual Galois representation or
integer solution is constructed, and the full Beal conjecture is not proved.

## 1. The exact image theorem

Let O=Z7[w]/(w^2-5), k=F49, K=Q(sqrt5), and K_infty=K(mu_(7^infty)).
Put B=beta(G_(K(mu7))), a nonzero F7-subspace of k, with dimension d=1 or2.
In the same normalized natural endpoint frame,

    H=rho(G_(K_infty))
     ={M in SL2(O): M mod7=[[1,x],[0,1]], x in k,
                    (M21/7) mod7 in B}.                 (1)

This is an exact conditional subgroup classification, not a conjecture based
on computed matrix examples. It applies to depth ONE, not arbitrary depth.
The determinant-one restriction uses the exact cyclotomic character, not a
finite approximation to it.

In particular,

    ker(SL2(O)->SL2(O/49)) subset H.                      (2)

The first layer is exactly

    {[[a,z],[b,-a]]:a,z in k,b in B},

of F7-dimension4+d. The next layer and every higher one have the full dimension6.
In Block75's semilinear frame B is F7,wF7,or all k. For the eight bounded all-inert
patterns their separately established ordinary class descent makes B=F7.

See notes/CYCLOTOMIC_JOINT_IMAGE.md, CONGRUENCE_SATURATION.md and EXACT_IMAGE.md.

## 2. Why the actual image is forced to be this large

The three independent global Kummer generators give alpha full k-image. The
nonzero opposite class survives restriction to K(mu7). Conjugation with
cyclotomic value3 acts by3 on alpha and5 on beta. Eigenspace projections separate
the ACTUAL two-coordinate joint image. The commutator[h,g] has exact cyclotomic
value1 and acts on those coordinates by2 and4, both invertible. Thus neither
coordinate loses any value on the full infinite cyclotomic kernel.

In the first congruence layer, conjugating a matrix with nonzero lower entry by
all residual upper unipotents forces the full upper and diagonal k-directions.
Seventh powers carry those directions to the next level. Their commutators with
one nonzero lower direction generate the entire lower k-direction at that level.
Power propagation and a convergent digit correction in the CLOSED actual image
then give the whole second congruence subgroup, not just its associated graded.
The exact first layer finishes the subgroup equality in(1).

No assumption that a pro-seven cyclotomic extension has degree prime to seven is
made. The group proof is elementary and separate from the finite verification.

## 3. Exact finite quotient orders, not a huge exhaustive enumeration

For j>=2,

    |H mod7^j|=7^(6j-6+d),             |H mod7|=49.

For all eight retained patterns d=1:

    |H mod49|=7^7=823543,
    |H mod343|=7^13=96889010407.

Every admissible determinant-one matrix modulo49 has all117649 possible next
determinant-one digits represented somewhere in H modulo343. The group order
7^13 is derived from the written structural theorem; it is NOT a count of
individually enumerated matrices or Galois realizations.

Equivalently, these are the degrees of the finite torsion extensions over the
infinite base K_infty, IF an actual representation satisfying the hypotheses
exists. No defining polynomial or arithmetic quotient map has been computed.

## 4. Exact abelianization and the global uniformizer

The closed commutator subgroup is the kernel of the two endpoint coordinates.
Consequently,

    H_ab = k direct-sum B.

For the eight patterns this has order343 and exponent7. The global Kummer class
[7] is independent of the three old natural generators. If it factored through
H, its chi-weight would eliminate the beta component of any abelian functional,
leaving an impossible expression in alpha alone. Therefore

    K_infty(7^(1/7)) is NOT contained in K_infty(J[7^infty]).

This is a GLOBAL field statement. It does not assert local noncontainment or
zero local period valuation. The finite probe matrix can lie in the reduction of the commutator
subgroup while its mixed trace is nonzero. That trace is not an abelian
character. See notes/ABELIANIZATION_AND_UNIFORMIZER.md.

## 5. Why no bounded pattern is eliminated

For a in k and nonzero b in B, the matrices

    T_a=[[1,7a],[0,1]],           G_b=[[1,0],[7b,1]]

belong to the exact image and satisfy

    tr(T_a G_b)-tr(T_a)-tr(G_b)+2=49ab modulo343.

All49 leading residue values occur. This does NOT allow us to replace the actual
local uniformizer probe by an arbitrary element T_a, or to change a fixed labelled
Galois element freely. The preimages can be different elements, and their local
membership is not given by the image subgroup alone.

The eight old conductor/character patterns and their A/C0 constraints remain
unchanged. The next arithmetic task is the global quotient map and its compatible
local embeddings, not the shape of the unlabelled cyclotomic matrix-image group.

Two other invalid strengthenings are explicitly excluded: when B=F7, L(7w) is
not in the image, so the full FIRST congruence subgroup is not forced. At depth3,
a subgroup with lower ideal343O need not contain L(49); the depth-one hypothesis
cannot be dropped. Full residual U(k), rather than a single F7 direction, is also
essential. See notes/MIXED_TRACE_BOUNDARY.md.

## 6. Finite evidence

The primary program uses a w-basis, explicit conjugation identities, modular
row reduction and binary powering. The separate program uses a phi-basis,
full matrix conjugation, fraction-free integer minors, Gauss-Jordan inversion
and repeated multiplication. Neither imports arithmetic from the other.

|Finite check|Coverage in each implementation|
|---|---:|
|Trace-zero field seeds with nonzero lower entry|115248|
|Even/odd unipotent conjugation instances|345744|
|First- and second-layer rank certificates|48 nonzero lower seeds|
|Complete traceless first-layer membership enumeration|117649|
|Exact mixed-characteristic second-layer commutators|2352|
|Exact derived-subgroup commutators|2352|
|Seventh-power propagation instances at six tested levels|882|
|Joint-image projection/commutator coordinate tests|2401|
|Abelian functional eigenspace tests|2744|
|Mixed-trace values|294|

The all-precision group statements and fourth-Kummer-coordinate noncontainment
are separate written proofs, not extrapolations from these checks. Fresh output
regeneration, corruption tests, predecessor hashes and final archive integrity
are recorded in the external final audit. No new Frobenius count, Lean run,
independent mathematical reviewer, or actual labelled mixed trace was produced.

## Remaining obligations

Conditional image classification at depth one is closed. Global arithmetic
realization, labelled local embeddings and adjoint compatibility are not.
Higher depths, unrestricted conductors, the minus component, independent upstream
acceptance, CM/higher Hilbert branches, full signature and full Beal remain open.
