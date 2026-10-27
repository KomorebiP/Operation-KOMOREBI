# Certificate applicability through revision

## Supplied contract

`code/revision_contract.py` implements a finite dependency DAG. Each obligation declares its direct artifact values and parent guarantees. `code/demo_revision.py` supplies a six-obligation graph and local checkers. The graph is not inferred from arbitrary code. The theorem requires semantic completeness of dependencies and sound local rules; the manager cannot authenticate those premises by checking its own output.

The demonstration tracks two branches:

```text
integer semantics + checker + admitted library
    -> equation validity -> ordered grammar quotient -> submitted capacity rule

finite problem + repair-success sets + nonnegative weights
    -> weight validity -> controller witness -> priced cost assessment
```

Full artifact values are canonically compared. Parent content identifiers bind the exact supplied certificates. Hashes do not establish authenticity, moral authorization, or correctness of an external physical model.

## Outcomes

- **VALID:** matching declared direct inputs, matching established parent evidence, and successful local replay.
- **STALE:** a declared direct input changed. The conclusion may still be true, but old evidence is not reused.
- **BLOCKED:** a required parent is unavailable or its exact supporting record changed.
- **REJECTED:** malformed bindings or failed local evidence.
- **MISSING:** no supplied certificate.

Exact output names and reasons are recorded in `validation/revision_demonstration.json`. Cycles are rejected; unsupported mutual assertions are not treated as proof.

## Actual revision controls

| Revision | Required behavior |
|---|---|
| Arithmetic contract changes | Invalidate equation evidence and its quotient/rule descendants. |
| Grammar order changes | Do not reuse the old earliest-representative quotient or its exact-transcript claim. |
| Rule artifact changes | Recheck the selected rule rather than trusting its filename. |
| Controller horizon changes | Invalidate controller and dependent assessment. |
| Resource prices change | Keep semantic evidence but require a new cost assessment. |
| Universal repair is added | Reject stale repair weights, reconstruct weights and controller, and do not revive an old performance assessment. |
| Parent proof record is replaced | Bind dependent evidence to the replacement rather than merely the parent's name. |

In the actual repair-extension demonstration, the rebuilt controller costs one unit and one record. The prior cost-assessment certificate remains blocked until separately justified. In the independent price-only revision, all semantic certificates remain valid, and a newly checked assessment reports a negative margin of -1,868.

## Crucial negative control

The tests intentionally define a claim u=v while declaring only u as a dependency. Altering v leaves that incomplete registry satisfied while falsifying the claim. This is an explicit failure of dependency completeness, not a claim that the manager detected every hidden premise.

## External and statistical premises

The generic finite graph can record external assertions, but the demonstration does not implement remote authorization, trustworthy clocks, physical model identification, or an auditor for the temporal order of statistical bets. A valid numerical record does not establish that a candidate was frozen or a bet selected before an external observation. Those requirements remain explicit in the statistical theorems and review notes.
