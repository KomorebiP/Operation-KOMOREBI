# Exact Wronskian image for every primitive triple

## Target, conventions, and scope

This extends Route D without changing its reviewed files. Let a,b be positive coprime integers, c=a+b, and exclude (a,b)=(1,1). Give each prime dividing abc an arbitrary integer coordinate z_p. Define

D_z(n)=sum_{p|n} v_p(n)(n/p)z_p,

G(1)=0, and, for n>1,

G(n)=gcd_{p|n}[v_p(n)n/p].

Set A=G(a), B=G(b), C=G(c). Coordinates at primes outside abc are set to zero. We require the exact additivity condition D_z(a)+D_z(b)=D_z(c). The Wronskian is W=aD_z(b)-bD_z(a). Every claim below is an elementary exact statement, not a proof of ABC or a claim of historical novelty.

## The exact image theorem

Let g=gcd(A,B,C). Then the possible integer Wronskians are exactly L Z, where

L = gcd(cAB, bAC, aBC) / g.                                      (1)

In particular, L is a positive integer and the smallest possible nonzero absolute Wronskian is L.

Proof. The prime supports of a,b,c are pairwise disjoint. Bezout's identity, applied separately to the coefficients v_p(n)n/p, shows that the three derivative values range independently over A Z, B Z, C Z. Thus every additive derivative-value triple is

(D_z(a),D_z(b),D_z(c))=(Au,Bv,Cw), with Au+Bv-Cw=0,

and every such triple is attained by integer prime coordinates. The Wronskian is then -bAu+aBv.

Consider the two integer row vectors

r=(A,B,-C),     s=(-bA,aB,0).

Euclidean integer column operations give a unimodular matrix U for which rU=(g,0,0). Write sU=(t,h,k). In the transformed coordinates the integral kernel of r consists exactly of vectors (0,v,w), and the image of s on it is gcd(h,k) Z.

The gcd of all two-by-two minors of the matrix with rows r,s is invariant under unimodular column operations. After the transformation it is g gcd(h,k). Before the transformation its three minors are cAB,-bAC,aBC. Consequently gcd(h,k) equals the expression in (1). At least one of a,b exceeds 1, and C>0, so one of the displayed minors is nonzero. Therefore L>0. This proves the theorem.

Boundary checks. If a=1, A=0 and g=gcd(B,C), giving L=BC/g=lcm(B,C), exactly the earlier image theorem. If b=1 the symmetric formula applies. For the excluded triple 1+1=2 all Wronskians vanish and the minor gcd is zero; no nondegenerate derivation exists.

## Exact strengthening of the radical divisibility

Write U(n)=n/rad(n), R=rad(abc), and P=U(a)U(b)U(c)=abc/R. For every prime coordinate choice, U(n) divides D_z(n), because it divides each coefficient v_p(n)n/p.

On the additivity kernel, the same Wronskian can be written in the three forms

W=aD_z(b)-bD_z(a)
 =aD_z(c)-cD_z(a)
 =cD_z(b)-bD_z(c).

These expressions show that each of U(a),U(b),U(c) divides W. They are pairwise coprime, hence P|W. Since the exact image contains W=L, we obtain

P | L.                                                        (2)

Thus J=L/P is a positive integer which measures the extra divisibility that the exact derivative-value images impose beyond the usual radical argument.

For a prime-coordinate norm H=max_{p|abc}|z_p|, the triangle inequality gives

|W| <= ab H sum_{p|ab} v_p(ab)/p
     <= ab H log(ab)/(2 log 2)
     <= ab H log(c)/log 2.

The middle inequality uses p log p >= 2 log 2 for every prime p. Combining this with |W|>=L=PJ for W!=0 gives

c J <= R H log(c)/log 2.                                     (3)

Equation (3) retains an exact integer factor J omitted by the coarse radical divisibility alone. It is a proved inequality for any given nondegenerate additive derivation. It supplies no independent upper bound on H/J.

## Why the next proof step is still missing

To infer full ABC from (3), it would suffice to prove that, for every delta>0, nondegenerate integral lifts can be chosen outside an explicitly handled family with

H/J <<_delta c^delta.

Indeed, (3) would give c <= O_delta(R c^delta log c); choosing delta small and absorbing log c yields c <= C_epsilon R^(1+epsilon). Easily settled exceptional families must be handled directly, rather than imposing a false derivative bound on them.

Neither the exact image theorem nor ordinary real projection establishes this bound. They give existence of a lift with W=L, but recovering the individual prime coordinates requires Bezout representations within each prime support. Their coefficients can be large. Conversely, choosing very small integer prime coordinates may force W=0. The image generator L alone therefore does not control the norm of an integral section of the Wronskian map.

For 1+48=49, the formula yields A=0, B=16, C=14, L=112, P=56, J=2. The minimum nondegenerate norm is H=8, so the normalized cost H/J is 4. This checks the new normalization against the earlier exact example, but makes no asymptotic claim.

The route's precise remaining obligation is now an upper bound on the integral section norm divided by its forced Wronskian divisibility J. Establishing that bound would be substantive arithmetic progress. Calling the section a projector or a realization does not supply it.

## Verification and disposition

The theorem and inequality were derived directly above, with boundary cases included. No new finite experiment is needed to establish them. They have not been Lean compiled or independently reviewed in this extension.

Outcome: exact general image and strengthened pointwise inequality proved. Full ABC remains unresolved. The projection-only route remains blocked by integral lift cost, with a sharper identified quantity H/J rather than H alone. This is a refinement of the bottleneck, not evidence that a suitable uniform bound exists.
