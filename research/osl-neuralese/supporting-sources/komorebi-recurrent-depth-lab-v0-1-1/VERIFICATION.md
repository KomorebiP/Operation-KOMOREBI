# Verification record

Verified for this release:

- all Python files compile under Python 3.12
- the standalone NumPy acceptance runner passes 14 required gates
- the optional KM36 `PacketSystem` / `PacketOperator` cross-check passes
- `python -m pytest -q` passes all 16 tests under Python 3.12
- the mock Huginn adapter equivalence test passes
- the Transformers compatibility gate accepts 4.44.2/4.57.6 and rejects 5.16.1
  before model download
- the trajectory analyzer runs on a generated affine fixture with a temporal
  holdout
- the prompt-suite JSON parses, contains 24 unique safe prompts, and has 12
  discovery plus 12 held-out records

The reference result is `outputs/synthetic_summary.json`.

Not executed in this build environment:

- loading the 3.5B Huginn checkpoint
- CUDA, quantized, or BF16 capture
- a real manual-forward equivalence run
- real latent-state interventions

The build environment did not contain PyTorch or the model weights. The adapter
was therefore reviewed statically against the pinned Huginn source and tested
with a mock model that enforces the same recurrence and output-options contract.
The optional dependency now pins Transformers 4.57.6 because Huginn's pinned
remote code uses the Transformers 4.x tied-weight list contract; Transformers
5.x expects a mapping and fails during `post_init` before loading checkpoint
weights.
The first actual model run must pass the fail-closed depth 1/2/4 latent-and-logit
equivalence gate before its trajectories are analyzed.
