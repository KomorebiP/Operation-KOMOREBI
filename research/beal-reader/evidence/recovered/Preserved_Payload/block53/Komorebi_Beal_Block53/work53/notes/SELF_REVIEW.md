# Adversarial self-review

Reviewer: the same assistant, separate proof pass. Not an independent reviewer.

1. **Wrong lattice?** H4 is natural-lattice entrywise divisibility; H3 uses an
integral Frobenius-at-three basis of that SAME natural lattice. A lattice
rescaling would invalidate the easy upper-entry argument. Such rescaling is
not performed here. Source comparison is in LOCAL_INPUT_AUDIT.

2. **Residual versus characteristic zero?** Fixed-place trace chi+1 is obtained
from actual toric uniformization at all powers, including at residue7, not
from beta splitting or a residual characteristic polynomial.

3. **Coincident local residual characters?** At fixed2,3,5 Frobenius separates
them; at 7 inertia separates them. A complete cyclic counterexample without
separation is retained. At variable eligible primes the proof instead uses
nilpotence and does not cancel a nonunit cyclotomic difference.

4. **Unramified at only selected variable places?** The argument handles all
q|C outside 2,3,5,7, irrespective of beta support or ordinary assumptions.
The other finite places are covered by good reduction and the twist conductor.

5. **Narrow class group or infinite ramification?** The image is a finite
7-group, so real Galois groups act trivially. Hilbert class field theory with
all places unramified applies. Cl(K)=1 is proved here. No assumption about
arbitrary ray groups or the larger cyclotomic field is substituted.

6. **Overclaim precision?** The exact exponent is floor(n/2)+1. The concrete
n=3 nilpotent with diagonal valuation2 falsifies the full-depth shortcut.
A surviving additive character may still be ramified and nonliftable. The
old ray example remains a useful boundary control for n>=3 on bad 13.

7. **Scalar versus repeated roots?** At good 13 the scalar identity is inherited
from actual semisimple finite-field Frobenius. Scalar -13I and diag(169,1)
have identical characteristic polynomials modulo 49, but different diagonal
entries. Thus trace-only evidence could not supply the depth 2 contradiction.

8. **Norm degree?** The order is the norm from E toQ7 of a rank-two determinant,
so a factor7^m in O gives7^(2m) in the integer order. It is an abelian surface,
not an elliptic curve. At inert rational primes Q=q^2, notq. New11,31 split.

9. **Forced divisor means contradiction?** No. The product1566013238790 leaves
infinitely many integer multiples. The good 13 branch now has n=1, but its
unknown Kummer ratio and eligible support remain. Full reducible, CM, higher
levels, and full Beal are not concluded.

10. **Conjugation silently imposed?** No actual semilinear comparison was
constructed. The paired71 result only forbids simultaneous ramification and
does not force ramification to occur in pairs. r is still inF49, notF7.

11. **Circular computation?** Universal written proofs precede the test grids.
The independent program uses the sqrt5 basis and a complete finite-ring
enumeration rather than the primary phi-basis generated matrices. The
portable verifier deletes outputs in temporary copies and compares fresh
results with pinned references, and reruns the original52 verifier.

Verdict: the written derivations survive this self-review under their explicit
inherited inputs. Independent mathematical review and Lean formalization
remain unperformed, and that limitation is propagated to the report.
