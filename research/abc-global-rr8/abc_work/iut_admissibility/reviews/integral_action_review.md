# Focused audit of the fixed integral-action estimate

**Primary verdict for the corrected claim: proved as written**, on its
bounded, full-Q_p-span hull domain in a nonempty product of local fields.
The source-to-Ind2 application remains conditional and is not passed by
this internal algebra audit.

Reviewer: `/root/rr6_algebra_review`, 2026-10-25. Base RR5 archive SHA-256:
79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01.
The exact original and corrected raw-note hashes are preserved separately
in `integral_action_review_inputs.json`. The earlier finished algebra
review was not edited by this follow-up.

## Claim card

Let A be a nonempty finite product of finite extensions of Q_p, O_A its
maximal compact subring, I a full Z_p-lattice, and J=O_A I. Fix integers
a>=b with p^a J subset I subset p^b J, and a nonempty family G of
Q_p-linear automorphisms preserving I. General regions R lie in the
explicit domain: bounded subsets whose Q_p-linear span is all of A.
Their full O_A-ideal hulls exist.

For q in A^x having the same p-normalized component valuation alpha and
any integer s, put t=floor(s alpha), k=t-(a-b). The displayed estimate is

    phi(union_(M in G) M(q^s I)) subset p^k J.

If k>alpha, this hull cannot contain the native full ideal qJ. For scalar
q=p^m, or q=p^m u with u in Z_p^x, the hull is exactly p^(ms)J, without
the lattice-width loss. The nonhomogeneous variant uses
t=min_i floor(s alpha_i).

## Original domain issue and its correction

The original raw note, SHA-256
e6a345abf396ef68eb65e97c97bf5d6289840b1fc057fdfc8b15ec6d67b1256b,
introduced phi for arbitrary R whenever the smallest fractional ideal
exists, then asserted existence for all sets used below. Its use of
arbitrary R subset p^k I in (1)-(2) did not specify whether degenerate
fractional ideals were allowed.

Under the full-fractional-ideal convention used by the local hull contract,
the original blanket existence assertion is false. Take A=Q_p,
I=J=Z_p, G={identity}, R={0}, k=0. Every full fractional ideal H contains
R, and pH is a strictly smaller full fractional ideal still containing R.
Thus there is no smallest full hull. The historical verdict is therefore
**correct only after the stated domain restriction**, for that intended
full-hull convention. If zero and zero-component fractional ideals are
allowed instead, a bounded set has module hull O_A R and the corresponding
original algebra identities are meaningful. The original note did not
unambiguously select that alternative convention.

Merely requiring R to have nonzero projections would not be stable under
the stated automorphism family. In A=Q_p times Q_p with I=Z_p squared,
the set R=Z_p(1,1) has full O_A-hull. The I-preserving shear
M(x,y)=(x-y,y) sends it to {0} times Z_p, with no smallest full hull.

The correction instead restricts general R to bounded full-Q_p-span sets,
defines phi as a full hull, and checks this domain for the union in (2).
Every invertible M preserves full span. A nonempty union of its images
has full span, and R subset p^k I bounds the entire union uniformly.
This resolves the domain issue and includes the actual R=q^s I used in
the depth estimate. The substantive estimates (3)-(5) did not require a
change. The original note is retained as a snapshot rather than overwritten
without provenance.

The nonempty product convention is also material to the strict exclusion:
the zero algebra would make component-depth hypotheses vacuous. It is not
a local-field packet and is excluded from the corrected claim card.

## Dependency reconstruction

1. A bounded full-span R is contained in a scalar fractional ideal and
   contains finitely many points spanning a full Z_p-lattice. Its O_A-span
   is therefore a full fractional O_A-ideal and is the smallest one
   containing R. This proves existence on the corrected domain.
2. Q_p-linearity and M(I)=I imply M(p^k I)=p^k I for every integer k.
   Multiplication by p^k bijects full fractional ideals and their
   containment conditions, giving phi(p^k R)=p^k phi(R). The definition
   gives phi(I)=J.
3. If R subset p^k I, every image M(R) remains in p^k I subset p^k J.
   The corrected domain makes its nonempty union hull defined, and its
   smallest-ideal property gives (2). No O_A-linearity of M or false
   covariance phi(MR)=M phi(R) is used.
4. In every component, v_i(q^s)=s alpha>=floor(s alpha)=t. Since J is
   a product ideal, q^s J subset p^t J. Multiplying I subset p^b J by
   q^s and p^a J subset I by p^(b+t-a) gives

       q^s I subset p^b q^s J subset p^(b+t) J
                subset p^(b+t-a) I=p^k I.

   Applying step 3 proves (4).
5. Fullness of J makes every component ideal exponent finite. Hence
   qJ subset p^k J is equivalent to alpha>=k in every component. The
   strict k>alpha exclusion follows. With unequal component depths,
   any one component with alpha_i<k excludes native containment.
6. For q=p^m, central scalar linearity gives M(q^s I)=p^(ms)I for
   every M. Nonemptiness of G makes the union exactly that lattice and
   its hull p^(ms)J. A Z_p-unit scalar u preserves I, as do all its
   positive and negative integer powers, proving the stated extension.

## Edge cases and equality

| Obligation | Outcome |
| --- | --- |
| Existence of J and of integers a>=b | Passed by full-lattice commensurability |
| Hull domain in general (1)-(2) | Passed after the explicit bounded/full-span correction |
| Arbitrary nonempty G, including infinite G | Passed; the images have one uniform scalar-lattice bound |
| All integer k, including negative k | Passed; scalar multiplication does not reverse inclusions |
| Rational positive, zero or negative alpha | Passed with v_i(p)=1; component depths need not be integers |
| All integer s, including zero and negative s | Passed because q is invertible and floor(x)<=x for every real x |
| Nonhomogeneous alpha_i | Passed with t=min_i floor(s alpha_i) |
| Nonunit p and strict k>alpha threshold | Passed by componentwise fractional-ideal containment |
| Central p^m and Z_p-unit scalar factors | Passed for all integer m,s |
| General O_A-unit factors | Correctly not asserted to preserve I |
| Actual Ind2 representation and output orbit | Conditional, not supplied by the algebra proof |

At k=alpha, p^k J=qJ, but this outer bound alone does not determine
whether qJ is contained in the actual union hull. Both outcomes occur:
with A=Q_p, I=J=Z_p, G={identity}, q=p, choose a=b=0,s=1 to obtain the
actual hull pJ=qJ. Choose a=1,b=0,s=2 to obtain the same outer k=alpha=1
but the actual hull p^2 J, which does not contain qJ. Both sandwiches
are valid; the second bound simply uses a nonoptimal width. A special
identity such as (5) can thus decide a case that the outer bound cannot.
The corrected wording explicitly makes this distinction.

## Source boundary and review provenance

This review checks the displayed fixed-lattice/module argument only. It
does not independently reconstruct Ism, the source's anabelian comparison,
the induced operator family on actual packets, or the claimed source
attribution. Source transfer requires the fixed-realization interface
stated in the note. Applying the depth estimate further requires that
the actual input is q^s I, or has the proved initial scalar containment,
in that same realization. A uniform global bound on a-b and the full
Ind1-Ind3 output union are not established here.

The first delegated pass inherited parent context. A separate reviewer,
`/root/rr6_algebra_review/isolated_replication`, received only this new raw
proof path and the audit scope, without an author verdict or existing
review. It independently identified the original hull-domain ambiguity,
verified the substantive full-lattice estimates, and reread the corrected
raw note. It found no remaining internal gap on the corrected domain.
It read no route status files, source summaries, or other reviews for this
added task. The final nonempty-product clarification is checked explicitly
in the input record.

No finite mathematical computation or proof assistant was needed or run.
The only shell checks read files and computed SHA-256 hashes. This audit
does not establish the actual IUT compatibility or any global ABC theorem.
