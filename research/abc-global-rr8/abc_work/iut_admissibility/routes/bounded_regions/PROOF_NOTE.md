# Bounded regions, ideal hulls, and the limits of calibration by volume

Checkpoint: ABC-20261025-RR6. Base: the exact RR5 archive with SHA-256
`79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01`.
Owner: `/root/bounded_regions`.

## 1. Contract and scope

This note proves statements about a finite product of local fields and its
integral-module hull. It permits every measurable region in one fixed bounded
ambient ideal. That is an explicit enlargement of any as-yet unverified class
of admissible IUT regions. No identification with the full IUT construction,
its allowed indeterminacies, or its normalized volume is asserted.

Fix a rational prime p and finite extensions K_i/Q_p, for i=1,...,r, with
r>=1. Put A=product_i K_i and O=product_i O_i. Let pi_i be a uniformizer,
v_i(pi_i)=1, and q_i the residue-field cardinality. Use additive product Haar
measure mu normalized by mu(O)=1. A full fractional O-ideal has the form

    I(a) = product_i pi_i^(a_i) O_i,     a_i in Z,
    mu(I(a)) = product_i q_i^(-a_i).

Fix J=I(a), and g=(g_i) in A^times. Set b_i=v_i(g_i) and J_g=gJ=I(a+b).
Multiplication by g has measure factor

    d(g) = product_i q_i^(-b_i),
    mu(gT) = d(g) mu(T)

for measurable T. The O-hull of a subset T is its algebraic O-module span,
denoted H(T). Closure is not silently added to this definition.

Only subsets S of J with 0<mu(S)<infinity are considered, unless an example
explicitly says otherwise. Since J is compact open, the finiteness is automatic.
All such S have a full-rank hull, as proved below.

## 2. Exact hull and target-ideal classification

**Theorem 1.** For such S define

    k_i = min {v_i(s_i) : s in S},      v_i(0)=+infinity.

Every k_i is a finite integer, the minimum is attained, k_i>=a_i, and

    H(S) = I(k),
    H(gS) = gH(S) = I(k+b).                              (1)

Consequently the full fractional O-ideals attainable as H(gS), with S ranging
over the stated measurable regions, are exactly the full ideals contained in
J_g. In coordinates, H=I(h) is attainable exactly when

    h_i >= a_i+b_i       for every i.                    (2)

*Proof.* The subset of J with ith coordinate zero has measure zero, because
a singleton in the nondiscrete local field K_i has Haar measure zero. Positive
measure therefore prevents S from being contained in that subset. Its ith
projection contains a nonzero element. All its nonzero valuations are integers
bounded below by a_i, so they have an attained finite minimum k_i.

Every point of S lies in I(k), giving H(S) subset I(k). Choose, separately
for each i, a point of S whose ith coordinate has valuation k_i. Multiplication
by the ith coordinate idempotent of O isolates that coordinate. Its O_i-span
is pi_i^(k_i)O_i. Summing these coordinate submodules gives I(k) subset H(S).
This proves the first formula. The second follows because multiplication by g
commutes with every O-coefficient in the span.

Equation (2) follows. Conversely, if H subset J_g is a full ideal, choose
S=g^(-1)H. This is a compact open full ideal contained in J, has positive
measure, and satisfies H(gS)=H. QED.

No topological closure issue remains in (1): the algebraic span is already the
compact open fractional ideal I(k).

## 3. Arbitrary raw volume while retaining a fixed hull

**Lemma 2.** Let L be any full fractional O-ideal. For every real t with
0<t<=mu(L), there is a compact measurable T subset L such that

    mu(T)=t,                 H(T)=L.                     (3)

*Proof of the measure choice.* Write D=sum_i [K_i:Q_p]>=1 and N=p^D.
The quotient L/pL has N elements. Its cosets partition L into N compact open
sets of equal measure. Iterating gives N equal-measure children inside each
coset. For any theta in [0,1), expand theta in base N. Select as many children
at the first level as its first digit, continue inside one remaining child,
and at each level select as many of that child's children as the next digit.
The selected cosets are disjoint and their countable union is open in L,
with measure theta mu(L), by the digit expansion. For theta=1 take L itself.

Applying the open-set construction to theta=1-t/mu(L) and taking its complement
in L gives a compact measurable E subset L of measure t. The ideal L is a
principal O-module: x=(pi_i^(ell_i))_i generates it if L=I(ell). Set
T=E union {x}. A singleton has measure zero, so mu(T)=t. Since T subset L
and contains a generator of L, H(T)=L. QED.

The exact raw volume can therefore vary through a real interval even among
compact regions whose hull is fixed. Compactness by itself does not remove
this freedom.

**Theorem 3 (joint raw-volume and hull criterion).** Given a full fractional
O-ideal H and a real tau>0, there exists a compact measurable S subset J with

    H(gS)=H,                mu(gS)=tau                  (4)

if and only if

    H subset J_g,           tau<=mu(H).                 (5)

*Proof.* Necessity follows from gS subset H subset J_g and monotonicity of
measure. For sufficiency apply Lemma 2 inside H with t=tau to get T. Set
S=g^(-1)T. Multiplication by g is a homeomorphism and rescales Haar measure by
the positive finite factor d(g), so S is compact, measurable, and of positive
measure; S subset J. Formula (4) follows. QED.

If S is required to be an O-submodule, positive measure and S subset J imply
H(S)=S by definition and Theorem 1. Then (4) is possible exactly when
H subset J_g and tau=mu(H). The interval of raw-volume freedom in Theorem 3
belongs to general regions, not to integral submodules.

In particular, with no prescribed hull, choosing a region with a target raw
output volume tau is possible exactly when tau<=mu(J_g). Thus a proposed
proof that merely chooses such a region still has to establish that numerical
upper bound. Region selection alone cannot establish it.

## 4. Discrete ideal-hull degrees versus continuous region volumes

For a precise rank-normalized convention, define

    ell_D(T) = (1/D) log mu(T)

for every measurable T of finite positive measure. For full ideal hulls the
attainable values are exactly

    ell_D(J_g) - (1/D) sum_i n_i log q_i,
    n_i in Z_(>=0).                                      (6)

Hence a proposed target hull degree u is attainable exactly when

    D(ell_D(J_g)-u) in
        {sum_i n_i log q_i : n_i in Z_(>=0)}.             (7)

This is stronger than the inequality u<=ell_D(J_g). The set in braces is
locally finite: if its value is at most B>=0, each n_i is at most
B/min_i(log q_i), so there are only finitely many possible tuples. Since all
K_i lie over one prime p, log q_i=f_i log p with integers f_i>=1; the set is
the nonnegative integer semigroup generated by the f_i, multiplied by log p.

In contrast, Lemma 2 shows that raw region values ell_D(gS) with fixed hull
J_g fill the entire interval (-infinity,ell_D(J_g)]. Thus equality of a
region's normalized log-volume with a target does not establish equality of
its hull's degree with that target.

More generally, for independently specified positive weights w_i, the
ideal-only degree ell_w(I(h))=-sum_i w_i h_i log q_i has the analogous
attainable spectrum ell_w(J_g)-{sum_i w_i n_i log q_i}. This does not define
a weighted measure on arbitrary, non-product regions; such an extension
would require its own definition.

The normalization ell_D has the property ell_D(pT)=ell_D(T)-log p. It is a
normalized logarithm of Haar measure. For D>1, exp(ell_D(T))=mu(T)^(1/D)
is not itself additive Haar measure: two disjoint sets of the same positive
measure already show the failure of additivity. This distinction matters
whenever a source describes rank-normalized log-volume using Haar terminology.
No assertion about the source's actual normalization follows without a dictionary.

## 5. The hull operation does not descend through volume equivalence

In A=Q_3, O=J=Z_3 and g=1, let

    T_1 = 9Z_3 union {1},        T_2 = 9Z_3.

Both are compact, measurable and have measure 1/9. They even differ by a
measure-zero set. Nevertheless

    H(T_1)=Z_3,        H(T_2)=9Z_3,
    mu(H(T_1))=1,     mu(H(T_2))=1/9.                     (8)

Thus neither equal raw volume nor equality almost everywhere suffices for
the hulls to have equal volume. The operation taking a measurable region to
the volume of its integral-module hull cannot be defined on the quotient by
equal volume alone, nor on the quotient by equality almost everywhere.

This is a type and ordering check, not an IUT counterexample. A construction
may retain a specific representative until after forming its hull. It may
also restrict representatives enough to make the operation well defined.
Either possibility requires its actual admissibility and equivalence data.

## 6. Consequence for the proposed repair and its remaining leaf

This route tests the proposal to force the native q-pilot value by choosing
an input region with the desired volume. In the present enlarged local model:

* attainable full ideal hulls are exactly those in (2);
* arbitrary raw volumes under a fixed hull have the continuous freedom in (3);
* prescribed raw volume and target hull obey the joint criterion (5);
* a hull-degree target obeys the discrete criterion (7);
* the measure quotient cannot carry the hull operation without more data.

These are exact, elementary results, not finite experiments or novelty claims.
They neither construct nor exclude an admissible S in actual IUT. Our class
of all compact measurable regions is only an outer class. An actual region
must satisfy every further constraint before this classification can be used.

The strongest open leaf is therefore concrete: specify the actual admissible
representatives and their action, identify whether measurement occurs before
or after the hull, and prove that the required native comparison is realized
by one representative whose hull obeys the independently stated bound. The
raw-volume choice and the hull-bound choice must be the same representative.
An equality in a quotient that has forgotten this data does not supply it.

## 7. Evidence and disposition

Universal proofs are supplied above. Equation (8) is an exact arithmetic
counterexample to descending the hull operation through the stated quotients.
No finite computation, external theorem, or proof assistant is load-bearing.

Disposition: the naive raw-volume calibration argument is insufficient for
the desired hull comparison. The full admissibility and IUT compatibility
route remains open. A resumption must use actual admissibility constraints
or a new operation preserving the relevant hull data, rather than repeat the
unrestricted region-selection argument.
