# RRCT v0.56 Execution Notes

## Canonical build

The canonical artifact is `0.56.0.dev2`.

A prior dev1 confirmation had completed successfully, but its unuploaded working directory was removed during a sandbox figure-generation synchronization collision. Cached figures and metrics were not treated as a release. The complete study was rebuilt as dev2, assigned new namespaces and 22 entirely new holdout seeds, sealed under a new source manifest, and rerun.

The dev2 cohort is therefore the only canonical scientific result in this package.

## Pre-outcome seal

- sealed files: 12
- status: `SEALED_BEFORE_CONFIRMATION`
- manifest SHA-256: `37ab08dda2c8410c851b1f2bd9bec8722596c6f6583e3f212e869f19b636be90`

The seal includes source, tests, protocol, thresholds, seed receipt, runners, package metadata, and adjudicator.

## Confirmation execution

### Primary

- 16 fresh seeds
- \(\lambda=0.12\)
- 20,000 evaluation episodes per seed
- 320,000 total primary episodes

### Edge

- 6 independent seeds
- 13 price points
- 10,000 evaluation episodes per cell
- 780,000 total edge episodes

### Naïve control

- 6 edge seeds
- 15,000 evaluation episodes per seed
- 90,000 episodes

Total analyzed evaluation episodes: **1,190,000**.

## Result

- status: `V056_CONFIRMATION_ENDPOINTS_MET`
- endpoints: **23 / 23 passed**
- Goldilocks band: `[0.03, 0.22]`
- first underformation price: `0.24`
- overlap break-even: `0.249756`

## Determinism

The runtime sets:

```text
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)
```

Seed namespaces, cue projection, model initialization, training streams, and evaluation streams are all deterministic.

## Packaging boundary

This is a compact standalone pilot, not a merged full RRCT historical release. It includes all code, tests, raw per-seed summary cells, analysis, figures, protocol, and verification machinery needed for this block. It does not include older RRCT source or large transition streams.
