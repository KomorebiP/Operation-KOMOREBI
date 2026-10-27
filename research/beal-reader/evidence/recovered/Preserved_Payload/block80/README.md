# Komorebi Beal research: Block 80
## Restricted primitives and an explicit affine obstruction operator

Version8.0.0.22 September2026. Start with work80/REPORT.md and TARGET_CONTRACT.md.

The bare equation dp=-alpha cup beta now has a global primitive with no auxiliary
ramification. The first-stage geometric matching problem has an explicit15-by-10
linear operator. Its homogeneous kernel dimensions are3,3,2,3 overF49. The actual
affine target, and therefore its7 or8 obstruction coordinates, remain unevaluated.
No one of the eight patterns is eliminated. No new Lean or independent reviewer.

## Replay

Use Python3.10 or newer, standard library only. Disable bytecode and write reports
OUTSIDE this immutable directory:

    python -B verify.py --report ../Block80_Replay.json

Add --replay-predecessor to execute ONLY the immediate Block79 default verifier.
The full historical chain is retained in nested ZIPs but is not rerun by that flag.
The verifier rebuilds four scientific JSONs and the input fixture in a clean copy,
compares entire results, verifies pinned source bytes, and runs rejection controls.

## Supplied-target evaluator

    python -B work80/computations/evaluate_target.py --input ../target.json --output ../target_result.json

Read work80/notes/AFFINE_OBSTRUCTION.md for the15-coordinate target definition.
The evaluator does not produce a global primitive or authenticate its target.
Synthetic inputs and their outputs are explicitly labelled; a zero input is not
evidence that the actual arithmetic problem is soluble.

## Archive structure

predecessor/ contains the exact original Block79 ZIP and all its nested history.
work80/notes contains the written mathematical proofs. computations contains two
independent arithmetic implementations, a source-fixture builder, and the target
evaluator. inputs contains exact pinned source copies and the rebuilt fixture.
verification contains finite certificates and recorded runs. The final extracted-
ZIP replay and final integrity audit are external, avoiding circular checksums.

See CONTINUE_WITH_BLOCK81.md for the exact next target.
