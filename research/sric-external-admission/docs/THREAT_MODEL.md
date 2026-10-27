# Threat Model

## Assets to protect

- validity of the external checkpoint identity;
- fidelity of latent trace capture and replay;
- independence of final semantic evidence;
- protected answer and proof-instance meaning;
- integrity of thresholds, donors, and task partitions;
- preservation of negative results.

## Principal threats

1. Wrong or modified upstream code.
2. Wrong checkpoint or base model.
3. Dirty repository checkout.
4. Latent trace extracted from the wrong layer or token position.
5. Cache behavior differing between clean and replay runs.
6. Final-support traces influencing quotient construction.
7. Gold proof or explicit CoT leaking into semantic discovery.
8. Donor matching that merely changes the answer.
9. Surface perturbations that accidentally alter problem semantics.
10. PrOntoQA content effects mislabeled as algorithmic procedure effects.
11. Covariance corruption calibrated on the final audit itself.
12. Selective reporting of only necessity-positive tasks.
13. Threshold movement after result access.
14. Large quotient memorizing task identity.
15. Probe decodability mistaken for causal mediation.

## Controls

Each threat maps to a source lock, parity test, replay gate, group split, post-seal witness, same-answer donor, twin validator, calibration split, full-population report, minimum-rank rule, causal patch, or fail-closed terminal status.
