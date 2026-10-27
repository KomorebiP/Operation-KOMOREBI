# Learned primitive results

Author: **Komorebi P.** · J-space v0.5 · 2026-09-05

## Finding

The system learns numerical behaviors corresponding to subtraction, multiplication, and addition from examples attached to opaque channel IDs. Its new language executes those learned kernels directly, then synthesizes cubic and quartic programs by composing their calls. Those signals can extend an editable J-like workspace.

**This does not establish unrestricted primitive emergence.** The successful architecture supplies square nonlinearities, and random square features plus learned output weights match the fully trained network. The evidence supports learning the appropriate relation within a supplied polynomial function space. Hidden-feature training is unnecessary for this result.

The generic tanh comparison is a material failure: it learns a useful numerical approximation but cannot reliably serve as a precise, repeatedly composed arithmetic primitive. Final readout fitting matters too; the trained square model before that fit fails strict whole-function validation.

## Experimental boundary

Four separate channels are supplied: `channel_17`, `channel_42`, `channel_91`, and `channel_63`. Their scoring meanings are subtraction, multiplication, addition, and maximum. The learner receives paired inputs and observed outputs, without those arithmetic names. Channel grouping and the number of channels are supplied.

Each channel has a two-input, 12-hidden-unit model with a linear skip connection: **51 parameters per channel, 204 in total**. Matched architectures use tanh or square activations. Both receive 2,048 training examples per channel with operands in [−2, 2], 6,000 Adam steps of batch size 256, then the same least-squares output-layer refit. Three initializations use the same training data. There are 1,024 separate validation inputs per channel; the gate requires maximum absolute error ≤ 10⁻⁶.

The trained-square catalogs accept subtraction, multiplication, and addition in all seeds. Trained-tanh catalogs accept subtraction and addition. Neither accepts `max`. All shuffled-label catalogs accept nothing. Integer rounding is an additional diagnostic, never the acceptance gate.

Model files and prediction files were hashed before scoring. Final query labels were not used for gradient updates or library selection. The designed architecture and synthetic curriculum do encode knowledge of the target family; label isolation does not remove that prior. This is an internal synthetic experiment, not a preregistered or externally blinded benchmark.

## Direct multiplication behavior

Each cell aggregates 1,024 inputs across three kernel seeds. Both operands are drawn from the indicated interval. Values below are maximum absolute errors, not rounded accuracy.

| Kernel | Inputs [−2, 2] | Inputs [−6, 6] |
|---|---:|---:|
| Trained square + refitted readout | 6.22 × 10⁻¹⁵ | 5.33 × 10⁻¹⁴ |
| Random square features + learned readout | 7.11 × 10⁻¹⁵ | 7.46 × 10⁻¹⁴ |
| Trained square before readout refit | 0.00192 | 0.0113 |
| Trained tanh + refitted readout | 0.0940 | 43.98 |
| Untrained square | 5.32 | 40.38 |
| Shuffled-label square | 4.14 | 35.12 |

The tanh model's rounded multiplication accuracy is 99.02% in range and 38.83% on larger inputs. Its in-range mean absolute error is 0.00618. This is real approximate learning but insufficient for strict primitive reuse.

The final square-network coefficients can be expanded algebraically. A read-only audit recovers coefficients near `[0, 0, 0, 1, 0, 0]` in the basis `[1, a, b, ab, a², b²]`. For seed 0 the largest multiplication coefficient discrepancy is 8.82 × 10⁻¹⁶. No coefficient snapping, symbolic replacement, or compiled arithmetic opcode is used during inference. The expansion is evaluated numerically and does not certify floating-point behavior over an unlimited domain.

## Composition

The executor enumerates **2,316 ordered programs** with at most three calls to validated kernels. It receives 24 development demonstrations for each of nine cubic/quartic monomials and promotes a fitting program only after 16 independent validation inputs. No algebraic equivalence or commutativity is assumed. The functions are x³, x²z, xz², z³, x⁴, x³z, x²z², xz³, and z⁴.

For the controlled substitutions below, the same ASTs are evaluated through the other kernels. Unvalidated tanh/control kernels are used only in this explicitly marked evaluation arm; they are not installed as validated production primitives.

| Kernel | Whole function/seed pairs passing, [−2, 2] | Passing, [−6, 6] | Largest error, [−6, 6] |
|---|---:|---:|---:|
| Trained square + refitted readout | **27/27** | **27/27** | 2.34 × 10⁻¹¹ |
| Random square features + learned readout | **27/27** | **27/27** | 3.07 × 10⁻¹¹ |
| Trained square before readout refit | 0/27 | 0/27 | 9.36 |
| Trained tanh + refitted readout | 0/27 | 0/27 | 1,359.31 |
| Untrained square | 0/27 | 0/27 | 1,335.02 |
| Shuffled-label square | 0/27 | 0/27 | 1,294.98 |

A function/seed pair passes only if all 1,024 test inputs have absolute error ≤ 10⁻⁶. Thus 27 means nine functions times three initializations. Tanh rounded composition accuracy falls from 84.20% in range to 25.06% on larger inputs. Even in-range terminal inputs can generate larger intermediate values during composition.

A separate test repeatedly applies the learned two-input kernel to `(state, state)` six times, starting with 128 values in [0.75, 1.25]. All 384 trained-square outputs at depth six remain within 10⁻⁶, with maximum absolute error 1.19 × 10⁻⁷. The errors increase substantially with depth and magnitude. This bounded test is not a general guarantee of stable iteration.

The full score file also contains unequal-magnitude inputs, all pre-refit controls, and random-feature tanh controls. In particular, trained hidden features do not consistently beat random tanh features either. Do not infer a general benefit for hidden-layer optimization from this experiment.

## Editable workspace integration

Each of 144 fresh synthetic tasks combines the six legacy quadratic features with one learned cubic/quartic signal. **The original frozen integration run is given the correct signal entry.** It fits the base coefficients and amplitude from 24 demonstrations using least squares. The new signal is evaluated by neural calls, not a multiplication opcode. The old 734-parameter core and its 24-dimensional state interface are frozen; a shared linear reader adapter is fitted from supplied reader-calibration outcomes.

| Cohort | Successful task/seed pairs | Maximum output error |
|---|---:|---:|
| Queries in [−2, 2] | **432/432** | 2.63 × 10⁻¹³ |
| Queries in [−6, 6] | **432/432** | 6.82 × 10⁻¹¹ |

These are the same 144 tasks repeated with three primitive initializations, and 41,472 output values per cohort. Each task has 32 pairs of query locations and three readers: value, difference, and sum. The fitting mechanism is still supplied, and the success is not attributable solely to the neural core.

Three original snapshots are preserved per bank. New workspaces are named, forkable, editable in amplitude, and undoable. The measured amplitude-edit coherence error is at most 5.33 × 10⁻¹⁵. Changing primitive or core checkpoint identity prevents silent loading of saved expressions.

### Automatic admission follow-up

After scoring, inspection identified the supplied correct-signal index as an integration shortcut. The added `admit_workspace.py` wrapper receives only demonstration inputs, observations, and the learned nine-entry library. It fits every candidate and commits only when exactly one distinct expression has full-rank support and passes the demonstration-error tolerance.

On the same 144 tasks and three checkpoints, it selects a unique fitting signal in **432/432 admissions** and produces states exactly identical to those from the original given-signal run. The admission function receives no family index, coefficients, final query inputs, or query outputs. State comparison happens only after selection. The existing query-prediction replay therefore applies to these identical reconstructed states.

Nine negative checks cover insufficient observations, an unsupported sinusoidal behavior, and two distinct expressions that can represent the same behavior together with the legacy features. All retain the previous bank. The last case demonstrates deliberately conservative ambiguity handling; expression uniqueness is not always necessary for prediction uniqueness.

This is explicitly a **post-score follow-up on an already used task set**, not a new frozen generalization benchmark. It adds automatic selection within a finite library and leaves all original experiment files unchanged. See `results/automatic_admission_audit.json` for every admission receipt.

## Interpretation and next research target

The useful change is that **an operation's executable meaning now lives in learned parameters**, which can be probed and reused. The square model learns the needed cancellation and combination of its features; shuffled or untrained weights do not do this. But the supplied feature family already contains all quadratic relations, so the results do not show discovery of an unrestricted new algebra.

Finite law probes recover different evidence for subtraction, addition, and multiplication. Subtraction fails symmetry and associativity, while the product-like channel supports symmetry, associativity, identity-at-one, and zero annihilation over the sampled probes. These law templates are supplied; passing them is empirical evidence, not a universal proof. The executor does not reorder operands using those results.

The next important gap is **precision-preserving discovery beyond the supplied activation family**, including piecewise operations such as selection, comparison, and conditional writing. This release does not solve that gap, discover operation grouping automatically, or improve an ARC score. It also does not integrate a primitive-learning controller into the earlier ARC solver. The symbolic search is still finite enumeration over a small learned catalog.

## Verification

- Ten tests pass: numerical gradients for both architectures, learned calls, operand order, composition, acceptance rejection, checkpoint reload, changed-meaning rejection, and editable-state preservation.
- All **1,170,432** saved primitive, composition, depth, and workspace values replay exactly in the tested Python/NumPy runtime.
- All 27 saved programs reconstruct identically using their development and promotion evidence, with no final query data passed to the reconstruction.
- Eleven live CLI commands pass, including a nonfinite edit that leaves the persisted bank unchanged and an attempted unvalidated primitive call that is rejected.
- All 11 original frozen source files, 27 frozen model files, and four prediction files match their recorded hashes. Later delivery/audit files are outside the original training freeze and included in the release manifest.
- The PowerShell wrapper was inspected but not executed on Windows.
- The interactive comparison uses actual seed-0 weights. All 720 browser reference values agree with Python to maximum error 6.26 × 10⁻¹³. Its input, amplitude, legend and hover controls passed at 736px and 360px in light and dark themes.

`results/scores.json` uses the historical key `within_1e6` for **absolute error ≤ 10⁻⁶**, not ≤ 10⁶. Frozen experiment code and score keys were retained unchanged. Bitwise replay is an engineering check, not the scientific acceptance metric.
