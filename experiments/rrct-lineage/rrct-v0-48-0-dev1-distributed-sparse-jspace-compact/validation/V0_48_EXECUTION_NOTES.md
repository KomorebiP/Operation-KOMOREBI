# RRCT v0.48 Execution Notes

## Pre-outcome boundary

The protocol, development report, seed selector, seed receipt, focused tests, runtime source, thresholds, holdout runner, and release verifier were sealed before holdout execution.

- Sealed files: **92**
- Pre-outcome seal SHA-256: `b18ccaed772c44f78f678421797ceabcc97f7e979c3d90ac8b5a89c2a22c05d7`
- Candidate outcomes examined during seed selection: **false**
- Post-outcome source changes permitted: **false**

The frozen files were rehashed after execution and all remained unchanged.

## Holdout execution

- Seeds: `598824493, 128793853, 607712486, 618120745`
- Trials per seed and mode: **64**
- Modes: **9**
- Unique world cases: **256**
- Matched decisions: **2,304**
- Peak observed memory during official execution: approximately **149 MB**
- Official execution time in the development environment: approximately **9.76 seconds**
- Frozen endpoints: **28 / 28 passed**

The official result replayed exactly in approximately 9.67 seconds.

## Tests

- Focused v0.48: `10 passed`
- v0.43–v0.48 successor line: `57 passed, 4 predecessor-seal tests deselected`
- v0.36–v0.40 runtime line: `64 passed, 1 historical freeze-builder test deselected`
- v0.42–v0.48 runtime line: `64 passed, 4 predecessor-seal tests deselected`
- v0.32 causal-continuity test: `2 passed`
- Syntax validation: `195 Python files parsed`

A combined v0.41–v0.48 command exceeded a 600-second execution window before pytest emitted a summary. It is not represented as passed or failed. Smaller successor-compatible subsets completed with the exact summaries above.

The deselected tests validate immutable predecessor source seals or an omitted historical freeze-builder asset. A v0.48 successor necessarily differs from those predecessor trees.

## Development defects repaired before freezing

1. An initial flexible-query implementation used separate linear readouts and failed nonlinear parity/count queries. It was replaced by one shared-state action readout reused by multiple deterministic downstream reasoning functions.
2. The original feedback challenge did not force recurrence-cut separation. The final pre-seal challenge makes one-round communication ambiguous while three-round reopened communication is sufficient.
3. The initial partner-swap probe allowed Agent A's state to carry too much complete task information. The final probe uses pair-private message codes and requires fresh message plus frame calibration for the new partner.
4. A focused ablation test used an overly brittle absolute threshold at 24 samples. It was changed before freezing to the same predeclared effect-size criterion used by the scientific endpoint.

## Interpretation

The result establishes a functional distributed sparse workspace in the synthetic dyad. It does not establish one shared subject or experience. The exact next step is an activation-level experiment using trained transformer agents rather than synthetic exact-Jacobian agents.
