# Torsion-distance transfer to exceptional birth depths

## Contract and inputs

The RR2 family consists of coprime integers A>B>=1, c=A^n+B^n, and odd primes p|c. Set

    d_p=ord_p(A/B),   e_p=v_p(A^d_p-B^d_p),
    W_n=product_(odd p|c) p^(e_p-1).

The input proof gives v_p(c)=e_p+v_p(n). Its unresolved target is an independent estimate on the large exceptional contribution to log W_n, or a transfer of that contribution to D=rad(AB). An estimate applying only as n tends to infinity does not settle arbitrary triples via n=1.

Input: abc_work/routes/global/PROOF_NOTE.md, SHA-256 f4b1c1eb8d4e52ee43634b454ea5fa3e12e88488dc148d76ea68e79a58e29bfc. This report does not claim historical originality or a solution of ABC.

## Exact primary-source checks

John Tate and Jose Felipe Voloch, *Linear forms in p-adic roots of unity*, author manuscript https://web.ma.utexas.edu/users/voloch/Preprints/root10.pdf, Theorem 2, Proposition 3, Section 4. Checked 25 October 2026. Theorem 2 separates nonzero torsion linear forms from zero for fixed coefficients and fixed p. Its constant depends on those coefficients. Lemma 2 bounds the ramified Vandermonde loss by N(N-1)/(2(p-1)), with N the number of terms. Proposition 3 treats the reduction to prime-to-p torsion. Section 4 asks about a global weighted sum rather than proving its convergence.

Thomas Scanlon, *The conjecture of Tate and Voloch on p-adic proximity to torsion*, author manuscript https://math.berkeley.edu/~scanlon/papers/tvfo20m99.pdf, revised 20 March 1999, Main Theorem. Checked 25 October 2026. For a semiabelian variety over a finite extension of Q_p and a fixed closed subvariety over C_p, its theorem bounds the proximity of torsion points outside that subvariety. The bound depends on the subvariety. It does not assert uniformity as its equations vary.

Authentication, theorem extraction, and the following transfer were checked against these primary texts. No retained full source text is included in this package.

## A complete two-term calculation

Normalize v_p(p)=1. Suppose p is odd and p does not divide AB. Let x=A/B in Q_p and let omega be the unique root of unity of order dividing p-1 whose reduction equals x modulo p. Since A>B>=1, x is not a rational root of unity, so x-omega is nonzero. Put d=ord_p(x). Then omega has exact order d, and x=omega*u with u in 1+p Z_p. Because p does not divide d,

    v_p(A-omega B)=v_p(u-1)=v_p(u^d-1)=v_p(A^d-B^d)=e_p.       (1)

The equality for u follows immediately by expanding (1+(u-1))^d; the linear coefficient is a p-adic unit.

Now consider any root of unity zeta in C_p. Write zeta=nu*eta, where nu has prime-to-p order and eta has p-power order. If the reduction of nu differs from that of x, then v_p(A-zeta B)=0. If the reductions agree, uniqueness of prime-to-p lifts gives nu=omega. For eta=1 the valuation is e_p. For nontrivial eta of order p^r,

    v_p(eta-1)=1/[p^(r-1)(p-1)] < 1 <= e_p.

The unequal-valuation triangle rule therefore gives

    v_p(A-omega*eta B)=1/[p^(r-1)(p-1)].                       (2)

Equations (1)-(2) prove the exact sharp separation constant in the relevant two-term instance:

    max_(zeta root of unity) v_p(A-zeta B)=e_p,
    min_(zeta root of unity) |A-zeta B|_p=p^(-e_p).             (3)

There is no zero value to exclude here. All coefficients are p-adic units, so this is already a normalized instance and cannot be fixed by rescaling the coefficients.

This is an elementary calculation, not an inference from numerical testing. In this application, the unspecified constant in Theorem 2 is exactly the exceptional birth depth we wanted to control. Applying the theorem establishes its finiteness for fixed A,B,p, which was already immediate from A^d-B^d being a nonzero integer. It supplies no independent height-uniform upper bound on e_p.

## Dictionary to RR2 and the determinant cost

For p|A^n+B^n, the same omega satisfies omega^n=-1: its n-th power is a prime-to-p root of unity reducing to -1, whose lift is unique. Thus the root at which the contact is deepest is already one of the factors in

    A^n+B^n=product_(zeta^n=-1)(A-zeta B).

When p does not divide n, reduction is separable and the other factors are units at p. Therefore the factor omega carries all v_p(c)=e_p. When p divides n, the ramified neighboring roots account for the additional v_p(n) already present in RR2.

Theorem 2 uses N=2 linear terms here, irrespective of n. Its ramified determinant loss is at most 1/(p-1). Eliminating or sharpening that loss does not bound (1), which takes place entirely in the unramified field Q_p. In a formulation with many Fourier terms, reducing an O(N^2/(p-1)) loss still leaves this same unramified contact untouched. No improvement on that determinant can by itself supply a bound on e_p.

## Why the general torsion-distance theorem does not repair uniformity

Take the fixed ambient torus G=G_m^2 and the subvariety

    X_(A,B): A X-B Y=0.

The torsion points (1,zeta) satisfy exactly the two-term proximity problem. As A,B vary, X_(A,B) varies. Scanlon's bound therefore varies with it; equation (3) computes that dependence explicitly in this slice.

Alternatively, fixing X-Y=0 requires moving A/B into the point coordinates. Such a point is not torsion, since a positive rational number greater than 1 is not a root of unity. Adding A,B as coordinates in a larger fixed torus has the same problem. Those changes leave the theorem's torsion hypotheses. The first failed transfer is thus either a varying subvariety constant or loss of torsion, depending on which dictionary is chosen.

## A uniformity counterexample with bounded exponent

Fix n=2 and p=5. There is a compatible Hensel sequence 1<=A_m<5^m with

    A_m^2=-1 mod 5^m,

starting from A_1=2. The lift exists uniquely because 2A_m is a unit modulo 5. Set B=1 and c_m=A_m^2+1. Then ord_5(A_m)=4=2n and

    e_5=v_5(A_m^4-1)=v_5(c_m)>=m.

Hence

    log W_2 / log c_m
       >= (m-1)log(5) / [2m log(5)+log(2)].                    (4)

The A_m are unbounded: otherwise a fixed positive integer would solve A_m^2+1=0 modulo arbitrarily high powers of 5, impossible. Thus c_m tends to infinity and the lower limit in (4) is at least 1/2.

The same construction works for any fixed prime p=1 mod 4, using a primitive fourth root modulo p. It can therefore be placed above any prescribed fixed small-prime cutoff. The finite verifier includes p=101 as a second exact case.

This refutes the claim log W_n=o(log c) uniformly in A,B,n as height grows while allowing bounded n. It does not refute a statement only as n tends to infinity, uniformly in A,B. It does not refute ABC: the input radical D=rad(A_m) has not been estimated, and can pay the repeated output contribution. A full proof route must keep that radical budget or handle bounded n separately.

## Evidence, outcome, and continuation

Command: `python3 abc_work/roots_unity/routes/torsion_distance/verify.py`.

The script checks 40 exact named-prime cases, for p=5,101 and m=1,...,20: Hensel congruence, primitive order 4, and the equality e_p=v_p(A_m^2+1). It does not factor entire outputs, compute total W_n, or establish an asymptotic theorem. Python 3.12.14 was used. Results are in results.json.

Transfer verdict: the fixed-coefficient torsion separation is applicable but does not imply the desired independent exceptional-depth bound. The coefficient-uniform strengthening covering bounded n is refuted by (4). The large-n-only RR2 target remains open, as does the possibility of transferring exceptional mass to rad(AB). No general-method impossibility is claimed.

The next useful input would have to quantify the separation constant jointly in the varying coefficients, torsion order, and prime, or couple the sum of local depths to the global input radical. The two-term calculation identifies exactly the constant such an input must control. No such uniform estimate was proved here.
