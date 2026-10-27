# Komorebi: complete discrepancy covers, grade extraction, and exact gluing

Date: 2026-09-21.
Status: written proofs with self-review and exact finite checks. The P-versus-NP target is not reached. No Lean verification, independent review, or publication-novelty claim.

## 0. Target, lineage, and cost conventions

Original target: decide P versus NP. A sufficient stronger endpoint remains a superpolynomial unrestricted Boolean-circuit lower bound for an explicit NP language, with length measured in encoded input bits. An exponential vector-space dimension, a linear gate bound, or a result for a restricted summary model is not that endpoint.

Authoritative predecessor: `Komorebi_PNP_Cut_Comparison_Block_2026-09-21.zip`, SHA256 `2c72f7a75efc2277fed11aafbec5d77afbd376b81a98c0f3042e11d3c13ab0bd`. Its extracted, unchanged contents are retained under `predecessor/komorebi_pnp_cut_comparison/`. All 52 entries of its seal were checked. Its entire documented runner was replayed in a separate working copy and its two immediate scientific result files matched.

Classical reversible basis: NOT, CNOT, and Toffoli with three distinct wires. A restored oracle is

    (x, 0^a, y) -> (x, 0^a, y XOR f(x))

for every logical input x and both initial target bits y. Logical inputs and the target may be used as controls and workspace. All ancillas and logical inputs must be restored. Borrowed bits, when allowed, must be restored uniformly; fixing their initial values cannot weaken our lower bound. No measurements, relative phases, quantum superpositions, or discarded garbage are included.

T is the number of Toffoli gates. NOT and CNOT are free in this count, not in total circuit size. M(f) denotes the number of AND gates in an unrestricted XOR-AND circuit. All Boolean polynomials are their unique multilinear ANFs over F2. Statements comparing exponentially different T counts must not be restated as exponential separations in total gate count or in input length.

Three routes were executed:

1. Strengthen the cut obstruction from existence of one safe packet to complete coverage of every positive input.
2. Attempt to charge grades separately; test whether grade extraction preserves generation cost.
3. Attempt an efficient exact witness summary and weighted trace, testing compositional gluing.

## 1. Complete coverage supplies a stronger pointwise obstruction

Write I_f={h: h(1+f)=0}, the Boolean functions supported only on positives of f. For v with f(v)=1 set

    b_v(f) = min {deg h : h in I_f, h(v)=1}.

Put b(f)=max_{v:f(v)=1} b_v(f), and b(0)=0. Thus b(f) is the least degree at which the safe polynomials collectively cover all positives. The predecessor's alpha_1(f) asks only for one nonzero safe polynomial. Always alpha_1(f)<=b(f)<=n for a nonzero n-input function.

The upper bound n follows from a single-point indicator at each positive input. If f has at least two positive inputs, b(f)<=n-1: for each v choose a second positive w; the sum of their two point indicators is safe, is one at v, and has its degree-n coefficient canceled.

### Theorem 1.1: complete cut bound

Every restored oracle satisfies

    T >= max(0, deg f - 1, 2 b(f) - 3, 2 b(1+f) - 3).

More generally let Aff_n be all affine Boolean functions and define

    b*(f) = max_{l in Aff_n} b(f+l).

Then

    T >= max(0, deg f - 1, 2 b*(f) - 3).                 (1)

Proof. At an arbitrary cut C=Q P, the predecessor's exact comparison gives

    A(x)=P(x,0), B(x)=Q^{-1}(x,0), H_i=A_i+B_i,
    H_i <= f,  OR_i H_i=f.

Choose a cut after floor(T/2) Toffolis. Each forward or reverse coordinate is computed with at most ceil(T/2) multiplications, hence has degree at most ceil(T/2)+1. The same degree bound holds for H_i. Every positive v is hit by some H_i, not just some positive input. Therefore

    b(f) <= ceil(T/2)+1,

which gives T>=2b(f)-3, including the integer rounding. Appending output CNOTs and possibly a NOT computes f+l at no additional Toffoli cost, because the logical inputs are restored. This proves the affine optimization. The usual degree-minus-one bound gives the other term. QED.

The degree fact permits arbitrary sharing: introduce a formal Boolean variable for each AND output, so each is a product of two affine forms in preceding formal variables. Starting with an affine output and substituting in reverse order, each substitution raises degree by at most one. Multilinear reduction does not increase it.

The new b bound is an algebraic/coverage strengthening, not a new superpolynomial method. It is invariant under invertible affine input changes. It remains at most n.

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

The strongest predecessor bound even after affine output masks gives only n-1. Equation (1) gives

    T(F_k)>=2k-1=2n-5.                                  (5)

For example n=8 gives 11 rather than 7. A simple compute-uncompute construction gives T<=2n-3: compute A=ab and B using k-1 multiplications, toggle the target by A+B+AB, and uncompute A and B. Thus this is still a linear-size easy family, and its exact optimum is not claimed when the two bounds differ. The stronger bound can also be seen by restriction to b=1 followed by a free affine target adjustment. It is not presented as a new best circuit lower bound.

The moment certificate in (2) is explicit here. On the face b=1, every point except v=(a=0,z=all ones) is negative for G_k. The sum of any polynomial of degree <=k over that (k+1)-dimensional cube is zero. Consequently its value at v is the sum of its values at those negatives.

### Small-case coincidence did not extrapolate

For every function on at most four inputs the finite calculation found max_affine alpha_1=max_affine b. This suggested a possible equality. It fails already at n=5 in (4): the two values are 3 and 4. The general family proves that their difference is unbounded. This was a failed candidate extrapolation, not a program failure.

### Exact small restored-oracle calibration

All functions on at most three inputs have an implementation attaining (1). Affine functions need zero Toffolis. Every nonaffine quadratic on at most three bits has alternating quadratic rank two and is a product of two linear forms plus an affine function, requiring exactly one. Every three-bit cubic becomes a three-variable monomial plus an affine function after input translations, requiring exactly three by the predecessor singleton bound.

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

The random fingerprints use only O(m log m) random bits for a field of polynomial size. That removes the need to store the predecessor's arbitrary exponential coefficient table, but no polynomial-time evaluator has been established. It is not a SAT algorithm.

## 6. What has and has not moved

Surviving results:

- Complete safe coverage yields the pointwise bound (1), with the exact moment obstruction (2).
- Family (4) gives an unbounded separation from the predecessor's affine-optimized one-packet parameter, though both gate bounds remain linear.
- Every function on at most three inputs has a matching classical restored implementation for (1).
- The projection family (6)-(8) demonstrates exact nonlinear-cost distortion and failure to preserve safe support under homogeneous grade extraction.
- Fixed linear faithful conjunction summaries require exponential algebra dimension by (9).
- The compact weighted witness polynomial and its trace formula are exact, but the trace compiler fails on overlaps.

Unresolved sufficient endpoint:

    every actual complete cut-discrepancy cover for an explicit NP family
    requires superpolynomial SHARED total construction cost,

with the forward/reverse histories, dirty workspace, reuse, and input length all charged correctly. Neither b, isolated grade rank, nor algebra dimension proves this.

The next mathematical bottleneck is a cost-controlled treatment of compatibility defects for succinct overlapping expressions. A successful lower-bound statement must permit arbitrary Boolean circuits. A successful algorithmic statement must evaluate, rather than merely name, the needed projection. This note establishes neither final statement.

## 7. Computation scope and evidence

`python checks/run_all.py` compiles the exact C++ profile calculation, replays the predecessor in an isolated directory, and runs the three Python scientific checkers. A C++17 compiler is required for the four-bit exhaustive profile table. The runtime used g++ 14.2.0 and Python 3.13.5. The mathematical tests use integers, GF2, and GF16; no floating-point tolerances enter conclusions.

- All 276 functions on one through three inputs: pointwise supported-function enumeration (6,375 nonzero support cases), independent evaluation-span duality, exact matching restored circuits, 4,240 scalar input/target checks and 2,344 gate cuts.
- All 65,536 four-input functions: exact subset-minimum profiles. This algorithm enumerates every candidate support polynomial and propagates minima to every containing positive set. Independent rank-based checks cover 765 specified/sampled functions. All 168 monotone functions are separately checked against minterm formulas. The random sample is fixed by seed 20260921.
- The unbalanced OR family: full truth-table dual checks through nine inputs; every affine output mask through eight inputs. Ninth-input affine optimization is justified by the written proof, not exhaustive mask testing.
- Projection: 693,965 pair coefficients and nine exact full-rank checks through m=10 (n=1,022). Full truth tables are checked only at m=2,3,4, totaling 16,452 logical inputs and 65,808 restored input/target cases across both oracles.
- Weighted fingerprints: 1,052,736 polynomial/field-point evaluations, 20,544 independent Boolean-ring coefficient extractions, and 4,096 disjoint-variable product checks. Extraction covers all GF16 points for m<=2, and the stated 4-point-per-coordinate grid for m=3; root counts cover all GF16 points for every verifier through three witness bits.
- Scalar summary maps: every linear map in the three stated finite domains (256 + 65,536 + 256 maps), checking primitive-idempotent equations against evaluation maps.

No new verifier run failed in this block. Failed mathematical candidates are recorded separately: small-case affine equality, cost-free nonlinear grade extraction, and context-free multiplicative weighted trace. The unrestricted separation remains unproved.

## 8. Bounded source check and overlap

Primary sources checked in their stated versions:

1. Mathias Soeken, `arXiv:2005.01778v1`, *Determining the Multiplicative Complexity of Boolean Functions using SAT*. XOR-AND model and degree-minus-one lower bound. `https://arxiv.org/html/2005.01778v1`
2. Joan Boyar and Magnus Gausdal Find, `arXiv:1407.6169v3`, *Multiplicative Complexity of Vector Valued Boolean Functions*. Affine-flat restriction argument, quadratic/inner-product controls, and distinctions between general and restricted circuit models. Section 1.1, especially the statement preceding Proposition 2. `https://arxiv.org/html/1407.6169v3`
3. Chris Beck and Yuan Li, `arXiv:1304.0713v1`, *Represent MOD function by low degree polynomial with unbounded one-sided error*. Context for one-sided immunity/weak representation. `https://arxiv.org/html/1304.0713v1`

These sources authenticate the reused terminology and elementary complexity tools, not the new circuit-to-packet claims by authority. Those claims are proved in the note. This was a bounded dependency check, not a novelty audit and not a claim about the current best circuit lower-bound frontier. Initial broad searches returned mostly irrelevant material; the primary versioned texts supplied the relevant checks. No external PDFs were used.
