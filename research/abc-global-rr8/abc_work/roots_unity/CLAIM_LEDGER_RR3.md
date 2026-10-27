# Versioned claim ledger: ABC-20261025-RR3

Parent: RR2 archive SHA-256
f5b5e7336d5cae31502106100997cf02733b1054f62e3df39827002cfe7e9469.
The prior archive and its live-view snapshot are retained. Root-of-unity
work has its own live view here, leaving the pinned RR2 inputs unchanged.

Target: for every epsilon>0, finiteness of primitive positive triples a+b=c
with c>rad(abc)^(1+epsilon). The target is not reached in this checkpoint.

| ID | Exact result | Evidence and scope |
| --- | --- | --- |
| RU1 | Coefficient roots-of-unity projectors select residue lanes; torsion removal preserves first-contact valuation exactly | [Local proof](routes/padic/PROOF.md), [review](reviews/local_aux.md) |
| RU2 | Depth period d_k=d p^max(0,k-s); compatible joint periods combine by lcm, and local complete-period means retain the positive birth contribution | [Character proof](routes/characters/PROOF_NOTE.md), [review](reviews/characters_cyclotomic.md) |
| RU3 | Standard Fourier resolvents retain primitive pole depth; canceled packets of a coprime fixed combination divide its resultant, with the displayed coefficient/degree bound | [Cyclotomic proof](routes/cyclotomic/PROOF_NOTE.md), same review. The fixed finite prime set requires both conductor and coefficients fixed |
| RU4 | The optimal two-term p-adic torsion-distance constant equals p^(-s); existing theorem constants do not provide a uniform estimate of s | [Transfer and source contracts](routes/torsion_distance/TRANSFER_REPORT.md), [review](reviews/torsion_distance.md) |
| RU5 | A modular auxiliary coefficient vector can evaluate identically to zero; nonzero evaluation requires height at least M/S_D(A,B) | [Auxiliary proof](routes/auxiliary/PROOF.md), [review](reviews/local_aux.md) |
| RU6 | Exceptional birth factors lie in distinct birth cyclotomic packets; their total degree supplies a uniform restricted pointwise criterion | [Order-budget proof](routes/cyclotomic/ORDER_BUDGET.md), [review](reviews/order_budget.md) |
| RU7 | For fixed epsilon>0 and 0<delta<1, exceptional output primes bounded by n^(1-delta) suffice for the ABC inequality at all sufficiently large n, uniformly in the bases | [Prime-cutoff corollary](routes/cyclotomic/ORDER_CUTOFF_COROLLARY.md), [review](reviews/order_cutoff.md). This is a restricted sufficient condition, not an automatic bound on exceptional primes |

These are elementary written mathematical results plus the checked contracts
of the cited primary torsion-distance theorems. No historical priority,
external peer-review, or Lean-kernel certificate is claimed. Separate agent
reviews reconstruct the displayed implications but are not formal certificates.

The per-depth density saving N/(d p^(k-1))+1 is refuted by the explicit
base-2, p=1093 example. Multiplication of marginal exponent-contact densities
is refuted by the exact joint congruence law and synchronized examples.
A uniform output-only sublinear birth budget covering bounded n is also
refuted. These are failed proposed lemmas, not counterexamples to ABC.

Two resolved drafting/verification failures are preserved:

* The original auxiliary note incorrectly said the adjacent relation vectors
  need not form an integral basis. Under coprimality they do. The false aside
  was removed, its source snapshot retained, and the unaffected main statements
  audited on the corrected revision.
* A manually selected cyclotomic control initially had p not dividing its
  output. Its domain assertion caught the error. The corrected control and
  successful rerun are documented in `routes/cyclotomic/RUN_NOTES.md`.

The inherited RR2 fixed-offset correction remains in `../ERRATA.md`.
No previous mathematical status was silently overwritten.

The open obligations are a global simultaneous-contact height/radical bound,
a controlled nondegenerate adaptive auxiliary construction, and coverage of
arbitrary primitive inputs. RU6 is a sufficient restricted criterion. It
does not establish the conjectural bound on every triple.
