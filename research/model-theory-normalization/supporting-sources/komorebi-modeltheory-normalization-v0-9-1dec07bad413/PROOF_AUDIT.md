# Mathematical self-review

Verdict: the value-preservation and declared arithmetic-unit claims are proved by
the indicated Lean statements, subject to the completed execution records. They
are not a formal claim of compiled runtime or bit-operation complexity.

| Obligation | Review outcome |
|---|---|
| New value is computed by metered routines | Passed by source inspection and projection proofs |
| Actual gcd work omitted? | No; a separate recursive gcd is implemented, counted, and equated to Nat.gcd |
| Arbitrary words and initial states | Inherited all-state contract retained by exact value equality |
| Row order and recomputation | Right action prepends; metered reconstruction is proved equal, no cache assumed |
| Nonunits / integer lattice equality | Inherited positive-pivot solver preserved by projection theorem |
| Early failure / no observations / zero dimension | Explicit costed examples and general fuel theorem |
| Initial normalization | Included; a deliberate omission control rejects |
| Operation count tied to arithmetic magnitude | Old insertionPeak and Euclidean depth theorem yield the needed bound |
| Polynomial count at all fuel budgets | General pending-word horizon/fuel induction, not measured extrapolation |
| Compiler sharing / function-valued arrays | Not addressed; eager-array interpretation stipulated |
| Primitive bit cost, allocation and queue cost | Out of scope; no end-to-end runtime claim |
| Python parser/export/compiler correctness | Not proved; literal source and expected result/count independently audited |
| Priority / independent referee review | Not established |

Dependency chain: existing exact normalized solver and peak bound -> metered
arithmetic projections and exact counts -> metered FIFO projection -> inherited
all-word logical semantics; peak/depth bounds -> per-update arithmetic units ->
full fixed-fuel polynomial bound.

The universal results do not use the generated expected counts as hypotheses.
Those counts are asserted and checked in separate kernel computations. False
counts are intentionally rejected. The audit was conducted by the authoring
assistant, not an independent researcher or independent model.
