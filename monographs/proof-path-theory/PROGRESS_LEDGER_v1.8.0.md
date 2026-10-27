# Progress ledger — publication 1.8.0 / Python 1.6.0

## Lineage

Started from the delivered 1.7.0 ZIP and checked all **719** predecessor manifest
entries. The archive identity and hashes are in `editorial/baseline_1.7.0.json`.
The thirteen prior production Lean modules and all prior tests are unchanged.
The Python export/version module and CLI extend their public interfaces; the
new checker/codec lives in its own module. Existing named schemas are unchanged.

## Completed work

1. Defined finite indexed rule problems and executable strict/causal replay.
   Proved soundness, retention of known nodes, and exact trace composition.
2. Proved that complete replay plus the final model test gives the **least**
   seeded model on the original `Field` semantics.
3. Proved soundness and completeness of finite causal forbidden-node witnesses,
   including reuse under stronger observations and finite assembly of premises.
4. Defined the exact versioned problem/certificate JSON AST codec. Proved all
   round trips, injectivity, decoded-answer soundness and address confinement.
5. Added a separate indexed Python checker, named-field export and wire CLI.
   Generated real record pairs, six compiled semantic fixtures, and 83,994
   exact conformance cases including cycles, malformed inputs and alterations.
6. Extended the existing monograph with full proofs and a sixth visual study.
   Retained all 149 predecessor mathematical environments and all 41 groups.

## Verification

Fresh 18-module builds and own-kernel replays passed. All 283 explicit named
axiom audits passed; 169 declarations are named theorems, including examples.
Ten false-proof controls were rejected for their expected diagnostics. The
explicit extra-axiom control was accepted by Lean relative to that assumption
and rejected by the separate axiom policy. The standard allowed foundations
remain propext, Classical.choice, and Quot.sound.

The source and installed-wheel suites each contain 233 passing tests. Exact
serialized conformance covers 65,536 named protected problems, 16,384 lower-level
cyclic-capable problems, 2,048 alterations and 26 malformed inputs. The actual
Lean byte consumer returns 83,994 verdicts with zero mismatches. Earlier
semantic-cover, binary linear, recovery, retention and covariance checks are
rerun with their original finite scopes. Consult the final execution record for
hashes and timings, not an inferred count from this narrative.

## Failures and repairs

- Trace proof development initially used an incorrect Boolean equality lemma
  interface and needed explicit list/Option equalities. Corrected proofs compile.
- Completeness and codec proofs initially required specialized induction and
  round-trip lemmas. Their failed compiler output is retained, not counted as
  successful verification.
- An early example needed its certificate argument stated explicitly.
- The container's streaming execution mode was unavailable before execution.
  A direct whole-build command then exceeded its outer 200-second limit after
  all 18 modules compiled. The complete rerun passed builds, kernel replays,
  the axiom audit, actual JSON execution and all controls. The interrupted
  partial record is preserved separately.
- The first publication render exposed a split corollary, a short end-of-part
  paragraph and a near-empty ledger tail. The new study and codec discussion
  were rearranged, and the ledger was balanced over three pages. No body-font
  shrinking or deletion of a mathematical hypothesis was used to hide overflow.

Development logs remain in `evidence/development_1.8.0/`; final integrated
records are in `evidence/release_1.8.0/` and `evidence/formal_1.8.0/`.

## Remaining obligations

- Prove the named-source/indexed-problem adapter preserves the original field,
  rule order, admitted leaves, and protected observations for arbitrary input.
- Refine a finite closure producer and serializer all the way to the proved
  checker, including termination and full-result completeness. Witness
  completeness alone is not that producer theorem.
- Prove or separately certify the byte parser/printer boundary. The current
  general codec theorem is over Lean Json syntax trees; IO is tested only.
- Extend rule transport to derivation-valued rules and characterize equivalence.
- Verify native semantic adapters and selected remaining manuscript components.
- Independent review, empirical social-model tests and a license decision are
  separate and must not be manufactured by a successful internal audit.

## Next restart point

Start with `trace_codec.index_problem`, `ProofFieldViews`, and
`ProofPath.Trace.Problem.field`. Define a finite named-source snapshot in Lean,
construct its address maps, and prove derivation/model correspondence under an
explicit bijective node map and certified-rule enumeration. Bind the checked
indexed request back to that exact source snapshot before claiming an
end-to-end source-to-certificate refinement theorem. Keep the byte parser and
resource failures visible as independent boundaries.
