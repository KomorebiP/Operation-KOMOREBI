# Nested polyphase refinement preserves the exceptional birth budget

Base checkpoint: RR3 archive SHA-256 `557eeb61fcd37c984884b7123e7b599b403200244786f6fb549279d6b4b05302`. The mathematical input is RR3's exact common-power decomposition and occupied cyclotomic degree budget. This route uses the user's signal definition: x_j[t]=x[Nt+j], with nested phase paths corresponding to residues modulo N^r. The coordinator checked this definition in `Transfer_Block_Signal_Processing_Framework.pdf`.

Let A>B>=1 be coprime integers and define the ambient sequence x[h]=A^h+B^h for h>=0. Fix the target exponent n>=1 throughout the pointwise budget, blocking and compression statements below. For an odd output prime p write d=ord_p(A/B), s=v_p(A^d-B^d). Then d is even at a plus contact, p does not divide d, and

    p|x[n] iff n=d/2 modulo d,
    v_p(x[n])=s+v_p(n) at those contacts.                       (1)

RR3 gives U(x[n])=B_2(n) W_n G_n, where W_n is the product of odd birth factors p^(s_p-1), G_n divides n, and B_2(n)<=A. The target is to reduce the high-order birth budget through genuine polyphase refinement. No ABC proof, historical originality, or Lean compilation is claimed.

## 1. Exact contact geometry in nested phases

For a target depth k>=1 define

    L_p(k)=d p^max(0,k-s).

Since p is odd, (1) and the coprimality of p,d imply

    p^k|x[n] iff n=L_p(k)/2 modulo L_p(k).                      (2)

In a nested phase x_j[t]=x[Mt+j], M=N^r, set g=gcd(M,L_p(k)). This phase contains a depth-k contact iff

    g divides L_p(k)/2-j.                                     (3)

When compatible, the contact set is one residue class of t modulo L_p(k)/g. This follows by solving the linear congruence Mt=L_p(k)/2-j modulo L_p(k).

On refinement to the N children j+Ma, 0<=a<N, let g'=gcd(MN,L_p(k)). A compatible parent has exactly N g/g' compatible children. Indeed, the child congruence is a single class of a modulo g'/g, and g'/g divides N. An incompatible parent has none.

These formulas isolate contacts exactly. They do not suppress a contact already present in the selected phase. Once M is a multiple of L_p(k), every child of a compatible phase remains compatible at depth k.

For the baseline birth packet, k<=s gives L_p(k)=d. After selecting M=d,j=d/2, the entire phase has

    v_p(x[dt+d/2])=s+v_p(2t+1).                               (4)

Under a further p-ary split of t, p-1 children have the constant depth s, while the remaining child has depth s+1+v_p(2u+1). Thus the inherited lifting splits into deeper channels, but the birth floor s persists in every child. The local birth weight (s-1)log p is not reduced by decimation.

For the baseline birth depths k<=s, if gcd(N,d)=1, every phase at every tree depth remains compatible and retains residual period d; refinement by that radix never isolates the baseline contact into a single permanent phase. If all prime divisors of d divide N, sufficiently deep refinement captures the baseline contact, after which its birth floor persists in all descendants of each captured phase. Higher valuation depths k>s use the full modulus L_p(k) in (2)-(3); their behavior also depends on whether p divides N.

## 2. Zero-phase blocking moves inherited depth into birth depth

Suppose M|n and put t=n/M, C=A^M, D=B^M. The same output is x[n]=C^t+D^t. For each odd p|x[n], its new order and birth depth are

    d'_p=d_p/gcd(d_p,M),
    s'_p=s_p+v_p(M).                                         (5)

The order formula is the order of the M-th power of a finite-group element. For the depth formula, put g=gcd(d_p,M). Then M d'_p=d_p(M/g), and p does not divide g. The elementary odd-prime lifting formula for A^d_p-B^d_p gives (5).

Write H_M=product_(odd p|x[n]) p^v_p(M). It divides M. If W'_t,G'_t denote the birth and lifting factors computed in the blocked bases C,D, then

    W'_t=W_n H_M,    G'_t=G_n/H_M,
    W'_t G'_t=W_n G_n.                                      (6)

The output and its 2-adic factor are unchanged. Ordinary primes dividing M can become exceptional in the blocked representation: their inherited lifting has simply been renamed birth depth. This is exact mass transport, not a smaller radical defect.

Example: x[3]=2^3+1=9 has ordinary p=3, birth s=1 and G_3=3. Blocking by M=3 gives 8^1+1, birth s'=2 and W'_1=3. Nothing about the integer output improves.

## 3. Exact cyclotomic refinement comparison

For each positive r,

    Phi_r(X^M,Y^M)
       = product_(d: d/gcd(d,M)=r) Phi_d(X,Y).                 (7)

The set of d in the product is finite: every such d divides Mr. To prove the identity, a complex number z is a root on the left exactly when z^M has order r. If z has order d, this is the equation d/gcd(d,M)=r. All roots are simple, and both sides are monic with precisely that root set. Homogenization gives (7).

Let S be any set of old plus-contact conductors at exponent n, and let S' be its image under d->d/gcd(d,M). The map z->z^M sends their primitive-root sets into the primitive-root sets of S' and has at most M elements in a fiber. Consequently

    sum_(d in S) phi(d)<=M sum_(r in S') phi(r).                (8)

More strongly, (7) gives exact integer divisibility at positive A>B:

    product_(d in S) Phi_d(A,B)
       divides product_(r in S') Phi_r(A^M,B^M).                (9)

All extra cyclotomic factors have positive integer values, so the latter exact norm budget is at least the former. This comparison concerns the actual cyclotomic products, not only a loose degree bound.

For S=E_n, every old exceptional prime remains exceptional by (5), so S' is a subset of the new occupied conductor set E'_t. Thus

    D_n<=M D'_t,    D'_t/t>=D_n/n.                             (10)

A reduced degree after blocking is paid for by a larger phase base. Pure zero-phase regrouping cannot improve the normalized occupied-degree fraction, and the exact norm budget in (9) cannot shrink. Further exceptional channels can appear when p|M.

Example: p=5 in 7^2+1 has d=4, s=2. Blocking M=2 changes d to 2 and halves phi(d), but Phi_4(7,1)=Phi_2(49,1)=50 exactly. The apparent degree gain is entirely the height change.

## 4. A valid compression theorem and its limit

There is a useful exact transport to a smaller exponent, but it does not beat RR3's degree budget. Write a=v_2(n), and define

    m=lcm(2^a, {d/2:d in E_n}).

The lcm of the empty order set means m=2^a. Since every allowed d has v_2(d)=a+1, one has m|n and n/m odd. Therefore x[m]|x[n]. Every exceptional birth prime of x[n] already divides x[m] by its order, and every exceptional birth prime of x[m] divides x[n]. Their birth depths are unchanged in the original bases. Hence

    W_m=W_n,    B_2(m)=B_2(n),
    U(x[n])/U(x[m])=G_n/G_m divides n.                         (11)

The last quotient is an integer because x[m]|x[n], m|n, and G_m uses a subset of the output primes with exponents v_p(m)<=v_p(n). Thus G_m|G_n, and G_n/G_m divides G_n, which divides n.

All occupied d are allowed conductors for exponent m. The sum of phi(d) over all allowed conductors is m, so

    D_n<=m.                                                  (12)

If m=o(n), (11) gives a restricted ABC conclusion using x[m]<=2A^m. However D_n<=m shows that this condition was already covered by the sharper degree-budget theorem. Compression is a correct realization of the old packet at a smaller exponent; it supplies no new bound for a top-order channel with m comparable to n.

## 5. What the refinement does and the first unresolved step

Nested polyphase refinement exactly locates the contact residues and transports their lifting hierarchy. It separates inherited depth and detects compatible channels. The calculations do not reduce the exceptional birth floor of a selected contact, the exact cyclotomic norm budget, or the occupied degree after height normalization.

The failed proposed bridge is the inference that fewer compatible phase paths imply a smaller pointwise birth weight at a known contact. Conditional on that contact path, the whole birth packet remains. The examples p=5 in 7^2+1 and p=1093 in 2^182+1 test this directly.

The first unresolved arithmetic step is a height or radical estimate for a high-order channel that improves (9)-(10), rather than reindexes its factors. A tap/refinement argument supplying such an inequality could advance ABC. Orthogonal phase decomposition and zero-phase blocking alone do not supply it.

## 6. Verification

`verify.py` checks bounded nested phase trees against direct modular powers, verifies the compatible-child count, and tests the persistent birth floor. On a finite full-factorization grid it checks blocked order/depth transport, exact mass conservation, the cyclotomic identity and norm-product divisibility, normalized degree comparison, and the compression theorem. Its domain and counts are recorded in `verification.json`. No finite checks are used as a proof of ABC or a global height estimate.
