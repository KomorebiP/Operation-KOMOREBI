# v0.24 route record: compatible-target continuation

Base: exact v0.23 archive 56ebe6213cad43a0f7c85e40df30c7407a15637e8ece100bd0e972979e2a0418.
Additional mathematical dependencies: unchanged v0.19 Hensel modules and v0.16
auxiliary-column construction, with archive/source hashes in MANIFEST.json.

## Target contract

Prove the next v0.23 bridge:

    selected dual kernel = syzygies
      -> augmented image = syzygy annihilator
      -> valid nonlinear lifting inside the compatible target.

Do not manufacture a Selmer comparison or an automorphic carrier.

## Outcome

The linear statement is proved over every field; finite dimensionality is
unnecessary. Its direct v0.23 presentation instance is checked.

The nonlinear statement is proved AFTER an explicit restriction: an integral
split compatible target, actual nonlinear compatibility on the residual fibre,
and the v0.19 projected right-inverse/Taylor inputs. A second checked route
eliminates known exact graph-form redundancies B(x)F(x).

## Decisive negative checks

F(x)=(x,x^2) has horizontal derivative at the origin but F(2)=(2,4) over Z/8Z.
The true relation (-x,1) varies. Therefore the proposed general implication from
residual syzygies to fixed-target nonlinear compatibility is false.

Over Z/4Z, C=2R contains 2, which is ambient-divisible by 2 but is not divisible
by 2 inside C. Thus a submodule inclusion need not reflect the power filtration.

Both counterexamples are Lean proofs, not numerical samples.

## Evidence

See RESULT.json, verification/fresh/logs and AxiomAudit.lean. All direct sources
are replayed in the pinned runtime; every new theorem/definition is axiom-audited.
Development failures are recorded in FAILURE_LEDGER.md and the append-only
attempts.jsonl. Historical ancestor PASS records are not substituted for the
fresh direct-dependency replay.

## Next question

Can the actual arithmetic relation system be reduced by exact identities, or
can one prove compatible normalized defects at every square-zero layer? This
is not resolved by the present linear image theorem.
