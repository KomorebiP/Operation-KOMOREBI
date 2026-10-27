# B66.2. Two opposite-character components, with different rational twists

Let epsilon5:G_Q -> {1,-1} be the quadratic character of K/Q. Under B66.1,
write the normalized opposite class uniquely as

    beta=beta_+ + w beta_-,
    beta_+,beta_- in H1(K,F7(chi^-1)).

Concretely beta_+=(beta+sigma beta)/2 and
beta_-=(beta-sigma beta)/(2w). Scalar extension splits into the two indicated
F7 coefficient summands because the cyclotomic coefficient action is in F7.
B66.1 yields

    j beta_+=beta_+,          j beta_-=-beta_-.

Restriction/corestriction for the degree-two extension K/Q therefore give
UNIQUE classes

    gamma_+ in H1(Q,F7(chi^-1)),
    gamma_- in H1(Q,F7(chi^-1 epsilon5)),

such that

    beta=res_K(gamma_+) + w res_K(gamma_-).                             (1)

For the second term, epsilon5 restricts trivially to G_K, but changes the
j-action by -1. Thus beta_- becomes invariant for the twisted rational
coefficient module. Surjectivity onto invariants can be obtained explicitly
as one half of corestriction, since Res Cor=1+j; injectivity follows from
Cor Res=2. The constructions occur in cohomology, not in a chosen Tate lattice.
The value w is a coefficient scalar with trivial Galois action in the original
K-module; epsilon5 is included in gamma_-'s RATIONAL module, not assigned to w.

Ordinary chi^-1 descent of beta is equivalent to gamma_-=0. In that case (1)
recovers B65.1's F7-valued normalized representative. Without an argument
killing gamma_-, an unrestricted F7-valued conclusion is not justified.

## B66.3. The anti-invariant component cannot ramify at inert variable primes

Fix a rational prime q outside{5,7}. The coefficient module of gamma_- is
unramified there, with arithmetic Frobenius value epsilon5(q)/q modulo7.
Wild inertia is pro-q, so has no seven-primary H1. Tame seven-inertia is
Z7(1). Arithmetic Frobenius conjugates a tame generator tau to tau^q.
This relation also follows directly by choosing compatible roots of a
uniformizer: Frobenius raises the tame roots of unity to their qth power.

If a twisted cocycle has nonzero inertia value c, covariance and this
relation give

    q c=(epsilon5(q)/q)c,
    q^2=epsilon5(q) modulo7.                                          (2)

When q is inert in K, epsilon5(q)=-1. But -1 is not a square modulo7, so
(2) is impossible. Thus gamma_- is unramified at EVERY inert variable prime,
not just the finite conductor primes previously enumerated. At split primes
(2) permits q=+1 or-1 modulo7. This is a necessary tame-support restriction,
not a sufficient realization theorem.

The plus component likewise requires q^2=1 for tame ramification. At an inert
variable supporting prime, all actual beta inertia is therefore in its plus
component, and is F7-valued in the compatible normalized coordinates. At split
pairs the anti-component has opposite transported values; the combined values
are coefficient-conjugate, not assumed equal.

Under the inherited condition that beta is unramified at the fixed primes and
split at seven, and the inherited injectivity of variable-inertia localization,
one obtains an additional corollary:

    no beta ramification above split rational primes => gamma_-=0.     (3)

Indeed beta_- then has no variable ramification by (2), has the inherited
fixed-prime conditions, and is zero by inertia injectivity (extend scalars to
k if necessary). This is a support condition, not a proof that split
ramification is absent. It broadens the earlier all-inert descent statement
without placing a numerical bound or requiring q=1 rather than-1 modulo7.

## Mandatory non-descent control

Take u=w,r=1, and formal opposite values b=w, b'=-w. For EVERY
(x,y,z) in F7^3 the products

    w(wx+y+z),       -w(-wx+y+z)

are coefficient-conjugate. These values satisfy the universal paired-product
constraint although b is not F7-valued. The resulting sign action is exactly
the chi^-1 epsilon5 component in (1). It can be encoded on the finite
semidirect product (F7^3 plus F7) semidirect (F7^* times C2), with cyclotomic
weights chi and chi^-1 and base signs(-,+,+,-). This is a consistent finite
cohomology/algebra model, NOT a Frey representation or Diophantine solution.
It prevents turning (1) into ordinary descent without proving gamma_-=0.

No claim here extends the depth-one trace-product theorem to n>=2.

## B66.4. The formerly redundant prime13 condition detects the minus component

The frozen Block64 boundary records full local beta-zero at13 at depth one,
using the already forced bad reduction, eta1=1 and the nonseventh phi symbol.
It is not a new good-reduction assumption. By the direct coefficient splitting,
both beta_+ and beta_- restrict to zero on G_(K_v) at13. Since this local extension
has degree two, restriction on seven-primary H1 is injective. Consequently both
rational gamma components are locally zero at13.

For gamma_+, this unramified Frobenius statement is automatic: its coefficient
Frobenius is chi(13)^-1=-1, so H1_unram is zero. For gamma_-, the additional
quadratic sign makes the Frobenius action (+1). It can have a genuine unramified
additive value, and the actual condition imposes

    gamma_-(Frob13)=0.                                                 (4)

More concretely, on rational Frobenius F at13 the two square evaluations are
(1-1)gamma_+(F)=0 and (1+1)gamma_-(F)=2gamma_-(F). The K-local beta-zero kills
the second value. Thus the previous "13 gives no row" result remains true for
the descended plus regime, but does not discard the real constraint on a
nonzero minus component. No numerical ray matrix for arbitrary minus conductors
has been constructed in this block.

The actual geometric support law is stronger than the bare tame condition(2):
beta-support requires Q_v=1 modulo7. Thus any variable ramification of the
minus component must lie over a SPLIT rational q=1 modulo7, not q=-1. This
uses the inherited actual-support theorem, not just the abstract cohomology.

## A second control: do not reuse the descended29 row in the mixed regime

For u=w,r=6, take opposite values b=6+w, b'=6-w at the two split29 places.
The actual natural rows are(4,1,5),(3,1,5), and both products equal2. This
satisfies the actual singleton good correction set at29, with b nonzero.
It also satisfies b'=b^7. Therefore the new semilinear theorem does NOT justify
beta29=0 without ordinary descent. That old zero row is used only in the
finite all-inert conductor calculation, where descent has its own proof.
