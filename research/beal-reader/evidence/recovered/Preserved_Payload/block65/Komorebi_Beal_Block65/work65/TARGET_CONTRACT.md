# Target contract and hypothesis register

Authoritative predecessor: Komorebi_Beal_Block64_Common_Frobenius_Conductor_Closure_v6.4.0.zip.
SHA256 ea8b5de0724f97b35cf72511fca92e872c13359d3787791d319183f870c7aa09.
The clean extraction passed its declared selected predecessor replay before
editing. No original predecessor bytes were changed.

Primary target: exclude alpha=(+/-w,6,1), beta inertia(s547,s743)=(5,1) using
an actual common-representation constraint. Secondary target: convert the
paired-polynomial observation into a genuinely conductor-independent theorem
for a descended opposite class. A larger-conductor stress test must retain
actual survivors rather than omit new columns.

Inherited actual hypotheses:
- K=Q(sqrt5), phi=(1+sqrt5)/2. Coefficient ring O is the unramified quadratic
  extension of Z7, residue k=F7[w]/(w^2-5). The two quadratic roles are distinct.
- Actual depth n=1 for every new conductor and coefficient theorem in this block.
- alpha=a_phi[phi]+a3[3]+a5[sqrt5] has all three coefficients nonzero.
  Normalize once by a5=1, rescaling beta inversely. Put alpha=(u,r,1).
- beta is a nonzero class in H1(K,k(chi^-1)), and the actual trace correction at
  an unramified norm-1-mod7 place equals alpha(Frob)*beta(Frob).
- The actual natural Jacobian is the stipulated twist by delta=9-3phi of
  z^2=x^6+10Bx^3+12Ax+5B^2. Its O-rank2 representation restricts to the natural
  rank4 representation. A good Frobenius quartic has the rank2 factor and
  its coefficient conjugate. At variable bad places the exact toric trace
  equals Q+1 in this same representation.
- The conditional coefficient theorem expressly assumes beta descends as a
  chi^-1 cohomology class gamma over Q. It does not assume descent of alpha
  or of a Tate lattice. For all stipulated finite conductors here, every
  prime is inert in K and1 mod7, so the inherited inertia-injectivity, split7,
  and class-group hypotheses give this class descent.
- beta is locally zero at71, forced bad in the retained branch. At beta support
  the same natural class alpha vanishes. Old actual trace data and period
  restrictions remain frozen inherited inputs.

New derivations, not extra assumptions:
- The independent Kummer triple over L=K(zeta7) and separation of the chi and
  chi^-1 isotypic components give independent joint values.
- Chebotarev realizes those finite values at good rational primes split in L.
- delta'=phi^2 delta makes the two split-place quartics identical, forcing
  coefficient conjugacy when their trace products are distinct.
- These imply the normalized coefficient and class-field restrictions.

Exact computations: F379, F379^2, k, integers and Z[zeta7]. Finite solvers use
F7 coefficients only AFTER the written coefficient theorem, and the retained
547/743 exclusion also has a separate proof using the previous full-k list.

Executed routes:
A. Actual379 good/bad Frobenius: closes the specific old tuples.
B. Joint Kummer/character image and common polynomial: proves coefficient rigidity
   for arbitrary conductor under class descent.
C. Correctly twisted expansion through all inert q=1 mod7 primes <=2000:
   a 21-prime exclusion succeeds but the full 25-prime system retains112 tuples.

Proof evidence: written conditional proofs, six exact output programs, separately
implemented arithmetic, source checking and adversarial SELF review. No independent
reviewer or Lean certificate. No assumption bounds arbitrary conductors by2000.
