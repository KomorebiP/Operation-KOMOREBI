# Neuralese Entry–Cone–Holonomy Block v0.3.2

**Author:** Komorebi P.  
**Status:** registered execution complete  
**Scientific design:** v0.3.1, prospectively frozen adaptive developmental diagnostic  
**Correction runner and result:** v0.3.2

## Outcome

This block separates three mechanisms in two frozen eight-state D4 recurrent
systems:

1. a seed-localized native-entry defect that recurrent reanchoring repairs;
2. a strictly safe finite observed-state cone through suffix horizon `H=8`;
3. accumulating angular holonomy under repeated semantically identity words,
   with delayed hard-decision boundary crossings.

The strongest defensible conclusion is **finite, path-dependent ambient
holonomy in this registered panel**. The result does not establish a causal
quotient, global invariant cone, universal Neuralese, or a population-level
effect.

## Start here

- `V032_RESULTS_SUMMARY.md` — principal findings and exact counts.
- `V032_CLAIM_BOUNDARY.md` — what the evidence does and does not license.
- `V032_NEXT_BLOCK.md` — confirmatory replication and intervention sequence.
- `results/V032_ENTRY_CONE_HOLONOMY_RESULTS.json` — immutable registered result.
- `results/V032_POSTHOC_SUMMARY.json` — deterministic compact derivation.
- `figures/V032_RELATION_EXIT_BY_CHECKPOINT.png` — checkpoint asymmetry.
- `figures/V032_MATCHED_LEX_COMPARISON.png` — registered severity comparisons.
- `V032_RELEASE_MANIFEST.json` and `V032_SHA256SUMS.txt` — release integrity.

## Integrity anchor

The registered result SHA-256 is:

```text
134135524c0b7017c4611ce385b3853fc33d8d883d1716e60f3f6aa1c9ffba5c
```

All seven integrity and eligibility gates passed. All eight registered
composites are true. `H0`, `X0`, and `X4` are false scientific outcomes under
the preregistered no-all-pass rule; they are not integrity failures.

## Reproduce the post-hoc derivation

The one-shot learned endpoint execution is already complete and must not be
invoked again. The compact tables and Python-only figures can be regenerated
without loading a checkpoint. Install `requirements-posthoc.txt`, then run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -B posthoc_v032.py
```

Verify the distributed release with:

```bash
PYTHONDONTWRITEBYTECODE=1 python -B verify_v032_release.py
```

## Provenance note

The original v0.3.1 bootstrap authenticated checkpoint **raw bytes** by
SHA-256, then aborted before creating a run-start ledger, before checkpoint
deserialization, and before learned endpoint execution. v0.3.2 preserved the
frozen scientific profile and corrected only the execution wrapper. See
`v032/V032_ABORT_DISCLOSURE.json` and `V032_REVISION_LOG.md`.
