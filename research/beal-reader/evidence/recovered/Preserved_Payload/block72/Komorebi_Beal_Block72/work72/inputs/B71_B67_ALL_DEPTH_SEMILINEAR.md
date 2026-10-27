# B67.3. All-depth semilinear cohomology compatibility

Retain the actual hypotheses at ANY positive stable-lattice depth n. In the
common global normalization a5=1 write

    alpha=u[phi]+r[3]+[sqrt5],       u,r in k^*, k=F49.

The nonvanishing of u is the inherited Block63 result, not proved anew here.
Let sigma(x)=x^7 onk, and let j induce the nontrivial automorphism ofK/Q and
fix the cyclotomic field at the chosen finite level. Then

    u^7=-u,   r in F7^*,   j[beta]=sigma[beta]
                       in H1(K,k(chi^-1)).                 (1)

Equivalently alpha=(v*w,r,1), with v,r inF7^*, w^2=5 in the COEFFICIENT field.
There are36 normalized directions at EVERY depth, not just depth one.

## Proof without assuming full diagonal triviality

Put e=ceil(n/2). B67.2 preserves the whole actual joint image
F7^3 direct_sum V onG_Le, including a nonzero pair(b,b'). It realizes all these
values at paired good Frobenius with ell=1 modulo7^e. B67.1 applies there,
using only the inherited half-depth precision of the actual diagonal.

For every(x,y,z) inF7^3 the two normalized trace products are

    P=b(ux+ry+z),           Q=b'(-ux+ry+z).

Both belong to the one- or two-element correction set of ONE actual quartic.
Thus Q=P or Q=sigma(P) at every vector. As inB66, these alternatives are
kernels of twoF7-linear maps. Two proper kernels cannot coverF7^3: each has
at most49 elements. At least one equality is identically true.

For a nonzero(b,b'), Q=P identically is impossible: its z-coefficient gives
b'=b, and its x-coefficient then gives2bu=0, forcing the pair zero. Hence
Q=sigma(P) identically. Comparing z,x,y yields b'=b^7, u^7=-u, r^7=r.
This applies to every pair, so B'=sigma B onG_Le.

## Returning to cohomology overK

Do NOT assert injectivity merely because[Le:K] is prime to7; it generally is
not. Let D=j[beta]-sigma[beta]. OnG_L1 its additive restriction has chi^-1
covariance. Its restriction toG_Le is zero. B67.2's commutator argument,
now applied to this single-character image with T=5, forces its entire
G_L1 restriction to be zero. Only THEN apply the inherited prime-to-seven
restriction injectivity for[L1:K]=6. It gives D=0 inH1(K,k(chi^-1)). QED.

## The two rational components now exist at every depth

The same degree-two cohomological argument asB66 gives unique

    gamma_+ inH1(Q,F7(chi^-1)),
    gamma_- inH1(Q,F7(chi^-1 epsilon5)),
    beta=res_K gamma_+ + w res_K gamma_-.

This extends the DECOMPOSITION, not every depth-one local-value consequence.
The tame support argument is independent ofdepth: gamma_- has no inert
variable ramification, and actual beta-support confines its remaining
ramification to split q=1 modulo7. If no split beta ramification exists,
the inherited fixed-prime conditions and inertia injectivity give gamma_-=0.

## Important non-extensions

1. There is no assertion eta_n=1 for n>=3. Half-depth precision is sufficient
   on the DEEP cyclotomic slice, not at arbitrary primes.
2. Ordinary beta descent still requires gamma_-=0. The old anti-only andmixed29
   controls remain valid. No semilinear isomorphism of integral Tate lattices
   is constructed, and no base/coefficient radical is identified.
3. The fixed13 local-zero condition was previously justified at depths1,2
   (and when full eta_n=1). This block does NOT export that condition to all
   higher depths with nontrivial eta. The explicit new13 ray row below has
   that additional local-zero hypothesis.
4. Depth-one finite correction tables are NOT reused as higher-depth tables.
   Formula(3) ofDEEP_TRACE_PRODUCT divides by7^n at higherdepths.
5. Every inference remains conditional on the original actual-model and
   half-depth-precision inputs. The finite tests do not audit those globally.
