# Claim boundary · 2.3.0

## Verified here

Finite real signal and image coordinate reconstruction, complete packet pruning,
explicit FIR polyphase decomposition, chunk-independent causal FIR, input
contracts, bounded source-archive round trips, typed regression fitting,
common-target candidate scoring, and observed-transition graph behavior were
executed in the local Linux/Python 3.13 environment. Numerical tolerances and
case counts are in `verification`. “Exact” refers to the declared finite algebra
and reconstruction up to float64 roundoff, except explicitly integer-only checks.

## Conditional mathematics

The transform identities require the stated finite domain and complete coordinate
families. Haar depth is constrained by divisibility. Best-basis optimality is only
over complete prunings of the supplied finite tree under the supplied additive
cost. Deterministic replay depends on sufficient state signatures and matching
observations. Hash equality does not prove that a partially observed environment
has no hidden state. Source checksums detect changed payloads, not authorship.

## Learning and scale

The fixed transforms, seeded projections and finite operator grammar are not
trained neural components. Coefficients and finite-candidate weights are learned
from transition data. Replay stores observations. No general grammar discovery,
pretrained large model, or scaling-law result is claimed by the word “Large”.
The standalone continuous-signal runtime is not automatically a trained general
forecasting, audio, or multimodal system.

## Not established

There is no official ARC score, general intelligence result, universal inference
or planning result, theorem prover for the implementation, or fresh Lean build
in this release. The 35 identification scenarios are generated from mechanisms
inside the supplied grammar. Their success does not establish open-world
operator discovery or transfer to unrelated physical data.

Posterior weights are conditional on the supplied candidates. A large weight can
occur even when all candidates are poor. The clipped Gaussian event outputs are
heuristic bounded scores, not empirically calibrated event probabilities. The
finite negative controls do not by themselves establish calibration or robustness.

The preserved signal reconstruction and Euler documents retain their own claim
maps and recorded failures. Their proofs or numerical results are not certificates
for this runtime. Windows/Python 3.12 CI, external ARC runtime execution, PyPI
publication and GitHub publication were not performed here.
