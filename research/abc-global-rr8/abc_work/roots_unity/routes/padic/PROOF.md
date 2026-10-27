# Roots of unity, birth depth, and the height that remains

Base: RR2, read from `abc_work/LATEST.md` and `abc_work/routes/global/PROOF_NOTE.md`. This is a new route record and changes neither inherited file. The target remains unrestricted primitive ABC. The results below are elementary local statements and counterchecks on a proposed filtering mechanism, not an ABC proof.

## 1. The exact torsion and principal-unit split

Let p be an odd prime, let A,B be integers with p not dividing AB, and let d be the multiplicative order of A/B modulo p. Then d divides p-1 and p does not divide d. There is a compatible sequence of residues z_k modulo p^k with

    z_k^d=1 modulo p^k,   z_k=A/B modulo p.

Each residue z_k has a unique lift z_k+jp^k modulo p^(k+1). Indeed,

    (z_k+jp^k)^d-1 = z_k^d-1 + j p^k d z_k^(d-1) modulo p^(k+1),

and d z_k^(d-1) is invertible modulo p, which uniquely determines j. This construction can be read entirely in finite rings; its inverse limit is a p-adic root of unity z.

Put t=A/B, with B inverted modulo each p^k. The factorization

    t^d-z^d=(t-z)(t^(d-1)+t^(d-2)z+...+z^(d-1))

has second factor congruent to d z^(d-1), a unit. Thus

    v_p(t^d-1)=v_p(t-z).                                    (1)

Equivalently, if t=z u with u=1 modulo p, then

    v_p(t^d-1)=v_p(u-1).                                    (2)

For every finite k these equalities hold with both valuations truncated at k and z replaced by z_k. Torsion removal therefore preserves the exceptional birth depth exactly. It does not reduce it.

If p divides A^n+B^n and d=ord_p(A/B), then d is even and n=(d/2)j with j odd. The same unit-factor argument and elementary exponent lifting give

    v_p(A^n+B^n)=v_p(A^d-B^d)+v_p(n).

The roots-of-unity description is consistent with RR2's decomposition into birth depth and ordinary lifting. It does not dispose of the birth factor W_n.

## 2. What a roots-of-unity filter does exactly

Fix a root z of order d modulo p, lifted as above. For a polynomial f(X)=sum a_m X^m over a ring in which p is the valuation prime and d is invertible, define

    P_r f(X) = (1/d) sum_(j=0)^(d-1) z^(-rj) f(z^j X).

For every integer ell, the sum of z^(j ell) is d if d divides ell and zero otherwise. In the second case 1-z^ell is a unit, so the geometric-sum identity is valid in every finite ring modulo p^k. Consequently

    P_r f(X)=sum_(m=r modulo d) a_m X^m.                     (3)

This filter selects coefficients. It gives no inequality bounding the valuation of a surviving evaluation.

Two direct checks distinguish the possible uses:

* For f(X)=X^d-1, P_0 f=f. The high-contact quantity is unchanged.
* For f(X)=X^n+1 with d=2n, P_0 f=1 and P_n f=X^n. At a root-contact input A, both pieces are units modulo p, but their sum can be divisible by p to arbitrarily high depth. Dropping either piece removes the equation that generated the large valuation. Recombining them restores that valuation.

Here 1/d has no p-adic cost because p does not divide d. It would be inaccurate to blame a denominator at the exceptional prime. A global argument using this presentation must still track normalization at primes dividing d, algebraic coefficient fields, and the heights of A and B. Exact coefficient selection can clear its displayed denominator by cancellation, so an automatic global denominator loss is not asserted either.

The root of unity itself has height zero. The unresolved height belongs to the rational input A/B and to simultaneous local approximation, rather than to the torsion point.

## 3. Arbitrarily deep primitive contacts with explicit height accounting

Let n be a positive power of two, let p be an odd prime with 2n dividing p-1, and choose r modulo p with order exactly 2n. Thus r^n=-1 modulo p. Starting with r, the elementary lift above, now for f(X)=X^n+1, gives canonical roots x_e in [0,p^e) for every e>=1.

Let j_e be the unique next lifting digit in [0,p). Choose k_e=1 unless j_e=1, in which case choose k_e=2. Set

    A_e=x_e+k_e p^e,   B=1.

Since k_e differs from j_e modulo p, the Taylor congruence gives

    v_p(A_e^n+1)=e,
    ord_p(A_e)=2n,
    v_p(A_e^(2n)-1)=e.                                      (4)

Every repeated factor at this p is a primitive exceptional birth factor: p does not divide n and the order is exactly 2n. The examples exist for arbitrarily large e. They disprove a depth cap that depends only on n,p, and the root-of-unity filtering operation while ignoring the size of A.

However, the chosen representatives satisfy

    p^e <= A_e < 3p^e.

Writing c_e=A_e^n+1, the certified exceptional contribution is p^(e-1), and

    log(p^(e-1)) < log(A_e) <= (1/n) log(c_e).                (5)

Thus this construction explicitly pays input height and does not contradict ABC or RR2's large-n sublinear target. It proves neither that all representatives must pay this much nor that no unusually small representative can occur. The elementary necessary bound for any positive A with p^e dividing A^n+1 is only

    e log p <= log(A^n+1),

which permits an exceptional factor to consume the entire output height. Improving the latter bound uniformly is the hard part.

## 4. Multiple primes and the precise unresolved comparison

One may prescribe compatible roots modulo p_i^(e_i) at several distinct primes and combine them by the Chinese remainder theorem. This always constructs a residue A modulo M=product p_i^(e_i). Taking A in [M,2M) supplies a positive representative with log A about log M. This establishes simultaneous arbitrary depth with an explicit height budget, rather than a counterexample to a global estimate.

The canonical CRT representative may also be much smaller than M. The local root filter does not constrain that disparity. A uniform estimate excluding excessive simultaneous high contacts for such small rational representatives would constitute new arithmetic input.

There is an essential small-n boundary. Taking n=1, A=p^e-1 and B=1 gives c=p^e, order d_p=2, and W_1=p^(e-1). Hence log(W_1)/log(c)=(e-1)/e tends to 1. A bound on output birth mass alone that is sublinear in log(c) cannot hold uniformly down to n=1. The input radical rad(A)=rad(p^e-1) must enter the unrestricted comparison. This example does not refute ABC, because it supplies no upper bound on that input radical.

The surviving research task is therefore a quantitative simultaneous approximation statement for rational A/B to roots of unity of orders dividing 2n, uniform in the moving primes, the order, and the bases. It must control the total repeated first-contact mass

    sum_(odd p|A^n+B^n) (v_p(A^d_p-B^d_p)-1) log p,

with enough dependence on rad(AB), n, and log(A^n+B^n) to satisfy RR2's pointwise criterion. A fixed finite set of primes, a fixed degree, or a mean over A/B would be a strictly weaker statement unless a further uniform transfer is supplied.

## 5. Verification contract and status

`verify.py` checks four explicit pairs (p,n)=(5,2),(17,8),(97,16),(257,128), with depths e=1,...,12. It independently computes each seed's order, checks canonical lifting, exact output valuation, birth valuation, coprimality, and the displayed input-height bounds. It also checks coefficient projection modulo p^e from its explicit averaging formula, rather than assuming the selection identity in code.

The proofs are uniform elementary arguments. The finite checks do not establish any distribution or height estimate. No full factorization of c is claimed, and additional exceptional primes may occur. No Lean compilation or novelty claim is made.

**Route disposition:** torsion removal or coefficient filtering alone is refuted as a mechanism for reducing birth depth. The simultaneous arithmetic approximation route remains open. Its first unresolved implication is a global height comparison for unusually small rational representatives of moving local torsion contacts.
