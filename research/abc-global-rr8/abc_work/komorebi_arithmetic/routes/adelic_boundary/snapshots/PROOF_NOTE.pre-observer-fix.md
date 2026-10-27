# An adelic boundary for a weak arithmetic realization contract

Checkpoint ABC-20261025-RR7. Base RR6 archive SHA-256:
026d1f544ba86acc3fd9d63b75b4a8fc73595407f67e15f1b9b7f7e5144d993a.
Owner: /root/komorebi_adelic_boundary.

This note constructs a counterexample to one explicitly weak gluing claim.
It is not an ABC counterexample, an IUT counterexample, or an obstruction to
all arithmetic realizations in Komorebi Space. It uses Komorebi Space's
distinction between a coherent ambient family and the image of the intended
global source. That distinction is retained, not challenged.

## 1. The weak claim to test

Fix K=Q(i), of degree two, with its one complex place. At a finite place v,
write O_v for the integer ring, ord_v for the integer-normalized valuation,
and N(v) for the residue-field cardinality. Use the product-formula
normalizations

    |x|_v=N(v)^(-ord_v(x)),        |z|_infinity=|z|_C^2.

Let a=(a_v), b=(b_v), c=(c_v) be ideles, all integral at every finite
place. The weak contract requires the following.

1. For every place, including infinity, a_v+b_v=c_v.
2. At every finite place, the triple is locally primitive: its three
   entries are integral and at least one is a unit.
3. All finite reductions of these local elements, and their arithmetic
   carry descriptions, are coherent under reduction.
4. Each coordinate satisfies the numerical product formula:
   product_v |a_v|_v=product_v |b_v|_v=product_v |c_v|_v=1.
5. The finite prime support of a_v b_v c_v belongs to one fixed finite
   set S of places.

The false conclusion is that these conditions force the adelic family to
be the diagonal realization of one global K-triple, or suffice by
themselves for a global conductor-height bound of the ABC type.

We will construct infinitely many such families outside that diagonal
image. Their support is exactly the places over 2,3,5. Their declared
height tends to infinity while their support cost remains fixed.

The complex place is essential to this construction. We do not replace
the positive real infinite place in the integer ABC problem by an
unjustified complex phase. This is a weak gluing test over the fixed
imaginary quadratic field K, whose actual archimedean completion is C.

## 2. Infinitely many suitable triangle lengths

For each positive integer n put

    C_n=3^n,
    m_n=floor(n log(3)/log(2)),      A_n=2^(m_n),
    k_n=floor(n log(3)/log(5)),      B_n=5^(k_n).

There are infinitely many n>=2 for which

    A_n+B_n>C_n.                                           (1)

Here all three exponents are positive. The other strict triangle
inequalities then follow because C_n>A_n and C_n>B_n.

We give an elementary proof of the infinitude rather than relying on
numerical sampling. First, for every irrational alpha and every epsilon>0,
there are infinitely many positive n with

    0 < fractional_part(n alpha) < epsilon.                 (2)

For arbitrarily large N, pigeonhole N+1 fractional parts into N equal
intervals. Taking the difference of two gives q>=1 with
0<||q alpha||<1/N. If fractional_part(q alpha)=delta<1/N, take n=q.
Otherwise it equals 1-delta. Put L=floor(1/delta). Irrationality gives
L delta<1 and 1-L delta<delta, so

    fractional_part(L q alpha)=1-L delta in (0,delta).

In either case an index has fractional part in (0,1/N). The resulting
indices are unbounded: a finite set of positive indices has a strictly
positive minimum of its nonzero fractional parts. This proves (2).

Take alpha=log(3)/log(2), which is irrational because a rational relation
would make a positive power of 3 equal a positive power of 2. By (2),
infinitely many n have fractional part less than log(10/9)/log(2). For
these indices,

    A_n/C_n=2^(-fractional_part(n alpha))>9/10,
    B_n/C_n>1/5.

The second inequality follows from k_n>n log(3)/log(5)-1. Hence their sum
is greater than 11/10, which proves (1). Unique prime factorization also
gives C_n>A_n and C_n>B_n, strictly, at every positive n for which the
corresponding exponents are defined. Discarding finitely many small n
ensures m_n,k_n>=1.

We now restrict n to any unbounded sequence satisfying (1), and abbreviate
A=A_n, B=B_n, C=C_n, m=m_n, k=k_n.

## 3. The finite-place realization

At every finite place v of K define

    (a_v,b_v,c_v) =
      (2^m, 1, 1+2^m)            if v divides 2;
      (1, 5^k, 1+5^k)            if v divides 5;
      (1, 3^n-1, 3^n)            if v divides 3;
      (1, 1, 2)                 at every other finite place.

Every displayed entry is nonzero and integral, and every displayed sum is
exact. At a place over 2 only a_v is a nonunit; b_v and c_v are units.
At a place over 5 only b_v is a nonunit. At a place over 3 only c_v is a
nonunit. Elsewhere all three entries are units, since those places do
not divide 2. Thus all finite triples are primitive, in fact with two
unit entries at each place, and their support is exactly S={v:v|30}.

The coordinate families are ideles because all coordinates are nonzero
and are units outside the fixed set S. They are also integral adeles at
all finite places.

Each local triple lies in the rational subring Z_p inside K_v. Therefore
its reductions modulo every p^N are coherent, and their ordinary
Teichmuller/Witt descriptions with the genuine carry terms are coherent
as well. Equivalently one can use the native reductions O_v/pi_v^N.
Their compatibility follows because they are reductions of actual
elements, not separately chosen finite-level solutions.

At the ramified place over 2, we do not identify O_v with an unramified
Witt ring. The rational Z_2 elements have ordinary Witt descriptions
before inclusion into O_v, and the native pi_v-adic reductions exist
independently. The carry terms are retained, not assumed to vanish.
No IUT-specific reconstruction theorem is invoked here.

## 4. An exact complex archimedean sum

The strict triangle inequalities imply that

    t=(C^2+A^2-B^2)/(2AC) belongs to (-1,1).

Choose

    a_infinity=A(t+i sqrt(1-t^2)),
    c_infinity=C,
    b_infinity=C-a_infinity.

Then a_infinity+b_infinity=c_infinity, and

    |a_infinity|_C=A,
    |b_infinity|_C=B,
    |c_infinity|_C=C.

The second identity follows by expanding
|C-a_infinity|^2=C^2+A^2-2ACt=B^2. All three are nonzero. Thus the local
additive equation holds at the actual complex place of K as well as at
every finite place. These archimedean elements are not required by the
weak contract to be images of elements of K; that is exactly the
semantic condition being tested.

## 5. All three numerical product formulas hold

The relevant Gaussian prime factorizations are

    (2)=(1+i)^2 up to a unit,        N(1+i)=2;
    (3) is prime,                   N((3))=9;
    (5)=(2+i)(2-i),                 N(2+i)=N(2-i)=5.

The quotient rings verify the norms: F_2, F_9, and F_5 respectively.
The finite product of a's absolute values is 2^(-2m): its only
nonunit coordinates occur at the place over 2 and ord_(1+i)(2)=2.
Likewise the finite products for b and c are 5^(-2k) and 3^(-2n).
Their complex absolute values in the product-formula convention are
2^(2m), 5^(2k), and 3^(2n). Consequently

    product_v |a_v|_v=1,
    product_v |b_v|_v=1,
    product_v |c_v|_v=1.                                  (3)

These identities were verified for the constructed families directly.
They are not being inferred from diagonal global membership. Genuine
nonzero K-elements satisfy the same normalization by the number-field
product formula, but its converse for arbitrary ideles is false.

## 6. Height grows while support cost stays fixed

For the weak adelic data declare

    h(a,b,c)=(1/2) sum_v log max(|a_v|_v,|b_v|_v,|c_v|_v),

using the usual local expression for projective height, now as a
functional on this specified ambient adelic space. At every finite place
the maximum is one. At infinity the maximum is C^2. Hence

    h(a,b,c)=log C=n log 3 -> infinity.                    (4)

This does not assert that every such ambient value is the height of an
algebraic point. That requires an intended global point first.

The declared normalized support cost is

    r(a,b,c)=(1/2) sum_(v finite,ord_v(a_v b_v c_v)>0) log N(v)
            =(1/2)log(2*9*5*5)
            =(1/2)log 450.                                (5)

It is constant. Thus, for every fixed real A_0>=0 and B_0, some member of
this family has h>A_0 r+B_0. In particular no all-epsilon ABC-shaped
inequality holds on the entire weak adelic realization locus.

This is a failure of that enlarged locus to enforce a height inequality.
It is not a counterexample to the integer ABC conjecture, to its number-
field forms, or to a realization contract that restricts to actual global
arithmetic sources.

## 7. The families are provably outside the diagonal source

Suppose a global alpha in K had image a_v at every place. At any place
over 3, that image is 1. The field embedding K->K_v is injective, so
alpha=1 in K. At the place over 2 its required image would then be 1,
whereas our image is 2^m!=1. This contradiction proves non-diagonality.

It does not depend on whether the chosen complex phases happen to be
algebraic, nor on a merely approximate failure of the global sum. The
finite source-membership obstruction is already exact.

A small illustrative member is (m,k,n)=(3,1,2), giving lengths (8,5,9).
Take

    a_infinity=20/3+(4 sqrt(11)/3)i,
    b_infinity=7/3-(4 sqrt(11)/3)i,
    c_infinity=9.

Their squared moduli are 64,25,81 and the sum is exact. The finite
coordinates follow the formulas above. This example is illustrative;
the infinite-family argument is the proof of unboundedness.

## 8. An actual Komorebi Space interpretation

The weak contract can be expressed as a declared Set-valued view system,
without assuming a Hilbert linearization of the nonlinear balance map.
Take one raw view T whose fiber consists of triples of ideles integral
at every finite place. For each v include a local-coordinate view, a
local defect view with map (x,y,z)->x+y-z, and at each finite precision
a reduction view. Include a balance view R^3 with the map

    (a,b,c) -> (sum_v log|a_v|_v,
                sum_v log|b_v|_v,
                sum_v log|c_v|_v).

All sums are finite outside the infinite place because the raw
coordinates are ideles. The finite reduction maps compose normally.
Use the view-category direction in which an arrow v->T induces the
restriction F(T)->F(v). Include composites as the corresponding maps.
Every coherent family is determined by its raw coordinate and all
restrictions. Prescribe zero at the defect and balance views (and their
zero reductions). The resulting extension fiber is exactly the weak
locus defined in Section 1. Our constructed point is an explicit element
of that fiber.

For local-coordinate fibers one may take O_v^3 at finite places and C^3
at infinity; the raw nonzero-coordinate condition simply restricts which
points arrive from T. Their defect fibers are O_v or C. Reduction views
are (O_v/pi_v^N)^3 with the standard transition maps. Nothing requires
the logarithmic balance map to be additive: the strict Set-valued theory
allows these declared maps. Its additive obstruction or Hilbert repair
theorems cannot be applied without supplying their stronger hypotheses.

There is also an intended-source evaluation: nonzero global integral
K-triples with a+b=c give diagonal raw points, and hence coherent
families satisfying the product formula. Section 7 proves that this
evaluation is not surjective onto the stated weak fiber. No universal
property of the ambient limit claims otherwise.

This is a concrete arithmetic instance of Volume I, Section 35.2:
constructing coherent data does not prove essential surjectivity of the
intended-source comparison. It parallels the observation/source-image
distinction in Realization Boundaries, Chapter 9, but does not identify
these adelic objects with that book's countable-group construction.

## 9. Outcome and the open continuation

The proposed weak bridge is refuted as stated: local exact arithmetic,
full finite-level coherence, three scalar product formulas and fixed
prime support do not force diagonal global arithmetic membership or
an ABC-shaped conductor-height inequality on the ambient locus.

The original arithmetic program remains open. A successful continuation
must retain or derive the intended global source image, and then prove
the quantitative conductor/height estimate on that image. Reintroducing
the full global source makes membership correct but supplies no new
height saving by itself. The present note gives neither an arithmetic
membership algorithm nor that saving.

No finite numerical test, novel-theorem priority claim, or Lean replay is
used as evidence for the universal statements. Exact source contracts
and local computations are recorded in INPUTS.json and SOURCE_NOTE.md.
