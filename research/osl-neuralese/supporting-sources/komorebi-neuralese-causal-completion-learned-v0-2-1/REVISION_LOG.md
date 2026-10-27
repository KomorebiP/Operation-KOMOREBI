# Revision log

## v0.2.1 — adaptive developmental revision

The preserved v0.2.0 quick smoke failed its implementation-validation gate: a single `0.001` tolerance was too strict for deep recurrent replay across NumPy and the upstream PyTorch/BLAS environment. The largest selected discrepancy was `0.02783203125`. This was an execution-parity failure, not a scientific result.

The smoke also exposed a conceptual error in the first audit design. It inserted relation loops at raw learned embedding anchors, although those anchors precede the recurrent transient and are not representative of the learned semantic codebook. Version 0.2.1 therefore inserts registered relation and Cayley paths after a fixed-depth reachable prefix.

Changes:

- preserve every v0.2.0 smoke artifact under `results/development_v0.2.0/`;
- validate depths 1–4 at `0.001` and backend-sensitive deeper replay at `0.03`;
- begin relation, Cayley, and tangent-observability audits after a registered depth-8 reachable prefix;
- add a finite behavioral-fiber audit over every depth-6 history and every continuation through depth 3;
- add the Q0 finite-behavioral-quotient gate.

The scientific thresholds for P1, P2, A1, A2, N1, and the comparative-completion gate were not relaxed. Because the v0.2.0 endpoints were inspected before this revision, v0.2.1 is explicitly developmental and not confirmatory.

### Post-registered numerical supplement

After the v0.2.1 registered result was inspected, `posthoc_numeric_mechanism.py` was added to separate three issues that are easy to conflate: expansion in the original raw parents, contraction and float32 underflow in the projective-trained weights, and normalization of the radial gauge. It also reconstructs finite D4 table-pair support from the frozen training configuration. The supplement does not alter any registered gate or registered result file and is explicitly marked post hoc.
