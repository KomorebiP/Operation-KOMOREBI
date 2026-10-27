# Complete discrepancy covers, grade extraction, and exact gluing

**Komorebi P. · original mathematical text v1.0.0 · formalization supplement v1.2.0**

**Formal status.** Block 02 verifies C01, the maintained NCT degree dependency, and the complete-cover lower bound. The dual certificate and later claim groups retain their prior written/finite status. See [the exact mapping](formalization/LEAN_BLOCK_02.md). The original theorem companion remains an unchanged historical document.

## Abstract

We collect a bounded set of results about classical restored Boolean computation. An arbitrary cut produces a complete cover of the accepting set by safe discrepancies between forward and inverse-suffix states. A pointwise safe-polynomial degree parameter gives a two-sided nonlinear-generation lower bound, with an affine optimization and exact finite certificates. Calibration families separate complete coverage from the existence of one safe packet. A second family shows why homogeneous projection cannot be assigned the nonlinear cost of the original computation and need not preserve safety. Finally, orthogonal idempotents give an exponential dimension bound for fixed faithful linear multiplicative witness summaries, while weighted witness fingerprints expose the exact failure of a context-free product rule at overlapping variables.

The results do not prove a superpolynomial unrestricted circuit lower bound or supply a polynomial-time SAT algorithm. Written arguments and finite computations have distinct evidence status throughout.

## Reading contract

Read `FOUNDATIONS.md` first for the model, simulation comparison, cut identity, and degree lemma. This is an edited consolidation of the Complete Packets and Projection checkpoint. `LINEAGE.json` identifies exact source bytes and code changes; the original note remains in its unchanged archive. The notation b in this manuscript is beta in the README and Foundations.

T counts only Toffoli gates. CNOT and NOT remain charged in total gate count. All polynomials are multilinear over F2 except explicitly stated extension-field computations. Tables of finite cases are computational evidence, not proofs for untested cases. External dependencies are S1–S3 in `REFERENCES.md`; no publication-novelty claim is made.


## 1. Complete coverage supplies a stronger pointwise obstruction

Write I_f={h: h(1+f)=0}, the Boolean functions supported only on positives of f. For v with f(v)=1 set

    b_v(f) = min {deg h : h in I_f, h(v)=1}.

Put b(f)=max_{v:f(v)=1} b_v(f), and b(0)=0. Thus b(f) is the least degree at which the safe polynomials collectively cover all positives. The one-packet parameter alpha_1(f) asks only for one nonzero safe polynomial. Always alpha_1(f)<=b(f)<=n for a nonzero n-input function.

The upper bound n follows from a single-point indicator at each positive input. If f has at least two positive inputs, b(f)<=n-1: for each v choose a second positive w; the sum of their two point indicators is safe, is one at v, and has its degree-n coefficient canceled.

### Theorem 1.1: complete cut bound

Every restored oracle satisfies

    T >= max(0, deg f - 1, 2 b(f) - 3, 2 b(1+f) - 3).

More generally let Aff_n be all affine Boolean functions and define

    b*(f) = max_{l in Aff_n} b(f+l).

Then

    T >= max(0, deg f - 1, 2 b*(f) - 3).                 (1)

Proof. At an arbitrary cut C=Q P, the cut comparison in `FOUNDATIONS.md` gives

    A(x)=P(x,0), B(x)=Q^{-1}(x,0), H_i=A_i+B_i,
    H_i <= f,  OR_i H_i=f.

Choose a cut after floor(T/2) Toffolis. Each forward or reverse coordinate is computed with at most ceil(T/2) multiplications, hence has degree at most ceil(T/2)+1. The same degree bound holds for H_i. Every positive v is hit by some H_i, not just some positive input. Therefore

    b(f) <= ceil(T/2)+1,

which gives T>=2b(f)-3, including the integer rounding. Appending output CNOTs and possibly a NOT computes f+l at no additional Toffoli cost, because the logical inputs are restored. This proves the affine optimization. The usual degree-minus-one bound gives the other term. QED.

The degree fact permits arbitrary sharing: introduce a formal Boolean variable for each AND output, so each is a product of two affine forms in preceding formal variables. Starting with an affine output and substituting in reverse order, each substitution raises degree by at most one. Multilinear reduction does not increase it.

The complete-cover b bound is an algebraic/coverage strengthening, not a superpolynomial method. It is invariant under invertible affine input changes. It remains at most n.

### An exact dual certificate

Let

    v_d(x)=(x^S)_{|S|<=d}

be the evaluation vector of all degree-at-most-d monomials, and U=f^{-1}(0). Then

    b_v(f)>d  iff  v_d(v) belongs to span_F2{v_d(u):u in U}.  (2)

Indeed, degree-at-most-d polynomials correspond to coefficient covectors on these evaluation vectors. A safe covector annihilates every negative vector. Such a covector can take value one at v exactly when v_d(v) lies outside their span. This is ordinary finite-dimensional linear duality.

A linear dependence

    v_d(v)=sum_{u in W} v_d(u), W subset U

is consequently a replayable obstruction against every safe degree-d packet at v. Because the constant monomial is included, |W| is odd. A basis yields |W| at most sum_{j<=d} binom(n,j), although succinct descriptions of larger W can also be used.

Building this entire evaluation system from an arbitrary SAT verifier is not claimed efficient. The criterion assumes the relevant negatives or their proved structure are available.

### Monotone specialization

For monotone f, I_f has a monomial basis indexed by positive supports. If a support S is negative, all its subsets are negative, and the coefficient of x^S in any h in I_f is zero by Boolean Mobius inversion. A monomial with positive support is safe by monotonicity.

Therefore b_v(f) is the size of the smallest positive support contained in supp(v). In particular,

    alpha_1(f)=minimum minterm size,
    b(f)=maximum minterm size.                            (3)

Here minterms are inclusion-minimal positive supports, not arbitrary positive inputs.

## 2. An all-size separation from the preceding bound

For k>=2 and n=k+2 define

    F_k(a,b,z_1,...,z_k)=(a b) OR (z_1...z_k),
    B=z_1...z_k,
    G_k=F_k+a.

The raw parameters are

    alpha_1(F_k)=2,  b(F_k)=k,  deg(F_k)=k+2.

More significantly,

    max_affine l alpha_1(F_k+l)=3,
    max_affine l b(F_k+l)=k+1.                            (4)

For alpha_1(0) in the maximum use the harmless sentinel zero; none of these F_k+l is zero.

Proof of the first maximum. Set z_1=0, so F_k+l becomes the nonzero quadratic ab+l|_{z_1=0}. It is one on an affine flat of codimension at most two in that face: if l contains a remaining z variable, set a=0 and the remaining affine form to one; otherwise fix a,b to an accepting pair. The indicator of the resulting flat in the full space has degree at most three and is safe. Thus alpha_1(F_k+l)<=3 for every affine l.

For l=a, alpha_1(G_k)=3. A witness is a(1+b)(1+z_1). To exclude a nonzero safe polynomial h of degree at most two, first restrict a=0. The accepting set there requires B=1. For k>=3 this forces h|_{a=0}=0 by degree, so h=a L with L affine. The negative face a=b=1 forces L(1,z)=0, hence L=c(1+b). The negative point a=1,b=0,z=all ones then forces c=0. For k=2, h|_{a=0} can only be cB. Write h=cB+aL. At a=b=1 the quadratic term cB cannot be canceled by affine L, so again c=0 and the same argument finishes.

For completeness, restrict b=1. Then

    G_k|_{b=1}=(1+a) B,

a singleton indicator on k+1 variables. At the positive point a=0,b=1,z=all ones, a safe detecting polynomial restricts to that singleton indicator, and therefore has degree at least k+1. The general two-positive-point upper bound gives b(G_k)<=n-1=k+1.

No F_k+l is a singleton, since that would have alpha_1=n>3. Therefore b(F_k+l)<=n-1 for all l, proving the second maximum. QED.

The one-packet bound even after affine output masks gives only n-1. Equation (1) gives

    T(F_k)>=2k-1=2n-5.                                  (5)

For example n=8 gives 11 rather than 7. A simple compute-uncompute construction gives T<=2n-3: compute A=ab and B using k-1 multiplications, toggle the target by A+B+AB, and uncompute A and B. Thus this is still a linear-size easy family, and its exact optimum is not claimed when the two bounds differ. The stronger bound can also be seen by restriction to b=1 followed by a free affine target adjustment. It is not presented as a new best circuit lower bound.

The moment certificate in (2) is explicit here. On the face b=1, every point except v=(a=0,z=all ones) is negative for G_k. The sum of any polynomial of degree <=k over that (k+1)-dimensional cube is zero. Consequently its value at v is the sum of its values at those negatives.

### Small-case coincidence did not extrapolate

For every function on at most four inputs the finite calculation found max_affine alpha_1=max_affine b. This suggested a possible equality. It fails already at n=5 in (4): the two values are 3 and 4. The general family proves that their difference is unbounded. This was a failed candidate extrapolation, not a program failure.

### Exact small restored-oracle calibration

All functions on at most three inputs have an implementation attaining (1). Affine functions need zero Toffolis. Every nonaffine quadratic on at most three bits has alternating quadratic rank two and is a product of two linear forms plus an affine function, requiring exactly one. Every three-bit cubic becomes a three-variable monomial plus an affine function after input translations, requiring exactly three by the singleton bound in Foundations F4.

Explicit circuits, not merely counts, are constructed and checked for all 276 functions on one, two, or three inputs. The resulting counts are 28 zero-Toffoli, 120 one-Toffoli, and 128 three-Toffoli functions. This is not an exhaustive search through all reversible circuits; optimality follows from the lower bound and matching constructions.

## 3. Grade extraction can be harder than generating the whole object

This route tested a potential invalid step: charge a circuit for the nonlinear complexity of each independently extracted homogeneous grade.

For m>=2 let a=(1,...,1) in F2^m and introduce a bit x_v for each

    v in V=F2^m \ {0,a}.

There are n=2^m-2 bits. Define m linear forms

    L_j(x)=sum_{v:v_j=1} x_v,

and the full function

    P_m(x)=product_{j=1}^m L_j(x).

The linear map has rank m (its columns include all standard basis vectors). It follows that P_m is linearly equivalent to a monomial in m independent coordinates, with n-m unused coordinates.

Therefore the exact costs are

    M(P_m)=m-1,
    T_rest(P_m)=2m-3.                                    (6)

The lower bounds follow from degree m and the affine-invariant one-sided singleton/codimension-m ideal argument. The upper construction computes the parities by CNOT, uses the optimal monomial oracle on their clean registers, and uncomputes the parities.

Now take Q_m to be the quadratic homogeneous ANF component of P_m in the ORIGINAL x coordinates. Since 0 and a were excluded,

    P_m(0)=P_m(e_v)=0.

For different u,v,

    coefficient of x_u x_v = P_m(e_u+e_v) = [u+v=a].

Hence

    Q_m=sum_{unordered {v,v+a}} x_v x_{v+a}.              (7)

This is the inner product on n/2 disjoint pairs. Its alternating polar matrix has full rank n. Consequently

    M(Q_m)=T_rest(Q_m)=n/2=2^(m-1)-1.                    (8)

For completeness, a general XOR-AND circuit with t multiplications has an affine subspace of dimension at least n-t on which its output is affine. Process AND gates in order; after preceding products have become affine on the current subspace, each new product is made affine by at most one affine restriction. If one operand is constant, no restriction is needed; otherwise set it to zero. For a quadratic with nondegenerate polar form, an affine restriction has a totally isotropic direction space, of dimension at most n/2. Thus t>=n/2. Direct Toffoli accumulation achieves this lower bound without ancillary nonlinear work. This lower bound does not assume that intermediate gates remain quadratic.

At m=10, the full function uses 17 Toffolis, while its quadratic projection needs 511. These are exact all-size cost formulas, not the outcome of synthesizing a 1,022-input optimal circuit by search.

### Essential qualifications

1. The growth is exponential in m but LINEAR in the actual input length n.
2. The full function's explicit construction also uses 2m(2^(m-1)-1) CNOTs. Its TOTAL gate count is O(n log n), while Q_m has n/2 total gates. This is NOT an exponential ordinary gate-count separation.
3. Q_m is generally NOT a safe packet for P_m. At m=3, the first unsafe input in the stated bit ordering is 13. At m=4 there are 7,616 inputs accepted by Q_m but rejected by P_m. A homogeneous projection does not preserve the positive-support ideal merely because the complete polynomial lies in it.
4. The result rules out a bound polynomial in T alone for this grade-extraction operation, independent of the linear/input-size resources. It does not rule out an overhead polynomial in n+T, nor a different rigorously specified invariant.

Thus a cheap affine coordinate computation can conceal expensive nonlinear homogeneous pieces, and extracting them can also destroy compatibility safety. Counting their isolated ranks as debt of the original dirty computation is not justified.

## 4. An exact exponential bound for flat, faithful gluing algebras

Here is a rigorously limited version of the proposed Komorebi flattening obstruction.

Let K be a field and W={0,1}^m. The full witness algebra is

    B=K^W,

with pointwise addition and multiplication. Equivalently, in characteristic two it is K[w_1,...,w_m]/(w_i^2-w_i). Let delta_v be the indicator of a witness v. Then

    delta_v^2=delta_v,
    delta_v delta_u=0 (u!=v),
    sum_v delta_v=1.

### Theorem 4.1

Suppose Phi:B -> A is a K-linear multiplicative map into a K-algebra, and Phi(delta_v)!=0 for every witness v. Then

    dim_K A >= 2^m.                                     (9)

Proof. The images e_v are nonzero orthogonal idempotents. If sum_v c_v e_v=0, multiply by e_u. All other terms vanish and c_u e_u=0. Since K is a field and e_u!=0, c_u=0. The e_v are linearly independent. QED.

No unital hypothesis is needed for this lower bound. If A=K and Phi is unital, Phi is exactly evaluation at one witness: scalar idempotents are zero or one, orthogonality permits at most one nonzero image, and the unit requires exactly one. Such a summary cannot preserve satisfiability of every singleton verifier.

This is an elementary consequence of the product-algebra decomposition, not a claim of new algebra. Its force for our research is the precise model boundary: a FIXED finite-dimensional linear summary cannot simultaneously preserve exact pointwise conjunction and retain every possible witness in polynomial dimension.

### Why (9) is not P != NP

An unrestricted algorithm need not compute through a fixed linear algebra homomorphism. It may use syntax, nonlinear encodings, different intermediate spaces, context-dependent operations, and succinct circuits representing elements of an exponentially large algebra. Exponential ambient dimension does not imply exponential expression length.

Moreover the quantified summary in (9) serves ALL predicates at a fixed witness length. Circuit lower bounds concern the minimum computation for a particular explicit decision family, and may be nonuniform in input length. The missing universal-simulation assertion is not smuggled into the theorem.

## 5. A succinct witness fingerprint avoids cancellation, but not evaluation cost

I also attempted the algorithmic direction, rather than only strengthening lower bounds.

For a Boolean verifier R(w) on m witness bits, put

    P_R(z)=sum_{w in {0,1}^m} R(w) product_i z_i^(w_i)

over a characteristic-two field. Distinct witnesses have distinct monomials. Therefore

    P_R is the zero polynomial iff R has no accepting witness. (10)

Let tau be top multilinear coefficient extraction in the Boolean w algebra. Then

    P_R(z)=tau_w [ R(w) product_i (1+(1+z_i)w_i) ].       (11)

Proof. For any Boolean-ring polynomial G, its top w coefficient equals sum_{v in {0,1}^m}G(v) in characteristic two: each proper-support monomial has an even number of nonzero evaluations, while the full monomial has one. At w_i=0 the multiplier in (11) is one; at w_i=1 it is z_i. Applying this identity gives (11).

The circuit expression INSIDE tau has only O(|R|+m) additional operations. The circuit cost of applying tau to that expression is not thereby bounded.

### A precise algorithmic implication

P_R has total degree at most m. Over a finite field K, a nonzero P_R vanishes at at most an m/|K| fraction of uniformly random z. A self-contained proof uses induction on the number of variables: expose the leading coefficient in the last variable, bound its zero probability by its degree divided by |K|, and otherwise use the elementary univariate root bound. The two degree contributions sum to at most m.

Thus a uniform polynomial-time exact evaluator for the weighted trace (11), with |K|>=4m, would give a one-sided randomized polynomial-time SAT algorithm. It never accepts an unsatisfiable verifier and accepts a satisfiable one with probability at least 3/4 per evaluation. This is NOT a deterministic P=NP proof.

The finite evaluator in this block explicitly keeps 2^m coefficients. It remains exponential in witness length. A concise formula containing a trace operator is not a completed trace computation.

### The attempted local compiler fails at overlap

Weighted traces multiply for predicates using disjoint witness-variable sets. They do not do so for predicates sharing a witness bit. With tau_z(P)=P(0)+z P(1),

    tau_z(w)=z,
    tau_z(1+w)=1,
    tau_z(w(1+w))=0,

but the product of the separate summaries is z. Also

    tau_z(w^2)=z,  tau_z(w)^2=z^2,

which differ for general field z.

This is not an implementation bug. It disproves the attempted context-free multiplicative trace compiler. Theorem 4.1 explains the all-size mechanism: retaining all witnesses while exactly preserving arbitrary intersections requires the full orthogonal information in a faithful linear algebra. Nonmultiplicative fingerprints can compress outputs, but must explicitly handle the compatibility defect at shared variables.

The random fingerprints use only O(m log m) random bits for a field of polynomial size. That removes the need to store an arbitrary exponential coefficient table, but no polynomial-time evaluator has been established. It is not a SAT algorithm.


## 6. Closure of the present scope

The fixed conclusions of this manuscript are C01–C08 in `CLAIMS.md`. Their definitions, proofs, executable finite checks, and limits form this release. Extending them to superpolynomial shared-generation bounds or a polynomial-time weighted-trace evaluator is outside version 1.0.0. Neither extension is assumed by a theorem here.

The release is deliberately not an open-ended sequence of continuation blocks. Failed inferences and optional research directions are retained in `FAILURES.md` and `OUT_OF_SCOPE.md`. The present work can be evaluated and reproduced without completing those directions.
