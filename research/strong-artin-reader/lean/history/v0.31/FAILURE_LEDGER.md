# Failure ledger — v0.31

Failed draft checks below are not proof evidence. Each accepted source subsequently compiled, and the release verifier performs a fresh dependency replay.

## Environment and wrapper events

- The portable runtime was absent initially. Seven local archive parts were assembled and their complete archive hash checked before extraction; extraction completed with exit code 0.
- An oversized development compilation batch was interrupted after ContinuousGaugeCoboundaries. No verdict was captured for the next module. It was rerun individually; subsequent modules were compiled normally. This interruption was not counted as success.

## Rejected draft/API checks

- `Probe`: RC 1, 2.53s. Exact diagnostic: `development/logs/Probe.1789186521050563759.log`.
- `DiagonalMatrixNormModel`: RC 1, 3.33s. Exact diagnostic: `development/logs/DiagonalMatrixNormModel.1789186633047575585.log`.
- `DiagonalMatrixNormModel`: RC 1, 3.41s. Exact diagnostic: `development/logs/DiagonalMatrixNormModel.1789186654498540494.log`.
- `Probe`: RC 1, 2.47s. Exact diagnostic: `development/logs/Probe.1789186699726202210.log`.
- `DiagonalMatrixNormModel`: RC 1, 3.56s. Exact diagnostic: `development/logs/DiagonalMatrixNormModel.1789186745225930241.log`.
- `SimultaneousSpectralRestriction`: RC 1, 3.20s. Exact diagnostic: `development/logs/SimultaneousSpectralRestriction.1789186910632553492.log`.
- `ProcyclicSpectralNormCapstone`: RC 1, 2.49s. Exact diagnostic: `development/logs/ProcyclicSpectralNormCapstone.1789187019534102674.log`.
- `FrobeniusNormResonanceExamples`: RC 1, 0.78s. Exact diagnostic: `development/logs/FrobeniusNormResonanceExamples.1789187086956375342.log`.
- `FrobeniusNormResonanceExamples`: RC 1, 25.50s. Exact diagnostic: `development/logs/FrobeniusNormResonanceExamples.1789187125173021235.log`.
- `FrobeniusNormResonanceExamples`: RC 1, 4.29s. Exact diagnostic: `development/logs/FrobeniusNormResonanceExamples.1789187165235744942.log`.

Causes included exploratory unknown API names, incorrect inverse/scalar coercion normalization, one missing proof argument, deprecated `if_false`, invalid field-notation line breaks, an incorrect import path, missing ZMod field import, and semireducible example aliases. No target theorem was weakened silently to make a failed proof pass.

## Excluded claims

- No claim that invertible degree alone makes the norm surjective.
- No claim that zero total trace suffices at the quotient prime.
- No claim that individually liftable local prescriptions are simultaneously liftable.
- No count or PASS assigned to an interrupted wrapper.
