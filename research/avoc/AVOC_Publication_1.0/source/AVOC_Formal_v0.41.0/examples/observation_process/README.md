# Observation-process examples

These synthetic fixtures exercise the existing calibration parser. They do not
authenticate the log or establish a probability model for real operations.

- `complete_prefix.json`: two warm checked reports are success then rejection.
  A cold report, a warm infrastructure fault, a later warm success, and an exact
  replay do not change the first two warm reports. The result has `n=2,k=1`.
- `insufficient_prefix.json`: one warm success, one warm fault, and one cold
  success cannot supply two warm reports. Calibration rejects the request.
- `thinned_log_trust_boundary.json`: two supplied warm successes are accepted.
  The parser cannot tell whether a rejection was maliciously omitted before this
  snapshot was supplied. Its statistical interpretation requires a complete log.
- `contract.json`: exact finite computation contract for the independent oracle.

Run from the project root:

```bash
python3 tools/calibrate_quote.py examples/observation_process/complete_prefix.json
python3 tools/calibrate_quote.py examples/observation_process/insufficient_prefix.json
python3 checks/test_observation_process.py
```

The second command intentionally returns an error. The oracle itself passes only
when that rejection occurs. No fixture launches an operation or changes a plan.

The oracle compares a fully preloaded latent report table with an independently
unfolded attempt tree. It enumerates every case in the stated bounds using exact
rational arithmetic, rather than random simulation. Attempt identity and fault
rates can depend on public history. The modeled fault does not consume the next
latent checked report, and an admitted report retains either binary outcome.
This is an explicit model; actual external attempts need a justified connection
to it.

A fixed checkpoint is issued only after enough reports exist. Its unconditional
bad-output probability is bounded by the latent-prefix event. The guarantee
includes trajectories that never complete and does not divide by completion
probability. With several predeclared identity/checkpoint pairs, the sum of their
allocated errors bounds any adaptively selected issued result.

Two counterexamples are evaluated exactly. If failures consume an attempted bit
but are labeled faults while successes are retained, calibration for the
attempted-success probability can fail. If the process stops after its first
rejection, conditioning on completion biases the completed sample even when the
unconditional bound is valid. The executable report records the exact masses.
