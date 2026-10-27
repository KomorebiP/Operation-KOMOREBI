# Arithmetic consequences and the exact 97/293 boundary

All implications concern the retained reducible branch of A^3+B^5=C^7,
with the explicit inherited representation and geometric hypotheses. They
do not eliminate the whole reducible branch.

## B56.4. Good-prime and character consequences

The two independently checked Frey certificates give

    491 does not divide C  =>  n=1,
    197 does not divide C  =>  n<=2 and eta_n=1 mod 7^n.

The second character conclusion uses the inherited m=floor(n/2)+1 bound,
which is full precision at n=1 or 2. Equivalently,

    n>=2 implies 491 divides C,
    n>=3 implies 197*491 divides C,
    eta_n nontrivial implies n>=3 and 197*491 divides C.

These implications allow arbitrary other prime divisors. No other high
prime can change the required good-Frobenius precision at an auxiliary
prime which does not divide C. The conclusion stops applying at that prime
when it becomes a bad-reduction divisor of C.

Combining with the previously forced divisor gives

    n>=2 => 768912500245890 divides C,
    n>=3 => 151475762548440330 divides C.

The first is

    2*3*5*7*11*13*19*29*31*43*71*491,

and the second includes the further factor 197. These are necessary
conditions, not upper bounds or contradictions for arbitrary C.

## B56.5. The original two-prime high-support branch has depth one

For a rational variable prime q define f_q by its residue degree in K and
h_q=v_7(q^f_q-1). Put

    H(C)={q|C : q not in {2,3,5,7}, h_q>=2}.

Since h_491=2, any branch with H(C) contained in {97,293} has 491 not dividing C.
The new good-491 theorem therefore proves

    H(C) subset {97,293} => n=1 and eta_n=1.

Arbitrary additional prime divisors with h_q<=1 are permitted. More generally,
the conclusion n=1 holds whenever 491 is absent from H(C), with no bound on
the remaining high support.

Thus Block 55's nonzero reciprocal line at 97/293 cannot be the nontrivial
actual diagonal under this COMPLETE high-support hypothesis. This is an
actual-Frobenius exclusion of a previously surviving necessary system, not
a claim that its abstract ray character fails to exist.

There is a further exact reduction:

    H(C) subset {97,293,491} => n<=2 and eta_n=1.

Here 197 is absent. At depth two, 491 must divide C and some actual
beta-supporting prime q in this set must satisfy

    t_q=2,       v_7(v_q(C))=1.

Indeed, eta trivial forces slope s=0 at beta support. The inherited exact
identity n=t_q+2s gives t_q=2, while Frobenius requires h_q>=n. Thus an
actual supporting prime exists and its multiplicity is divisible by 7 but
not 49. This does not rule out depth two.

## What the result does not prove

It does not exclude a highest-layer character supported only at 97 and 293
when other high primes, including 197 and 491, also divide C. The support of
eta, the support of its highest layer, the support of beta, and all prime
divisors of C are different objects.

In particular, adding 197 and 491 to a proposed C is not forbidden. They may
be unramified in the highest character layer. The corresponding bad-prime
matrices and other good Frobenius values must then be analyzed. No theorem
says every divisor of C ramifies in beta or eta.

Depth one remains unresolved even on the two-prime high-support class. The
new statement eta=1 is not beta=0. The separate CM cover, higher Hilbert
levels, full (3,5,7) signature, and full Beal remain open obligations.
