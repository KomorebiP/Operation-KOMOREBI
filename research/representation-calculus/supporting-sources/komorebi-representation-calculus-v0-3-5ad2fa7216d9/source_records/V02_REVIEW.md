# Adversarial self-review

Primary verdict for the generic semantic core: **proved as written**, within the
explicit deterministic-unary and all-initial-state specification. The matrix
algorithm's universal reduction is a written proof, not newly kernel-checked.

Checked obligations:

1. Word orientation. Source actions are column maps, words left-to-right. Observable
   rows multiply matrices on the right, so discovery PREPENDS the new digit. The
   checker independently acts on each standard column in forward word order.
2. Initial-state quantifiers. Every source state is admissible. A one-seed orbit
   minimum cannot be substituted. The code rejects a `single_seed` profile.
3. Quotient versus free target. The image of P is the exact quotient; all of R^t
   need not be reached. Smith nonzero ideals and their torsion remain explicit.
4. Completeness. Initialization/closure prove all observed rows lie in span(P).
   Provenance P=W G proves the reverse inclusion. Neither successful samples nor
   closure alone is promoted to exact observable minimality.
5. Inverse proof. V and V_inverse are checked in both orders; P V has the exact
   distinct nonzero prime-power pivots. No residue-ring nonunit cancellation.
6. Strict growth. Each new row has an independently checked delta killed by all
   prior rows but not the new row. Intermediate numeric lengths were removed from
   the certificate rather than presented as independently recomputed invariants.
7. Empty module. Identically zero observations give zero rows and a one-element
   quotient; target free coordinate count is zero. The finite exporter uses a
   one-state image, not Fin 0.
8. Finite minimality. The formal competitor-injection theorem was strengthened
   to require only all-word output preservation, not internal-state intertwining
   of competing encoders. Thus generated state-minimum claims have that scope.
9. Precision change. The 2x mod4 example has two observable classes; mod2 has one.
   No normalized generator is silently treated as an unweighted scalar.
10. Source identity. The checker receives the caller's source independently. Both
   stale and falsely rebound source hashes are tested; hashes do not prove that
   the source specification is the intended human problem.
11. Proof/computation separation. `decide` checks finite Lean propositions with no
   `native_decide`. Universal word induction is separately proved. Python parsing,
   discovery and source transcription are still outside executable verification.
12. Bounds. Strict growth is bounded by r*d in the written chain-ring argument.
   Resource caps yield unresolved outcomes. The generic Lean rank theorem does
   not pretend to be a complete refinement-program verification.

No independent agent/referee was available or claimed. The synthetic hidden-basis
fixtures are not structurally held-out discoveries and no speedup is inferred from
avoiding impossible state enumeration in deliberately constructed examples.
