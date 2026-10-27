# The dyadic quotient: exact capacity, low-rank failure, and a numerical-profile counterexample

Status: ordinary proof from the supplied actual defining sequence and the retained primary Bushnell–Kutzko results. No Lean or numerical computation is used. This note calculates the quotient of an actual simple type. It does not prove universal H5 or identify an explicitly constructed host with the source-defined arithmetic candidate.

## 1. Exact hypotheses and result

Let F=F_2((t)). Fix d>=1 and increasing positive odd integers

    h_1<...<h_d,       q_i=3h_i,       n=2^d.

Suppose the actual arithmetic constructor supplies a full-degree totally ramified parameter beta on the complete period-n chain, with actual approximating fields of degrees

    2,4,...,2^d

and ambient critical levels

    nu_j=2^(d−j) q_(d−j+1),       1<=j<=d.

These are the supplied dyadic specialization of the recursive tower's field/profile conclusions. The calculation applies equally to the original polynomial tower of Block166 and to an Artin–Schreier variant once that variant's field/profile conclusions are established. No trace-zero assertion is needed here.

The exact actual Heisenberg quotient is

    dim_F2(J^1/H^1)=2^d−2,
    dim eta=2^((2^d−2)/2).

Consequently its symplectic dimension is at least the 2d dimensions of the whole d-plane source packet exactly when d>=3. In rank8, d=3, the quotient has dimension6 and eta has dimension8: the source carrier fits exactly, with no complementary Heisenberg factor needed.

| d | Ambient rank | Actual quotient dimension | eta dimension | Whole source dimension | Capacity |
| --- | --- | --- | --- | --- | --- |
| 1 | 2 | 0 | 1 | 2 | Fails |
| 2 | 4 | 2 | 2 | 4 | Fails |
| 3 | 8 | 6 | 8 | 8 | Exact |
| 4 | 16 | 14 | 128 | 16 | Sufficient |
| general | 2^d | 2^d−2 | 2^(2^(d−1)−1) | 2^d | Sufficient iff d>=3 |

This improves the leading-layer-only sufficient threshold d>=4 to the exact whole-profile threshold d>=3. It also exposes a genuine low-rank limitation of this proposed whole-carrier realization.

## 2. Floors and ceilings in the actual BK orders

Write P=rad(A), and let B_j be the A-centralizer of the degree-2^j approximation. Its complete-chain grade has F_2-dimension

    b_j=2^(d−j),       b_0=n.

Put

    a_j=ceil(nu_j/2),       t_j=floor(nu_j/2)+1.

The exact BK definitions, 3.1.7–8, use a_j as the J cutoff and t_j as the H cutoff. Thus a_j=t_j for an odd critical level, while t_j=a_j+1 for an even critical level.

The increasing h_i give

    nu_j>2 nu_(j+1),       1<=j<d.

This strict separation is useful: the centralizer approximation estimate from BK 3.1.5 puts each newly introduced centralizer into the preceding one modulo a term above the preceding half-level. In the notation of these stages, the relevant error level is nu_j−nu_(j+1)>nu_j/2. Therefore the successive grade dimensions really are b_j; there is no unproved assumption that the approximation fields are literally nested inside the final field.

Applying the ring recursion gives the J-grade staircase:

* below a_d the grade dimension is b_d=1;
* on a_(j+1)<=k<a_j it is b_j;
* from a_1 upward it is b_0=n.

The H staircase uses the corresponding t_j. Hence the exact contribution of transition j to J^1/H^1 is

    (b_(j−1)−b_j) · 1_(nu_j even).

One can also obtain this by subtracting the exact logarithmic indices of H and J in 1+P. It is an equality of the group index |J^1/H^1|, not a guess from the visible leading matrix support. BK 3.4.1 makes the resulting commutator pairing nondegenerate.

For j<d the level nu_j has a factor of2 and is even. The final level nu_d=q_1 is odd. Therefore

    dim_F2 J^1/H^1
      =sum_(j=1)^(d−1) (2^(d−j+1)−2^(d−j))
      =2^d−2.

The omitted final increment would have dimension1. It cannot be treated as a symplectic plane or silently restored: at that odd level the two defining lattice cutoffs are exactly equal. Its disappearance is also consistent with the even dimension required of a nondegenerate alternating space.

The source packet requires dimension2d. At d=1,2, 2^d−2<2d. At d=3 equality holds. If the inequality holds for d>=3, then

    2^(d+1)−2−2(d+1) = (2^d−2−2d)+(2^d−2)>0,

so it continues to hold for every larger d. This proves the exact threshold.

## 3. Conductors still match despite the lost final contribution

This section reuses the same retained formal-degree and self-pair conductor identities already audited in Blocks161 and165. It is not needed to prove the dimension formula, but shows why numerical conductor checks do not expose the low-rank capacity failure.

Put Delta_j=b_(j−1)−b_j. The exact grade count gives

    I=log_2[(1+P):J^1]
      =sum_j Delta_j ceil(nu_j/2)−(n−1).

For this profile only the final level is odd and Delta_d=1. Therefore

    2I=sum_j Delta_j nu_j+1−2(n−1).

The Heisenberg dimension exponent is D/2, where D=n−2. The retained formal-degree identity for a full-degree, totally ramified, torsion-one maximal type gives

    a(Pi^vee×Pi)=n^2−1+(n−1)+2I+D.

Substitution yields exact cancellation of the odd-cutoff correction:

    a(Pi^vee×Pi)=n^2−1+sum_j Delta_j nu_j
               =2^(2d)−1+sum_(i=1)^d 3·4^(i−1) h_i.

The ordinary conductor is n+nu_1, so Swan(Pi)=2^(d−1)·3h_d, and the torsion number is one. These are the usual three numerical invariants of the stipulated independent dyadic Heisenberg tensor source.

Thus all three numerical invariants can match while eta is too small for the whole source carrier at ranks2 and4. This is a capacity failure, not a conductor mismatch. It does not by itself refute any original H1–H5 statement.

## 4. Rank2 failure is forced by Swan and torsion alone

Let Pi be any actual supercuspidal representation of GL2(F) with torsion number one and odd Swan exponent N=3h_1. BK 6.2.5 forces its maximal parameter field K/F to be totally ramified of degree2 and its hereditary order to have complete period2. The ordinary conductor formula then fixes its native level as N.

Every parameter beta of a maximal simple type in Pi has v_K(beta)=−N, which is odd. Since the residue extension is trivial, BK 1.4.14–15 say beta is minimal over F. The two order definitions are therefore

    J_order=O_K+P^ceil(N/2),
    H_order=O_K+P^(floor(N/2)+1).

The exponents coincide because N is odd. Hence J^1=H^1, eta is one-dimensional, and no two-dimensional symplectic source plane can embed into this quotient.

This proves failure for every maximal simple type of every candidate with these two invariants. It is stronger than failure of one explicit matrix formula. It remains a statement about attachment inside the actual maximal-simple-type Heisenberg carrier, not a proof that no other arithmetic realization relation could work.

## 5. Rank4 failure is also forced by Swan and torsion

Let Pi be any actual supercuspidal representation of GL4(F) with torsion number one and Swan exponent N=6h_2, where h_2 is odd. Its maximal parameter field is totally ramified of degree4, its order has period4, and its native level is N.

Here v_2(N)=1. The defining-sequence/minimality argument of Block166 forces the terminal minimal approximation field E/F to have degree2. There is no possible intermediate degree between2 and4. The scalar terminal case is excluded by 4 not dividing N, and a minimal full-degree4 parameter is excluded because gcd(N,4)=2. Thus the actual degree pattern is forced to be 4→2.

Write c=−k_0(beta,A), so 1<=c<N. Select the critical approximation furnished by the construction in BK 2.4.1 and the remark preceding 2.4.7. Because the original field is maximal, this approximation can be selected with a simple maximal derived stratum in B=End_E(F^4)≅M2(E). Equivalently one can replace its derived stratum by an equivalent simple representative and use BK 2.2.2–3. The derived field has degree2 and ramification index2 over E. A simple stratum [B_order,c,c−1,alpha] is minimal. Since the complete B-chain has period2 and the derived field is totally ramified, BK 1.4.14 forces

    gcd(c,2)=1.

Therefore c is odd. It cannot be made even while preserving this degree pattern and a genuine maximal derived field.

Let j=(c+1)/2. The actual orders are

    J_order=O_K+Q^j+P^(N/2),
    H_order=O_K+Q^j+P^(N/2+1).

The final low transition contributes nothing, while the high transition has dimension4−2=2. Thus every such Pi has

    dim_F2 J^1/H^1=2,       dim eta=2.

The desired two-plane source carrier has dimension4, so it cannot be a sector of this eta. Requiring the self-pair conductor additionally fixes c=3h_1 through

    a(Pi^vee×Pi)=15+2N+c,

but is unnecessary for the capacity failure.

## 6. Rank8: the three invariants do not force the good profile

The full 2→4→8 tower has quotient dimension6 and enough capacity. Nevertheless Swan, torsion number and self-pair conductor alone do not force that degree pattern. Here is an actual skipped-degree arithmetic construction with the same three numerical invariants and a smaller quotient.

Fix increasing odd h_1<h_2<h_3 and put

    q=3h_3,       N=4q=12h_3,       c=h_1+4h_2.

Then c is odd and 0<c<N; indeed c<5h_3, so even 2c<N.

Construct the separable totally ramified quadratic extension

    E=F(alpha),       alpha^2+alpha=t^(−q).

Put a=(q+1)/2 and z=t^a alpha. Then z is a uniformizer and

    z^2+t^a z+t=0.

The element alpha has E-valuation −q and is minimal over F. On E^4, gamma=alpha I_4 is minimal of ambient level N in the complete period-eight order A.

Now construct the separable Eisenstein quartic extension over E

    L=E(e),       e^4+z e+z=0,

and let C be multiplication by e^(−c) on L as a four-dimensional E-space. Since c is odd, e^(−c) is minimal, generates L/E, and defines a simple maximal derived stratum [B_order,c,c−1,C].

Let P0 extract the coefficient of1 on each E-coordinate in the basis 1,z. The normalized outer corestriction from the Artin–Schreier right-inverse calculation has

    s(P0)=t/z^2.

Consequently the explicit F-linear lift

    b=(z^2/t) C P0

satisfies s(b)=C and has valuation −c. Define the actual rank-eight matrix

    beta=alpha I_4+(z^2/t) C P0.

BK 2.2.3 applies because gamma is simple at level c<N and the derived stratum is simple maximal. It proves that F[beta]/F is totally ramified of degree8, normalizes the complete chain, has leading level N, and has critical exponent −c. Its defining degree pattern is 8→2, skipping degree4.

Since N is even and c is odd, the actual Heisenberg quotient has dimension

    (8−4)·1+(4−1)·0=4,

so eta has dimension4. Yet its invariants are

    Swan=N=12h_3,
    torsion=1,
    a(Pi^vee×Pi)=63+4N+3c
                 =63+48h_3+12h_2+3h_1,

exactly the same as the full three-stage profile. Any maximal simple character and its standard type completion give an actual supercuspidal Pi with these values. The required full three-plane source carrier would have dimension8, larger than this eta.

This is an arithmetic counterexample to the proposed implication from those three numerical invariants to adequate rank-eight Heisenberg capacity. It is not an H5 counterexample, does not identify the skipped host with the source-defined classical candidate, and does not claim that it preserves the supplied full source characters.

## 7. Which repairs have actually been tested

### Replacing the displayed type or parameter at fixed Swan and torsion

At ranks2 and4 this fails by Sections4–5 for every maximal simple type satisfying those invariants. A new matrix search or a different critical coefficient cannot manufacture the missing quotient dimensions.

At rank8 the full tower supplies the good profile, but the three invariants alone do not force it inside a separately selected candidate. Section6 proves the failure of that proposed inference with an explicit actual host. A finer endo-class or ramification comparison would be needed for that same-candidate assertion.

### Skipping approximation degrees or changing critical parity

At rank2 there is no degree to skip. At rank4 the level excludes both a scalar minimal approximation and a full-degree minimal approximation. The remaining quadratic derived step has odd critical exponent by minimality. Thus neither skipping nor declaring that exponent even is a valid repair at fixed invariants.

At rank8 a degree skip is genuinely possible, but it decreases capacity in the explicit example above.

### Scalar twists, shallow or deep

A scalar twist of the existing actual inducing representation does not increase its dimension. The exact Block164 pushout transport identifies the same quotient J/H and leaves its commutator pairing unchanged. Thus it cannot turn an insufficient eta into a whole source carrier.

For an actual parameter, replacing beta by beta+aI with a∈F leaves its field, centralizer and commutator map unchanged. A shallow scalar addition does not change the leading level. A dominating scalar addition can change that level, but it contributes no new noncentral Heisenberg directions: in the defining sequence the added scalar stage has equal H and J orders. This agrees with the exact representation-level twist transport. Enlarging a displayed numerical level is therefore not a capacity repair.

This paragraph does not assert that every arbitrary scalar character twist is represented by one globally specified additive parameter. The already proved group/representation transport suffices for its negative capacity conclusion.

### Adding residue multiplicity or increasing ambient rank

The torsion-one condition forces a full-degree totally ramified parameter field and residue multiplicity one. A host with an unramified or residual multiplicity factor does not preserve that invariant. Increasing the ambient rank changes the required source rank. Neither maneuver closes the current fixed-rank construction.

### Using a larger arithmetic carrier inside the same representation

A larger compact subgroup representation, a genuinely different arithmetic quotient, or an induction-stage carrier might have enough dimension. Such an enlargement is not ruled out here. It would need an actual finite Heisenberg action carrying the prescribed full source data and a proved recovery in the unchanged candidate. Artificially adding vector-space copies or transporting abstract operators to an induced space does not provide that arithmetic attachment or prove its kernel compatibility. No such repair is constructed in this note.

## 8. Quadratic refinements and marked centers

For d>=3, the dimension result gives a symplectic embedding of the source quotient into the actual host quotient. With C trivial, a C×-central pushout can then be matched by its alternating commutator, and Stone–von Neumann supplies the corresponding source sector. This is the same finite scalar-pushout attachment contract used previously.

At p=2, that statement must not be promoted to an identification of arbitrary preselected native quadratic refinements. The C× pushout permits rescaling lifts by i and can identify the pushouts of the dihedral and quaternion extraspecial planes, even though their native square functions differ. A chosen source embedding can preserve that source's full finite central extension and its character values. It does not thereby identify a separately marked target mu_2 extension or its Arf invariant.

In particular, symplectic-isotropic reduction respects a prescribed quadratic form only when the reduced subspace is totally singular for that form. The retained DYADIC_AND_WEAK_ATTACHMENT159.md gives the exact quadratic/Arf obstruction. Additional source or target marked centers, chosen lifts, quadratic refinements and nontrivial stabilizer actions therefore require their own comparison. They are neither erased from the task nor supplied by a dimension inequality.

## 9. Scope and source provenance

The strongest proved conclusion is exact capacity for the specified actual full defining profile, together with invariant low-rank failures and an explicit rank-eight counterexample to numerical profile forcing. No universal impossibility for original Theorem16.2 is asserted. In particular this note supplies no complete original H1–H5 counterexample and does not decide whether that endpoint requires this precise whole-maximal-type-carrier realization.

Primary source directly reread: Bushnell–Kutzko, *The admissible dual of GL(N) via compact open subgroups*, 1.4.14–15; 2.2.2–3; 2.4.1–2 and the maximal-field remark immediately preceding 2.4.7; 3.1.5, 3.1.7–9; 3.2.1–4; 3.4.1; 6.2.5 and its following paragraph.

Authorized retained text:

    closure_recovery/extracted/Paper_XI_Continuation158_General_Sectors_and_Arithmetic_Constraints/scratch158/information158/input_cache/BK_source.txt
    SHA256 d69db0827256707a34cd2562af68b9de11fc889ab3f43535ec47b620d58ca9c8

Internal inputs reused at their stated scope:

* attachment166/tower/RECURSIVE_TOWER166.md: actual defining degrees, levels, filtered right inverse and separated grade count; its field constructor permits p=2.
* attachment166/tower/TRACE_ZERO_AS_TOWER166.md, Sections1–2: normalized corestriction and explicit right inverse. Their algebraic formulas apply at p=2; the odd-prime trace-zero assertion is not used.
* attachment166/capacity/LEADING_LAYER_CAPACITY166.md: the leading subspace argument and the minimal terminal degree calculation.
* base_realization165/polarization/PROFILE_RIGIDITY165.md and closure_recovery/full161/scratch161/placement161/ADJOINT_CONDUCTOR_TEST161.md: retained formal-degree/self-pair conductor identities and normalization.
* input_pair164/TWIST_TRANSPORT.md: exact character-twist/pushout transport.
* closure_recovery/extracted/Paper_XI_Continuation159_Type_Completion_and_Sector_Recovery/scratch159/coverage159/DYADIC_AND_WEAK_ATTACHMENT159.md: distinction between symplectic and marked quadratic reduction.

No full copyrighted source is redistributed here. No new external correspondence theorem or H5 premise is introduced.
