# RRCT v0.50 Execution Notes

## Development

Exposed development seeds `50001, 50007, 50011` all passed the proposed endpoints. The scientific source, protocol, tests, seed receipt, and holdout runner were then sealed.

## Pre-outcome seal

- Sealed files: **94**
- Manifest SHA-256: `468582772cc907cd788ea8fcf54a84ee8b1dc66e758f17da8a70cf790dcadfbd`
- Candidate outcomes examined before seal: **no**
- Post-outcome source modification permitted: **no**

## Frozen execution

- Holdout seeds: `476798751, 912461818, 486597126, 559071340`
- Execution time in the development environment: approximately 14 seconds
- PyTorch: `2.10.0+cpu`
- Python: `3.13.5`
- All 23 endpoints passed

## Replay

A complete four-seed replay was performed after the canonical run. After removing only output-path fields and recursively generated digest fields, the replay object matched the canonical analysis exactly. All eight learned model-state digests matched.

## Tests

- Focused v0.50: **8 passed**
- v0.47, v0.48, v0.50 line: **28 passed**
- v0.42 through v0.50 successor line: **72 passed, 4 predecessor-seal tests deselected**
- v0.36 through v0.40 runtime line: **64 passed, 1 historical freeze-builder test deselected**
- Python AST validation: **207 files passed**

A combined v0.49 and v0.50 command exceeded the execution window after emitting eight progress dots and no pytest summary. It is not reported as passed or failed. The v0.49 scientific artifact remains independently sealed and verified in its own release.

## Limitation

The shared state is explicitly supplied as a 16-slot temporary workspace. The experiment establishes causal necessity of persistent joint state under controlled resource constraints; it does not establish spontaneous latent-space emergence.
