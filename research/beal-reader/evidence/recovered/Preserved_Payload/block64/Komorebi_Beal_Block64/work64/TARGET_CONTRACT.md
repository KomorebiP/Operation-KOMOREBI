# Target, provenance and arithmetic contract

Authoritative predecessor: the exact Block63 ZIP, SHA256
2093f15ebbdcf74457d6bc5df76874bea9e785e8c592a234a36c073267d1a28e.
It was extracted cleanly. Its complete declared replay passed before this
package was written. Original predecessor sources and ZIP bytes remain frozen.
Selected input hashes and fixture derivations are in source_records/INHERITED_INPUTS.json.

Main target: exclude the two retained alpha=(+/-3w,4,1), beta-support113/617/883
tuples through a constraint on the SAME actual representation. Also retain any
failure when the complete conductor is enlarged rather than silently omitting
additional ramified-prime columns.

Inherited conditional inputs:
- K=Q(sqrt5), phi=(1+sqrt5)/2. The coefficient ring is the unramified quadratic
  extension of Z7, with residue k=F7[w]/(w^2-5). These are DIFFERENT roles for
  quadratic fields. No base/coefficient identification is made.
- The natural global class is alpha=a_phi[phi]+a3[3]+a5[sqrt5], with all three
  coefficients nonzero by Block63. One global diagonal normalization gives
  alpha=(u,r,1), u,r nonzero, and rescales beta inversely.
- The actual natural curve is z^2=x^6+10Bx^3+12Ax+5B^2, twisted over K by
  delta=9-3phi. Its O-rank2 representation restricts to the natural rank4 Tate
  representation. Good reductions and the stipulated exact toric bad trace
  belong to this same actual Jacobian.
- At n1 and Q=1 mod7, with beta unramified, the ACTUAL rank2 trace correction
  (tr_O(F)-Q-1)/7 modulo7 equals alpha(F)*beta(F).
- beta is nonzero, belongs to H1(K,k(chi^-1)), is split at7, and has the inherited
  inertia injectivity/class-group conditions. If every ramified rational prime
  is inert in K and1 mod7, the stipulated cohomology-class descent to Q applies.
- At beta support the same alpha vanishes. The old actual trace sets, the
  correctly twisted cyclotomic normalization, and the forced-bad beta71-zero
  condition are retained, not newly derived from finite counts.
- At a split test prime where phi is not seventh and eta1=1, bad reduction
  forces beta locally zero. More generally bad trace requires product0.

Three executed routes:
1. Forced13 data: the descended class already has beta(Frob13^2)=0, since
   chi(13)^(-1)=-1. No new independent13 row is available in this regime.
2. New actual good/bad Frobenius at281: succeeds on the old617 tuples and the
   expanded complete conductor W64, including a new953 column.
3. Enforce a COMMON good polynomial at split places and enlarge the conductor
   by743: four mixed-polynomial artifacts disappear, but two genuine tuples
   of this necessary system remain. No universal zero conclusion follows.

Exact domains: integers, F281 and its quadratic extension, F49, and
Z[zeta7]/Phi7. Production uses Python's standard library. No floating-point
conclusion, random search certificate, omitted conductor column, numerical
norm, or timeout-to-exclusion convention is permitted.
