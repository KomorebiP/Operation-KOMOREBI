# Clarification of the inherited fixed-offset statement

Applies to Section 6 of the base `PROOF_NOTE.md` in
`ABC_Square_Kernel_Reverse_Realization_2026-10-25.zip`.

The fixed-offset extension must retain the assumption **gcd(h,Q)=1**
from the earlier multiplier family. Section 6 does not restate it.
If its displayed hypotheses are read as a standalone replacement, its
normalization is false. For example a=1,h=2,Q=4,c=9 gives an ordinary
hit 9>rad(72)=6, but its claimed upper bound would read 3<9/4.

The complete sufficient hypotheses are:

* a,Q,h are positive integers, h is squarefree;
* gcd(h,Q)=1 and gcd(a,hQ)=1;
* c=a+hQ, K=Q/rad(Q), A0=a/rad(a).

Then the pairwise coprimalities give exactly

    rad(a h Q c)=rad(a) h rad(Q) rad(c).

An ordinary hit therefore implies

    rad(c)<K/rad(a)+A0/[h rad(Q)]<=K+A0.

The original quadratic-root count, applied to m u^2=a modulo Q,
then gives the claimed bound with T=K+A0. This is the corrected
standalone statement. The a=1 main family and all new restricted
counting theorems explicitly assume gcd(h,Q)=1 and are unaffected.

The archived base source remains unchanged for provenance. Any broad
endorsement of its fixed-offset section in a route audit is to be read
subject to this explicit clarification. This correction does not establish
or refute the ABC conjecture.
