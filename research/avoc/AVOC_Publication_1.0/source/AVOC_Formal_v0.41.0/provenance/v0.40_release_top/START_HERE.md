# AVOC v0.40.0

This cumulative release derives calibration's binomial count law from a primitive
finite Bernoulli stream contract. A recursive observation machine preserves each
identity's report prefix, including rejections. Multiple scheduled checkpoints
share that history; unavailable selected checkpoints block plan issuance.

The integrated theorem bounds the unconditional probability of issuing an
uncertified frozen-episode plan by the total finite scheduled error allocation.
It does not assert the same bound after conditioning on sample completion.
Explicit counterexamples show why that stronger statement is false.

Read FORMAL_THEORY.md for the mathematical chain and PROOF_BOUNDARY.md for what
is assumed. OBSERVATION_EXECUTABLE.md describes independently enumerated exact
experiments and their range. REPRODUCE.md gives the pinned verification workflow.
results/VERIFICATION_v0.40.0.md records the final gates.

All examples are synthetic. Applying the sampling contract to a real service,
authenticating complete logs, and calibrating operational costs remain open.
