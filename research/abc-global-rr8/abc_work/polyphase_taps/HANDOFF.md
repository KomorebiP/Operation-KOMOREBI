# Continuation after the polyphase and tap test

Checkpoint ABC-20261025-RR4 follows the exact RR3 archive pinned in LATEST.md.
The original target is still every-epsilon primitive integer ABC, including
arbitrary input exponent vectors. A growing-exponent theorem for A^n+B^n is
restricted progress and does not cover arbitrary triples by setting n=1.

For the common-power family put c=A^n+B^n, D=rad(AB),
gamma=epsilon/(1+epsilon), and U(c)=B_2 W_n G_n as in RR3. A sufficient
adaptive certificate would be

    0!=Z in Z, W_n divides Z,
    |Z|<=D c^gamma/(B_2 G_n).

Those conditions imply U(c)<=D c^gamma and hence the requested pointwise
ABC inequality. The open work is to construct such a Z with an independent
size and nonvanishing proof in the required domain. Writing down the criterion
does not establish existence.

The current exact restrictions are:

* Pure refinement retains the local first-contact floor. In zero phase, it
  transports e_p to e_p+v_p(M), and D_n<=M D'_t. Compare actual evaluated
  cyclotomic products, not just their smaller apparent degree.
* At fixed stride h, all finite integer tap outputs form G_(n,h) Z. For
  h=2n the generator is c itself. Adding taps within that same linear span
  does not create a smaller nonzero integer.
* For short arbitrary taps, preserving birth powers P requires P|T(A)-T(B).
  If the difference is zero, the output is an exact scalar multiple of c.
  If nonzero, its magnitude is at least P(A-B) and at most the proved
  coefficient/degree bound. The fixed-support norm-degree optimization is
  not classified by that statement.
* Integral invertible banks preserve common content, not maximum coordinate
  depth. The target scalar functional transforms with synthesis and may
  retain deep cancellation between unit channels. A determinant estimate
  needs every relevant channel deep, a stronger premise than one deep sum.

Each route remains open under a precise new input:

| Route | Deferred next step | Resumption condition |
| --- | --- | --- |
| Refinement | Improve the transported exact high-order product or radical budget | Supply a bound beyond reindexing, with bases, phase weights, and normalization retained |
| Taps | Construct low-cost preserving taps with a provably nonzero small auxiliary | State support, coefficient and degree constraints, then exclude the exact annihilator/equal-evaluation kernel |
| Multichannel | Use adaptive constraints to force a useful simultaneous determinant or auxiliary certificate | Prove that all required contacts enter it and that its evaluated height improves on c |

Keep these controls:

* 2^3+1=9: blocking by 3 moves the factor 3 from inherited lifting into
  birth depth without changing the output powerful part.
* 7^2+1=50: blocking halves the occupied cyclotomic degree while
  Phi_4(7,1)=Phi_2(49,1)=50 remains unchanged.
* -511*(8^3+1)+8*(8^5+1)=9 is a genuine nonzero low-order tap certificate.
* p=1093,n=182,A=2,B=1: stride 364 has gcd generator c, while half-stride
  182 loses the odd contact.

Proofs and audits are linked in the claim ledger. New finite contracts can
be reproduced with `python3 abc_work/polyphase_taps/reproduce.py` from the
package root. No executable .mathbox ledger or Git revision was supplied;
archive/file hashes and append-only versioned claim records retain ancestry.
No Lean compilation was performed. Broad adaptive methods are deferred,
not claimed impossible or exhausted.
