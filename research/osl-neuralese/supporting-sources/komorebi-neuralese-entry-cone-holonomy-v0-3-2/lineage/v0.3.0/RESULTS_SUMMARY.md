# Neuralese Bi-Depth Completion Surface — Results

Version: 0.3.0  
Status: registered adaptive developmental follow-up  
Source result SHA-256: `3bddb9174ca7bb1bd217eeefa0421f43575a5838ac0b0ddb845de944fcd15553`

## Outcome

| Gate | Status |
|---|---|
| `C0_nonidentity_control` | FAIL |
| `D0_diagonal_action` | FAIL |
| `E0_execution_integrity` | PASS |
| `H0_hard_rectangle` | FAIL |
| `H1_downset` | PASS |
| `S0_soft_exact_collapse` | FAIL |
| `W0_relator_hard_closure` | FAIL |
| `W1_relator_soft_flatness` | FAIL |

Execution and cumulative down-set consistency passed. Every scientific completion, soft-collapse, and long-path gate failed under its preregistered exact rule.

## Ordinary histories

The full cumulative `(L=8,H=8)` domain contained **33,423,488** decisions. It had **8** errors, for aggregate accuracy `0.999999761`, but only `8/16` episode surfaces passed the strict hard gate. All eight errors were the same seed-0 depth-zero anchor defect: semantic label 2 decoded as 6, leaving 7 hard classes, a two-label merge, and minimum margin `-0.784008`.

The exact history shells reveal a different regime. Across every ordinary history length 1–8, all continuations through H8, both checkpoints, and all 16 episodes, **33,358,080/33,358,080** decisions were correct. Every one of the 128 episode/depth cells had one hard signature per semantic state, with minimum margin `2.397187`. This is a post-hoc conjunction of registered shell results; it does not replace the failed cumulative gate.

Diagonal compatibility passed in all `1792/1792` generator-cells at target horizons 1–7. At target horizon 0 it passed `128/256`: every seed-1 case passed and every seed-0 case failed because the zero-horizon interface could not resolve the anchor defect. Thus future observability repairs the coarse hard partition, but the full registered diagonal gate remains failed.

## Soft microstate

Exact hard profiles do not imply soft collapse. Already at exact `(L=1,H=0)`, every episode failed both soft interfaces. The maximum within-semantic probability-coordinate range lay between `0.000568483` and `0.00166907`; centered-logit range lay between `0.0308183` and `0.118875`.

By exact history `L=8` with cumulative futures through `H=8`, those episode-wise maxima ranged from `0.0111224` to `0.0438472` for probabilities and `0.450168` to `0.963105` for centered logits. The exact tolerance was `1e-10` (or its registered centered-logit scale adjustment), so this is a clear soft/history microstate, not numerical noise.

## Repeated identity paths

The witness block evaluated `336` relation/budget/environment records, covering `172,032` individual cases and **87,908,352** suffix decisions through H8. Hard closure passed `316/336` records; exact soft path flatness passed `0/336`; the matched nonidentity control passed `317/336`. Identity insertions produced `350,757` wrong decisions in `2,193` cases.

| Relation | Added tokens | Environments passing hard gate | Mean / worst H8 survival | First reveal |
|---|---:|---:|---:|---:|
| `f2` | 32 | 16/16 | 1.000000 / 1.000000 | none |
| `f2` | 64 | 7/16 | 0.848145 / 0.250000 | 0 |
| `frfr` | 32 | 15/16 | 0.991699 / 0.867188 | 3 |
| `frfr` | 64 | 12/16 | 0.978149 / 0.720703 | 0 |
| `r4` | 32 | 16/16 | 1.000000 / 1.000000 | none |
| `r4` | 64 | 14/16 | 0.952271 / 0.500000 | 0 |
| `rfrf` | 32 | 15/16 | 0.990601 / 0.849609 | 6 |
| `rfrf` | 64 | 13/16 | 0.971436 / 0.664062 | 0 |

The earliest hard counterexample occurred at total observed history depth **38**: checkpoint seed 1, episode 2, `frfr` with 32 inserted tokens. It remained correct at the loop endpoint and first failed after a suffix of length **3**, with target margin `-0.046918`. Across all hard-failing cases, `1,697/2,193` (`77.38%`) required a nonempty continuation. This is direct delayed observability.

Soft path flatness failed before hard behavior did. Even one `F^2` loop (two inserted tokens) reached worst angle about `0.0535` rad, probability-coordinate drift `0.01109`, and centered-logit drift `0.1602`, while hard decisions still passed. At 32 tokens the mixed relations first crossed decision boundaries; by 64 tokens every relation family failed somewhere. The matched nonidentity control failed in 19 records versus 20 identity-loop failures, so most long-depth failures are not unique to algebraically identity words; they indicate broader path-length fragility with relation-dependent rates.

## Interpretation

The most economical model is now:

\[
\text{entry transient}\;\longrightarrow\;\text{metastable hard decision-cone code}\;\longrightarrow\;\text{margin-crossing path drift}.
\]

This is stronger than “the model merely memorized depth 6”: every ordinary exact shell from depth 1 through 8 had perfect hard continuation profiles through H8. It is weaker than causal completion: raw initialization is not uniformly in the code, soft state retains history, and algebraically redundant paths eventually leave the correct decision cones.

No result here establishes unbounded recurrence, an exact soft predictive quotient, an invariant metric, a normally attracting fiber, architecture-independent transport, or spontaneous Neuralese in general language models.
