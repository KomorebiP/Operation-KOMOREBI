# Homogeneous tensor packets and factor permutations

Checkpoint: ABC-20261025-RR6. Base checkpoint RR5 archive SHA-256:
`79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01`.
Owner: `/root/iut_numeric_bridge`. Date checked: 2026-10-25.

This note proves a local algebra statement about an explicitly homogeneous
tensor packet. It does not identify this packet with every original-IUT packet,
classify all of (Ind1), or analyze (Ind2) and (Ind3). In particular, factor
permutations inside one tensor product are not arbitrary permutations of
coordinates belonging to different procession stages.

## 1. Exact objects and hull

Let `F=Q_p`, let `K/F` be a finite extension, let `r>=1` be an integer, and put

    A = K tensor_F ... tensor_F K                 (r factors).

Let `G` be any subgroup of the factor-permutation group `S_r`. For `q in K^x`,
write `q_i` for `1 tensor ... tensor q tensor ... tensor 1`, with `q` inserted
in factor `i`. It belongs to `A^x`, with inverse given by the insertion of
`q^(-1)`.

Since `K/F` is separable, `A` is a finite product of finite extensions of `F`:

    A = product_(lambda in Lambda) L_lambda.

For completeness, one can prove this by writing `K=F[t]/(f)` with `f`
separable and inducting on `r`. Tensoring a field factor `L` with `K` gives
`L[t]/(f)`; over `L` the polynomial is a product of distinct irreducibles, so
the Chinese remainder theorem gives a product of fields. The ring

    O_A = product_lambda O_(L_lambda)

is the integral closure of `Z_p` in `A`. Integrality can be checked component
by component in this finite product.

For a subset `U` of `A`, define its module hull by

    phi(U) = O_A U
           = { sum_(k=1)^n a_k u_k : n>=0, a_k in O_A, u_k in U }.

This is the smallest `O_A`-submodule of `A` containing `U`. No measure enters
this definition. Let `J=phi(U)`. When finite volume or a fractional-ideal
description is needed below, assume `U` is bounded and its `F`-linear span is
all of `A`. Then `J` is a full lattice: it is contained in `p^(-N) O_A` for
some integer `N` by boundedness, and it contains the `Z_p`-span of an `F`-basis
chosen in `U`. In particular it contains `p^M O_A` for some integer `M`.
As an `O_A`-module it is a full fractional ideal of the product of DVRs.

## 2. Componentwise insertion valuations

Fix on every finite extension of `F` the unique absolute value extending
`|p|_p=p^(-1)`. The existence and uniqueness used here are the standard
complete-field extension theorem. A checked primary exposition is J. S. Milne,
*Algebraic Number Theory*, v3.08, 19 July 2020, Theorem 7.38, printed p.123
(PDF page index 124), at
<https://www.jmilne.org/math/CourseNotes/ANTc.pdf>.
The statement and hypotheses were checked directly on 2026-10-25, extraction
reference `turn75view1`, lines 7650--7676. The PDF bytes were not retained in
this route. Milne's displayed norm formula is not required separately.

For every component projection `pi_lambda:A->L_lambda`, insertion into factor
`i` gives an `F`-algebra embedding

    iota_(i,lambda): K -> L_lambda.

Indeed, this is a unital map from the field `K`, and so is injective. Pulling
back the absolute value on `L_lambda` along this embedding yields an absolute
value on `K` extending the one on `F`. Uniqueness therefore gives

    |iota_(i,lambda)(q)|_(L_lambda) = |q|_K             (1)

for every `i` and `lambda`.

**Lemma 1.** For any `i,h`,

    q_i/q_h in O_A^x,      q_i O_A = q_h O_A.          (2)

*Proof.* In component `lambda`, the quotient has absolute value one by (1),
so it is a unit of `O_(L_lambda)`. A tuple is a unit of `O_A` precisely when
all of its components are units. Multiplying the unit relation by `q_h`
proves the principal-ideal equality. QED.

The lemma is unchanged if `q` is replaced by `q^m`, for any integer `m`.
It requires that the inserted element is the same element of the same local
field, with each factor over the same fixed `Q_p`.

## 3. Equivariant hull and the exact orbit formula

Each `sigma in G` is an `F`-algebra automorphism of `A` and preserves `O_A`:
an automorphism preserves integrality over `Z_p`. It follows directly from
the definition that, for every subset `V` and every `a in A^x`,

    phi(sigma(V)) = sigma(phi(V)),
    phi(a V) = a phi(V).                               (3)

The second equality uses commutativity of `A`. Module hulls also satisfy

    phi(union_alpha V_alpha) = sum_alpha phi(V_alpha),  (4)

where the sum on the right means all finite sums of module elements.

Adopt the convention `sigma(q_i)=q_(sigma(i))`. Reversing this convention
only replaces the indexing permutation by its inverse.

**Theorem 2 (exact orbit-hull identity).** For every subset `U` and
`J=phi(U)`,

    phi(union_(sigma in G) sigma(q_i U))
       = q_i sum_(sigma in G) sigma(J).                 (5)

In particular, if `sigma(J)=J` for every `sigma in G`, then

    phi(union_(sigma in G) sigma(q_i U)) = q_i J.        (6)

*Proof.* Equations (3)--(4) give

    phi(union_sigma sigma(q_i U))
       = sum_sigma q_(sigma(i)) sigma(J).

By Lemma 1, `q_(sigma(i))=q_i u_sigma` for some `u_sigma in O_A^x`.
Every `O_A`-module is unchanged when multiplied by an `O_A`-unit, so each
summand is `q_i sigma(J)`. This proves (5). Under the invariance hypothesis,
the sum of the modules `sigma(J)` is `J`, which proves (6). QED.

The identity also holds with every `q_i` replaced by `q_i^m`. No boundedness
or fullness hypothesis is needed for (5)--(6). Those assumptions ensure that
the resulting hulls are full lattices if a later numerical invariant requires
that domain.

This proof exhibits all properties of the hull that are being used. It cannot
be applied to a different operation merely because that operation is also called
a hull. For a more general closure operator, one must establish the analogues
of (3)--(4), closure under `O_A`-units, and invariance of the original hull.

## 4. Exactly what can and cannot be enlarged

The formula (5) separates two effects. Permuting the inserted `q` changes it
only by a unit after integral closure. Any enlargement beyond `q_i J` comes
from replacing `J` by its symmetrization `sum_sigma sigma(J)`. Under the
assumed invariance, that enlargement is zero. Invariance of `J` is therefore
an actual hypothesis; it is not being inferred from equality of principal
insertion ideals.

Now suppose `J` is a full lattice, and `q` is not a unit of `O_K`. For any
integers `m,n`,

    q_i^m J = q_i^n J   if and only if   m=n.           (7)

To prove this, choose a uniformizer `varpi_lambda` of each `L_lambda` and write
`J=product_lambda varpi_lambda^(a_lambda) O_(L_lambda)`.
For the integer-normalized valuation `ord_lambda`, equality implies

    (m-n) ord_lambda(iota_(i,lambda)(q))=0

in every component. By (1), all these inserted values have nonzero valuation
when `q` is a nonunit of `O_K` in the sense `|q|_K != 1`. Therefore `m=n`.
The converse is immediate. Here and below, "nonunit" for an arbitrary
`q in K^x` means `|q|_K != 1`, so it includes inverses of nonzero nonunits.

If `0<|q|_K<1` and `m>n`, then

    q_i^m J is a proper subset of q_i^n J.             (8)

Every component valuation increases strictly, proving both containment and
strictness. If `|q|_K>1`, containment reverses. For a unit `q`, the two hulls
coincide for all `m,n`, but there is no positive insertion depth to reduce.

Consequently, in a fixed homogeneous packet with invariant `J`, replacing `q`
by its `j^2`-th power retains that exact power in (6). For `j>=2` and
`0<|q|_K<1`, factor permutations followed by the stated hull do not transform
`q_i^(j^2) J` into `q_i J`. The assertion is about a fixed integer `j`; it
does not permit permutations between different stage labels.

## 5. Weighted numerical consequences without a Haar convention

Equality of hulls in (6) implies equality under every numerical function that
is defined on these hulls. Thus one does not need to replace a source's
procession-normalized determinant or weighted log-volume by ordinary Haar
measure to conclude that this particular orbit-hull operation leaves its value
unchanged. The numerical function and its domain must first be defined.

A fully explicit optional invariant makes the retained power visible. Normalize
`v_lambda(p)=1`, let the full fractional ideal `J_lambda` have threshold
`t_lambda` in `(1/e_lambda) Z`, and fix weights `w_lambda>=0` whose sum is
positive. Define

    d_w(J) = sum_lambda w_lambda t_lambda.

Equation (1) says `v_lambda(q_i)=v_K(q)`, with `v_K(p)=1`, and hence

    d_w(q_i^m J) = d_w(J) + m v_K(q) sum_lambda w_lambda.  (9)

For `0<|q|_K<1`, the increment is positive and linear in `m`. These are fixed
weights for the chosen packet, not weights asserted to be the IUT weights.
No permutation-invariance of the weights is needed to compare the identical
hulls in (6); a claim of numerical invariance for nonidentical hulls would
need an additional check.

## 6. Scope boundaries and route outcome

The following source-to-model dictionary remains conditional:

| Mathematical item | Required source hypothesis |
| --- | --- |
| `A=K^(tensor r)` | Every factor really is the same local extension over the same `Q_p`, or specified isometric identifications reduce it to this case |
| `q_i` | The same `q` is inserted, with no independent choice of values at unequal places |
| `phi` | The operation is the full integral-closure module hull used above |
| `G<=S_r` | The admissible operation acts by factor permutations inside this packet |
| `sigma(J)=J` | The initial module hull has the stated invariance |
| Numerical equality | The source's numerical invariant is defined on the resulting equal hulls in one fixed normalization |

Mixed local fields, unequal places, multiple independently chosen inserted
elements, a different integral order, and other indeterminacies are outside
this result. Even if the actual construction has a homogeneous subpacket,
other operations could modify its hull or the comparison contract; this note
does not bound those operations.

Proved outcome: homogeneous insertion ideals agree across tensor slots; the
orbit-hull identity (5) is exact; and an invariant full module hull retains the
same inserted power, including a fixed-stage `j^2` power. This is a reusable
restriction on this local mechanism. It is not a proof or disproof of the
numerical realization property needed for IUT or of ABC.

No novelty is claimed. No finite computation or Lean verification supports
the universal statements; they have the elementary proofs above. The next
source-dependent check is whether a named original-IUT packet, its actual
integral hull, and the relevant part of (Ind1) satisfy every row of the
dictionary. A global conclusion still requires the other local packets,
remaining indeterminacies, admissibility, and quantitative height bounds.
