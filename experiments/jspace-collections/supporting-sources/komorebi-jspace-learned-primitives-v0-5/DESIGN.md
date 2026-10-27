# From primitive observations to editable meaning

Author: **Komorebi P.**

## What changed

In v0.4, multiplication was an available constructor. In v0.5's new expression language, the only terminals are `x` and `z`, and the only operation form is:

```json
["call", "channel_42", "x", ["call", "channel_42", "x", "x"]]
```

The channel identifier resolves to a fitted two-input neural kernel. This particular discovered program behaves like a cubic on the tested inputs. The human interpretation is added after execution, not used as an arithmetic branch in the executor.

The local J-like state is now a composition of a legacy latent state and a learned executable signal. Its coordinate consists of a 24-dimensional core state, a registered expression, and a real amplitude. This is an engineered hybrid state space. It is not evidence that a unique intrinsic J-space emerged, nor is the discrete expression itself an unconstrained continuous coordinate.

## Supplied and learned

| Component | Supplied | Learned or inferred |
|---|---|---|
| Operation observations | Four distinct channels and their input/output examples | Weights approximating each channel's behavior |
| Kernel architecture | Two arguments, 12 units, normalization, tanh/square family, skip/readout form | Hidden and output weights in the trained arm; only output weights in the random-feature control |
| Primitive acceptance | Held-out examples, tolerance and rejection rule | Which channels pass that evidence test |
| Algebraic laws | Candidate law templates and probe distribution | Which templates fit finite kernel behavior |
| Expression search | Ordered AST syntax, terminals, depth and enumeration order | A demonstration-fitting composition and its stored provenance |
| Legacy core | Previously fitted model, geometry, six quadratic input features | No new core-weight learning in this release |
| New workspace | Base-plus-one-signal form and least-squares fitting procedure; correct signal index in the original integration run | Base coefficients and amplitude; signal selection in the separately labeled post-score admission follow-up |
| Reader transport | A shared linear adapter form and calibration observations | Adapter coefficients |
| Editing | Version structure, amplitude action and checkpoint-binding rule | No edit policy is learned here |

Square nonlinearities are a substantial algebraic prior: linear combinations of squared affine forms can express quadratic relations. Numerical multiplication still occurs in matrix arithmetic, optimizer calculations, square activations, the legacy quadratic feature map, and the environment/scorer. The accurate claim is **no multiplication opcode in the new composition language**, not removal of multiplication from the whole implementation.

## Workspace behavior

Each reader retains its existing base response. For a new expression `e`, the contribution is amplitude times a calibrated combination of `e(q1)` and `e(q2)`. Value, difference, and sum readers therefore change coherently when amplitude changes. This is a measurable, editable behavioral coordinate tied to executable meaning.

Changing an operation's weights can change every stored expression that calls it. Banks consequently include hashes of both the core and primitive checkpoints. A checkpoint mismatch stops loading. Future training would need explicit semantic transport or revalidation before existing workspaces could migrate; automatic migration is not implemented.

## Evidence boundaries

The learner never receives arithmetic operation names as input features. It does receive operation identity as a channel label and a supervised grouping of examples. The induction stage fits supplied higher-order behaviors; it does not invent the task curriculum. The reference environment necessarily contains arithmetic formulas to create examples and score predictions. Audits distinguish those oracle calculations from the executable kernel path.

No commutativity is built into enumeration: left and right operands remain distinct, which is essential for the subtraction-like channel. Law probes are read-only diagnostics. They do not silently merge programs or establish formal identities.

The polynomial audit is also read-only. It expands existing square-network weights to explain the learned computation, without rewriting those weights or swapping in an exact symbolic formula. Finite validation alone does not establish uniqueness, and the numerical expansion does not certify every floating-point intermediate.

## What a stronger successor would need

A next experiment should withhold whole kinds of operation, infer usable conditions or branches from residuals, and compare against an equally expressive fixed feature model. It should measure both primitive error and compounded execution error. Selection and conditional write operations would directly connect this scalar prototype to grid reasoning; they are a concrete unresolved target, not a demonstrated capability of v0.5.
