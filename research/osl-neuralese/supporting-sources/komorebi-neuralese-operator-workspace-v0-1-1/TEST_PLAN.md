# Test plan

## Automated unit tests

1. Verify the exact \(D_4\) relations.
2. Verify relation preservation under random conjugation.
3. Verify generated targets against independent table execution.
4. Verify that visible operator slots are balanced and therefore nonsemantic.
5. Verify tensor shapes and finite outputs for every model arm.
6. Verify recovery of a known affine coordinate transport.

## Smoke run

The smoke profile verifies the complete train, evaluate, intervene, report, checkpoint, and receipt path. Its optimization budget is intentionally too small for substantive interpretation.

## Pilot run

The pilot profile executes two seeds for all six arms and performs cross-seed transport for the terminal linear-hypernetwork arm.

## Confirmatory revision

Before a confirmatory claim:

- freeze a new archive and source digest
- increase to at least ten seeds
- add parameter and effective-compute matching
- add a state-space-model baseline
- hold out complete algebra families during training design, not only at evaluation
- test architecture-independent intervention sites
- predeclare uncertainty intervals and multiplicity correction
- reproduce on a second implementation
