# Compact-open calibration still does not determine the integral hull

Checkpoint ABC-20261025-RR6, based on RR5 archive SHA-256
`79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01`.
This is a separate extension of PROOF_NOTE.md, whose reviewed revision is
unchanged. The definitions are those of that note: A is a finite product of
finite extensions of Q_p, O its product valuation ring, J a full fractional
O-ideal, g in A^times, and mu(O)=1 for additive Haar measure.

The extra restriction tested here is that regions must be compact open in A.
This note does not claim that every such region is an admissible IUT output.
No dictionary to the full Ind1, Ind2 or Ind3 restrictions is supplied.

## Exact joint criterion for compact-open regions

Let H be a full fractional O-ideal and tau>0. There exists a compact-open
S subset J with

    H(gS)=H,                    mu(gS)=tau                 (1)

if and only if

    H subset gJ,                tau/mu(H) in Z[1/p] cap (0,1].   (2)

Here Z[1/p]={a/p^n : a in Z, n>=0}. This refines the arbitrary compact
measurable-region criterion, where every real ratio in (0,1] was allowed.

*Necessity.* The hull classification in PROOF_NOTE.md gives H subset gJ,
and gS subset H. Put D=sum_i[K_i:Q_p] and N=p^D. Every nonempty compact-open subset
T of H is a finite union of cosets of p^n H for some n>=0. Indeed openness
supplies one translated basic subgroup around each point of T; compactness
gives a finite subcover; replacing their subgroup powers by their maximum
expresses the set as a union of cosets of one common subgroup. Each coset
has measure mu(H)/N^n. Hence mu(T)/mu(H)=M/N^n for an integer
0<M<=N^n, which lies in Z[1/p] cap (0,1]. Apply this to T=gS.

*Sufficiency.* Write tau/mu(H)=M/N^n with 0<M<=N^n, taking n>=1
large enough to clear its p-power denominator. The ideal H is generated
as an O-module by x=(pi_i^(h_i))_i when H=I(h). Choose M cosets of
p^n H in H, including the coset x+p^n H. Let T be their union. Then T
is compact open, has measure tau, is contained in H, and contains x, so
H(T)=H. Set S=g^(-1)T. This proves (1). QED.

Thus the attainable compact-open raw volumes form the expected p-power
rational set. That restriction still leaves many different regions with
the same raw volume and different hulls.

## A compact-open counterexample to descent through equal volume

Take A=Q_3, O=J=Z_3 and g=1. For every integer m>=2, set

    S_1(m)=3^m Z_3 union (1+3^m Z_3),
    S_2(m)=3^m Z_3 union (3^(m-1)+3^m Z_3).

Both sets are compact open subsets of Z_3. Within each union the two
cosets are disjoint, and each coset has measure 3^(-m). Therefore

    mu(S_1(m))=mu(S_2(m))=2*3^(-m).                       (3)

The shifted coset in S_1(m) consists of units. Hence its O-module hull
is Z_3. The shifted coset in S_2(m) consists of elements of valuation
exactly m-1, while the unshifted coset has valuation at least m. Hence

    H(S_1(m))=Z_3,
    H(S_2(m))=3^(m-1)Z_3.                                (4)

Their hull log-volumes differ by

    log mu(H(S_1(m)))-log mu(H(S_2(m)))
        =(m-1)log 3,                                    (5)

which is unbounded as m grows. At m=2 the example is

    9Z_3 union (1+9Z_3),
    9Z_3 union (3+9Z_3),

with common measure 2/9 and hulls Z_3 and 3Z_3.

Consequently the operation taking a compact-open region to the volume of
its O-module hull does not descend through the quotient by equal raw
volume. This conclusion now uses only compact-open regions, rather than
the null-singleton modification in the earlier note.

This is not a counterexample involving equality almost everywhere: distinct
compact-open sets in a local field have a nonempty open symmetric difference,
and therefore a symmetric difference of positive measure. The equal-volume
claim and the almost-everywhere claim must not be conflated.

## Scope of the diagnostic

Compact openness alone cannot repair the loss of hull information in a
quotient that remembers only raw volume. A valid construction may instead
keep representatives until after taking their hull, or impose additional
admissibility restrictions that exclude the displayed pair. Those are
source-dependent mathematical obligations to check separately.

The proof is elementary and universal in its stated model. No finite
computation, novelty claim, or full-IUT conclusion is asserted. The exact
source-to-model dictionary and realization by an actually admissible region
remain open.
