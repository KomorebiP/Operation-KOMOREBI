# AVOC Formal v0.37.0 — verification record

## Result

**PASS within the stated local-project and implementation-test scope.**

- New theorem/lemma declarations: **60**.
- Complete audited inventory: **1,920**.
- Non-audit AVOC modules: **174**.
- Non-audit AVOC Lean source lines: **28,058**.
- Aggregate cached-dependency build: **1,965 jobs, PASS**.
- Full exact-name axiom reports: **1,920 / 1,920, PASS**.
- Deliberately invalid Lean files: **103 / 103 substantively rejected**.
- Inherited non-audit AVOC modules: **171 / 171 byte-identical** to the frozen v0.35 source archive.

## Toolchain

- Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- Nine exact external revisions from `lake-manifest.json`.

The local project build directory was absent at the beginning of reconstruction and was
rebuilt.  Pinned external compiled dependency caches were retained.  This was not a source
rebuild of mathlib or an independent Lean-kernel implementation.

## New source block

- `AVOC/LazyStagedControl.lean`: quote-only guarded Bellman model, checked artifacts,
  executable confirmation and safety.
- `AVOC/LazyStagedRecovery.lean`: sequence-bound intents, commits, idempotent
  acknowledgement and recovery.
- `AVOC/LazyStagedExamples.lean`: checked payoff, installation and recovery examples.
- `AVOC/LazyStagedCodec.lean`: selected-operation JSON interface.
- `tools/LazyStagedMain.lean`: executable Lean entrypoint.

All four AVOC modules and the entrypoint passed direct compilation with warnings treated as
errors.

## Axiom audit

`AVOC/FullAudit.lean` names exactly all 1,920 inventoried theorem/lemma declarations.  The
parser found no missing, extra or duplicate reports.  The union of reported foundations is:

```text
propext
Classical.choice
Quot.sound
```

No `sorryAx`, compiler-trust evaluation axiom or project-specific axiom appears.

## Source scan

The final positive Lean sources were scanned for proof placeholders, project `axiom`
declarations, `native_decide`, proof-tactic `admit`, and unsafe theorem-like declarations.
There were zero hits.  The scanner distinguishes the inherited ordinary function named
`admit` from the proof tactic.

## Negative suite

All **103 / 103** files under `tests/negative/` failed substantively.  Import failures,
missing object files and timeouts are not counted as mathematical rejection.

The three new files attempt to:

- advance the controller using an infrastructure fault;
- mutate the unselected cold artifact during warm success;
- increment the checkpoint during exact duplicate acknowledgement.

All were rejected.

## Executable workflow evidence

Four final regression groups ran against the actual Lean endpoint and Python/SQLite
coordinator:

1. **Warm selected:** completed warm inspection and deployment while the configured cold
   artifact path did not exist.  Warm external calls = 1; cold external calls = 0.
2. **Cold selected:** completed cold candidate validation and deployment while the configured
   warm artifact path did not exist.  Warm external calls = 0; cold external calls = 1.
3. **Commit/acknowledgement interruption:** process exit after warm result commit left sequence
   zero committed and unacknowledged.  Recovery rechecked the retained certificate, advanced
   the checkpoint once, and completed deployment.  Warm external calls remained 1;
   recovery rechecks = 1.
4. **Direct boundary checks:** initial recommendation was `inspect_warm` with value 14,867;
   after warm readiness it was `deploy_warm` with value 15,000.  Quote mismatch,
   infrastructure fault and premature deployment requests were rejected.

Recorded process-inclusive case times on this host were approximately 10.106s, 10.258s,
14.693s and 18.484s.  These are prototype timings, not portable performance guarantees.

The executable evidence is bounded implementation evidence.  The general Bellman,
artifact-matching, invariant and recovery statements are established separately by Lean.

## Provenance qualification

The retained prior v0.36 workspace contained its specification documents but not the promised
full source archive.  v0.37 was therefore reconstructed from the frozen v0.35 cumulative
source and retained v0.36 specification.  That missing intermediate source was not counted as
verified or silently reused.
