# Block54 target contract and inherited hypotheses

Sole authoritative predecessor: original Block53 v5.3.0 ZIP, SHA256
83987c80f66b0ac091ffdcd82b2e1657414f4736e4a1a297604abdf8ccf15c73.
Earlier sources are accessed through its immutable nested provenance only.

## Goal and bounded target

The long-term goal remains elimination of the retained reducible branch of
A^3+B^5=C^7, with CM and higher levels separate. This block's bounded target
is an actual-representation restriction on the remaining additive diagonal
correction, using global reciprocity and compatible toric directions.
A quotient of abstract characters alone would not achieve that target.

The completed target is stronger: a Frobenius/monodromy inequality for the
ACTUAL correction; global cup-zero and a one-step character lift; an exact
reduced reciprocity presentation; and the resulting support/depth bounds.
The full branch is not eliminated.

## Input list

H1. K=Q(sqrt5), O_K=Z[phi], phi=(1+sqrt5)/2. The seven-adic coefficient
ring O is the unramified quadratic ring, residue k=F49, w(7)=1.

H2. A hypothetical positive pairwise-coprime solution belongs to the inherited
reducible branch, including3990|C, and gives the specific twisted RM Frey
Jacobian and its characteristic-zero seven-adic representation.

H3. A single natural integral Frobenius-at-three basis has rho=[[a,b],[7^n c,d]],
finite actual depth n>=1, residual characters chi,1, determinant chi_7. The
natural and opposite endpoint extension classes alpha,beta are those of this
same representation. Beta is nonzero and must ramify at some variable prime.

H4. The exact local twisted toric characters at2,3,5,7 are chi_7 and1. The
full fixed local diagonal correction is trivial mod7^n. This is the stronger
Block53 conclusion, not an inference from residual trace alone.

H5. At each q|C outside2,3,5,7, choose actual Frobenius F and a unit tame
inertia generator I+N in the SAME basis. The split toric identities are
N^2=0,FN=QN,NF=N,Q=q^f. Natural content is t=1+v_7(v_q(C))>=1.
Both lower-left entries are divisible7^n. Beta ramifies exactly when
w(N_21)=n. Away from these and the fixed places the representation is
unramified. No arbitrary independent local conjugations are allowed.

H6. Block53's global theorem gives eta_n=a_n/chi_7=1 mod7^m,
m=floor(n/2)+1, so d(g)=1 mod7^m for EVERY g. Its proof and geometric leaves
are inherited and pinned, not newly certified by the finite computations.

H7. The preserved Block50 matrix identity is alpha cup beta=-delta(a_n)
in continuous H^2(K,k), with trivial action on k. The natural Kummer class
has the recorded three generators and nonzero3 andsqrt5 coefficients.

H8. Classical continuous cohomology, Hilbert90, the Brauer local-global
injection, and the ray-class reciprocity sequence are external mathematical
inputs, checked against Milne v4.03 with exact locators in SOURCE_CHECK.md.

## Three routes and outcomes

A. Five-row global reciprocity alone: executed exact residue/logarithm and
Smith calculations. Nonzero quotients survive, so this does NOT eliminate
all diagonal corrections.

B. Actual Frobenius together with the same natural monodromy and H6: proved
the loss of one tame inertia power and h>=m at beta support. This route
supplies the missing representation-specific restriction for routeA.

C. Test/falsify the stronger implications, then local-global lift: retained
valid old counterexamples when a new hypothesis is dropped, exhibited
surviving local examples, and proved cup-zero using the verified classical
localization injection. No beta-zero or conductor-preserving lift is inferred.

## Evidence contract

A written proof under H1-H8 is a conditional arithmetic theorem. Finite exact
runs audit algebra, examples and complete declared finite presentations only.
Independent implementation is not independent mathematical review. No Lean
compiler, new Lean source, or Lean certificate is claimed. Every timeout is
inconclusive. No finite prime support is a bound on arbitrary C.
