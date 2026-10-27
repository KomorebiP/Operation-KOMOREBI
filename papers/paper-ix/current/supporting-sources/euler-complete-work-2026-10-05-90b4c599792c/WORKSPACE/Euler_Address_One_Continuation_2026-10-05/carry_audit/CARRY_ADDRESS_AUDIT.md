# Carry-address audit and exact correction

Date: 2026-10-05. Source claims: supplied continuation message 161. Definitions checked against `sources/euler_v4.md`, sections 2, 3, 5, and `sources/finite_parameter.md`, sections 1–2. This is an independent derivation; no finite computation is used as a universal proof.

## Primary verdict

**Incomplete, with an explicitly false descent implication.** The record identities, regular-complement theorem, and finite descent of the *label combinatorics* are correct. Rewriting the same depth using a smaller label does not turn that label into its true terminal label. Remote carries in the new odd multiplier preserve the original difficulty. Consequently the claims that multiple lower roots have thereby been resolved, or that only odd-unit data remain, do not follow.

The exact address split is still useful and correct under the stated convergent packet definitions. It supplies a regular true-terminal complement when the original true terminal is certified. It does not prove transversality of the sum.

## 1. Exact record structure

For positive integers n define

    Θ(n)=3n+1+s₂(n−1).

For j≥1 and 0≤q<j define

    e_j(q)=3q+s₂(j−1)−s₂(j−q−1),
    E_j=min_{0≤q<j} e_j(q),
    M_j=max_{1≤c≤j} Θ(c).

Direct substitution gives

    e_j(q)=Θ(j)−Θ(j−q),
    E_j=Θ(j)−M_j,
    L_j=Θ(j)−E_j=M_j.

Also, incrementing the binary integer n−1 flips v₂(n) trailing ones, so

    Θ(n+1)−Θ(n)=4−v₂(n).

Thus j is regular, meaning e_j(q)>0 for every 1≤q<j, if and only if Θ(j) is a strict running record.

Let k be the *first* index attaining M_j and put a=j−k. The largest minimizing q of e_j is exactly a, and k is a strict record. Therefore

    k is regular,
    L_k=L_j,
    a=j−k.

These statements hold without any analytic or Euler-unit input. For regular j, a=0. All further statements concerning a positive address assume j is irregular.

## 2. Sharper address bound and exact local self-similarity

Put t=v₂(k). Because k+1≤j and k remains maximal through j,

    0≥Θ(k+1)−Θ(k)=4−t,

so t≥4.

Write k=2^t b with b odd. For 1≤c≤2^t,

    s₂(k−1)=s₂(b−1)+t,
    s₂(k+c−1)=s₂(b)+s₂(c−1)
              =s₂(b−1)+1+s₂(c−1).

Consequently

    Θ(k+c)−Θ(k)=Θ(c)−t.                       (2.1)

At c=t the right side is positive, since Θ(t)>t and t<2^t. Hence a<t. Applying (2.1) to each 1≤c≤a yields Θ(c)≤t, and therefore

    L_a≤t,
    3a+1≤Θ(a)≤t,
    a≤floor((t−1)/3).                         (2.2)

In particular

    a≤floor((floor(log₂ j)−1)/3).

This is substantially stronger than a<j. Iterating the first-maximizer address on irregular labels terminates extremely quickly as a combinatorial process.

For 0≤q<a, identity (2.1) also gives

    e_j(q)=e_a(q),
    e_j(a)=Θ(a)−t.                            (2.3)

The active lower minimizers can be described exactly:

    argmin e_j
      = {a} ∪ {a−c : 1≤c≤a and Θ(c)=t}.

If t>L_a, a is the unique lower minimizer. If t=L_a, the extra ties are exactly the record-level contacts of the smaller label interval.

## 3. The nested representation is algebraically true

Suppose r=b₀2^L−j>0 with L>t. Writing k=2^t c with c odd gives

    r=B2^t−a,
    B=b₀2^(L−t)−c.

Here B is positive and odd: B2^t=r+a>0. The hypotheses L>L_j used by the original shifted-wall theorem imply L>t automatically.

This is an identity for the same integer r. It is not an operation that replaces the Euler function H_r by a new function of smaller true terminal degree.

## 4. Exact remote-carry correction

The true Euler coefficient valuations are

    λ_r(q)=3q+s₂(r+q)−s₂(r),
    μ_r=min_{q≥0} λ_r(q),
    j_r=max{q : λ_r(q)=μ_r}.

For arbitrary positive odd B and 1≤a<2^t, set r=B2^t−a. Binary complementation gives

    λ_r(q)=e_a(q)                       for 0≤q<a,
    λ_r(a)=Θ(a)−t.

For q≥a write uniquely

    q=a+2^t d+e,   d≥0, 0≤e<2^t.

Since r+q=(B+d)2^t+e, we get the exact identity

    λ_r(q)=Θ(a)−t+Ψ_{B,t}(d)+3e+s₂(e),       (4.1)

where

    Ψ_{B,t}(d)=3·2^t d+s₂(B+d)−s₂(B).

Every tail minimum has e=0, because 3e+s₂(e)>0 for e>0. Therefore

    μ_r=min(E_a, Θ(a)−t+min_{d≥0}Ψ_{B,t}(d)). (4.2)

Only d satisfying

    d≤floor((s₂(B)−1)/(3·2^t))

can have Ψ_{B,t}(d)≤0. This is a finite exact minimization, but its range depends on the multiplier B. The nested representation retains the original high carries in Ψ. An arbitrary odd B cannot be replaced by 1 in the wall theorem.

### Small label counterexample with a strict inner wall

Take

    j=33, k=32, a=1, t=5,
    Θ(32)=102, Θ(33)=101, E_33=−1,
    L=103, r=2^103−33.

The original shifted-wall theorem gives

    μ_r=−2, j_r=33 uniquely.

But the nested representation is

    r=(2^98−1)2^5−1.

Its smaller label 1 is regular and its scale 5 is strictly larger than L_1=4. Nevertheless

    λ_r(1)=−1,
    λ_r(33)=−2.

Indeed B=2^98−1 has s₂(B)=98 and

    Ψ_{B,5}(1)=96+1−98=−1.

Thus even a regular smaller label on a strict inner wall does not identify the true terminal.

### The actual terminal-161 example

For r=2^640−161,

    k=160, a=1, t=5,
    Θ(160)=487, Θ(161)=486,
    E_161=−1, δ=153,
    μ_r=−154, j_r=161 uniquely.

Yet

    r=(2^635−5)2^5−1,
    λ_r(1)=−1.

Here B=2^635−5 has s₂(B)=634, and d=5 gives

    Ψ_{B,5}(5)=480+s₂(2^635)−634=−153.

Formula (4.1) returns λ_r(161)=−1−153=−154 exactly. The original 161-packet obstruction is stored in a carry of the new multiplier. It has not disappeared.

### A regular smaller address can still produce a multiple lower residue root

Take

    k=4096=2^12, j=4099, a=3, t=12.

The power-of-two label k is a strict record: for every c<2^12,

    Θ(k)−Θ(c)=3(k−c)+12−s₂(c−1)>0,

since s₂(c−1)≤12. Now Θ(1)=4, Θ(2)=8, Θ(3)=11, and Θ(4)=15. The exact self-similarity (2.1) therefore shows that k remains the first maximum through k+3, and the next record occurs at k+4. In particular

    L_3=Θ(3)=11<t=12,
    a=3 is regular,
    Θ(k)=12301,
    Θ(j)=12300,
    E_j=−1.

Because t>L_a, the lower minimum is unique at q=a=3. Set

    L=12302, r=2^12302−4099.

The original shifted-wall theorem applies with actual terminal j=4099, wall distance δ=1, and μ_r=−2. Its lower part V in

    G_r=P_j U+2V

has exactly one odd packet, q=3. Since the source reduces to 1, its binary reduction is

    V̄(X)=P̄_3(X)
         =X(X−1)(X−2)
         =X²(X−1) in F₂[X].

Thus V̄ has a double root at 0 even though the descending label tower has already reached the regular label a=3. Combinatorial regularity means a strict carry record; it does not mean squarefreeness of P̄_a or of the lower residue polynomial. This example does not refute a possible subsequent analytic resolution. It proves that resolution is still a separate obligation and cannot be inferred just from termination at a regular smaller label.

## 5. What true terminal inheritance does prove

There is a useful general cocycle identity:

    λ_r(a+h)=λ_r(a)+λ_(r+a)(h).                (5.1)

Suppose j=j_r is the certified true terminal and 0≤a≤j. Because the tail q≥a contains a global minimum and its last global minimizer is j, (5.1) implies

    μ_(r+a)=μ_r−λ_r(a),
    j_(r+a)=j−a.                              (5.2)

This is a genuine terminal shift because the depth changes from r to r+a. It is different from rewriting unchanged r in a smaller wall notation.

The packet coefficients c_(r,q)=8^q β_(r+q)/β_r satisfy

    c_(r,a+h)=c_(r,a)c_(r+a,h),
    P_(a+h)(x)=P_a(x)P_h(x−a).

Restricted convergence therefore proves the exact analytic identity

    H_r(x)=Σ_(q<a)c_(r,q)P_q(x)A(x−q)
             +c_(r,a)P_a(x)H_(r+a)(x−a).       (5.3)

Using G_r=2^(−μ_r)H_r and (5.2), the coefficient of P_aG_(r+a) in the normalized identity is a dyadic unit. For an outer wall with certified j_r=j and λ_r(q)=e_j(q) for q<j, μ_r=E_j−δ, the finite prefix has content at least 2^δ. Hence

    G_r=u_r P_a G_(r+a)(x−a)+2^δ V_(r,a)(x),  (5.4)

with V using only q<a. Choosing the first-record complement makes the *true terminal* of r+a equal to regular k=j−a.

Formula (5.4) is proved under these hypotheses. It does not imply that a repeated zero of G_r becomes a repeated zero of G_(r+a), or of an actual Euler function with terminal a. A sum of individually simple analytic pieces can be tangent.

## 6. Explicit counterexample to propagation from complement simplicity alone

This counterexample uses the actual analytic source but an artificial complement. It is **not** an Euler counterexample. Its purpose is to identify a missing necessary input in the proposed proof.

Let

    A(x)=(9^(x+1)−1)/(8(x+1)(2x+1)),
    p(x)=x(2x−1).

The removable value at x=−1 is understood. The source belongs to the restricted integral Tate algebra and A≡1 mod 2. Its explicit expansion also gives A'∈2 Z₂⟨x⟩. One way to see this is to write A(x)=B(x+1)/(2x+1), where B(t)=(9^t−1)/(8t): B' has coefficients divisible by 4, and differentiation of (2x+1)^(−1) contributes a factor 2.

Since A(1)=5/3, put

    v=5−A'(1) ∈ Z₂×,
    F(z)=7z²+64v z−320/3,
    G(x)=p(x)F(x−1)+64A(x).

F is primitive and has two distinct roots in Z₂. Indeed its discriminant is

    Δ=4096v²+8960/3
     =256(16v²+35/3).

The bracket is a unit congruent to 1 mod 8, hence has a square root s in Z₂×. The roots are

    z=8(−4v±s)/7,

and F' at these roots equals ±16s, which is nonzero.

But the proposed wall-transition form G is tangent at x=1:

    G(1)=−320/3+64·5/3=0,

    G'(1)=3(−320/3)+64(5−A'(1))+64A'(1)=0.

Thus primitive restricted analyticity, the actual Euler source, a positive dyadic wall magnitude, and simplicity of every complement root are insufficient for the transversality conclusion. A theorem specific to the Euler complement's unit coefficients is required.

## 7. Obligation matrix and surviving frontier

| Claim | Verdict |
|---|---|
| e_j(q)=Θ(j)−Θ(j−q) and L_j running maximum | proved |
| First record complement k is regular and L_k=L_j | proved |
| a<t and L_a≤t | proved; strengthened to 3a+1≤t |
| Finite descending tower of combinatorial labels | proved |
| Same depth has nested odd-multiplier representation | proved when L>t |
| Nested smaller label is the true terminal | refuted by j=33, L=103 |
| Remote carry geometry has disappeared | refuted by exact Ψ formula |
| A regular final address forces squarefree lower residue | refuted by j=4099, address a=3 |
| True-terminal shift r→r+a gives terminal j−a | proved |
| Exact normalized split with unit coefficient | proved under terminal certification |
| Complement simplicity alone forces transition simplicity | refuted by explicit artificial F |
| Multiple analytic roots descend along the combinatorial tower | not proved |
| Universal Euler simplicity | remains open in this audit |

The strongest safe reduction is: certify the true terminal, split at the lower last address, and exploit the regular true-terminal complement. The unresolved Euler-specific implication is nonvanishing of the transition derivative on its zero locus. A proof must use coefficient/unit information beyond the carry record identities and must not infer analytic descent from a reparametrization of unchanged r.
