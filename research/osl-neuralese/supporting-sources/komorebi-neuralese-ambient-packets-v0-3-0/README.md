# Komorebi Neuralese Ambient Packets v0.3.0

This block extends the verified stable-quotient v0.2.0 result into the full ambient latent space.

Version 0.2 separated raw recurrent growth into positive radial gauge and genuine projective drift. It showed that per-step positive-ray normalization keeps the learned computation finite, while an engineered semantic chart executes the exposed finite operator system exactly. The learned terminal-only model nevertheless retained nonzero null-loop drift and eventually lost accuracy at large depth.

Version 0.3 asks what that remaining ambient motion actually is.

## Central hypothesis

The semantic state need not be one activation vector or one preferred ray. It may be a continuation-stable packet in oriented projective space:

\[
\mathbb P_+(H)=(H\setminus\{0\})/\mathbb R_{>0}.
\]

For semantic state \(i\), the finite-horizon packet is

\[
\mathcal K_i^{(K)}
=
\left\{
[h]:\arg\max WM_u h=\tau_u(i)
\text{ for every }|u|\le K
\right\}.
\]

The meaningful stability variable is the distance to the nearest pulled-back future decision boundary, not raw hidden norm and not current-answer margin alone.

The long-term target is a robust task-relative semiconjugacy

\[
\pi_c(F_{c,g}(h))=g\cdot\pi_c(h),
\]

while the remaining ambient fiber may retain scale, confidence, path history, or provenance.

## What this block implements

### Continuation packets

`ambient_packets.py` provides:

- oriented positive-ray normalization without antipodal identification
- exact finite-horizon continuation halfspaces
- Euclidean or SPD-metric packet margins
- packet erosion across nested horizons
- deterministic discovery and heldout suffix splits
- explicit rejection of exact-word or equivalence-group leakage
- validity handling for zero states, nonfinite states, and degenerate constraints

### Gauge-aware operator decomposition

`gauge.py` tests the more general anchor action

\[
B^{-1}M_gB=P_g\Lambda_g+E_g,
\]

where \(\Lambda_g\) contains positive source-state scales and \(E_g\) is off-ray leakage. It separates:

- one global operator scale
- state-dependent radial gauge
- monomial semantic transport
- genuine ambient leakage
- word cocycle error
- repeated-loop scale holonomy
- changes induced by positive anchor-gauge transformations

Statewise gauge equivalence concerns action on the anchor rays. It is not automatically a global equivalence on arbitrary ambient mixtures.

### Switched projective stability

`switched_stability.py` provides scale-safe normalized projective maps and Jacobians. It measures ordered Jacobian products, worst singular amplification, margin-to-amplification risk, repeated-loop ray drift, and nonnormal switching effects.

This prevents individual spectral radius or bounded normalized norm from being mistaken for stability under arbitrary operator switching.

### Developmental frozen-checkpoint audit

`run_ambient_diagnostics.py` reuses the two terminal-only projective checkpoints from v0.2. It does not retrain them. It evaluates:

- diagnostic specificity on exact, globally scaled, statewise-scaled, negative-scale, leakage, delayed-return, and nonnormal controls
- global-scale versus statewise-gauge explanations of learned operator error
- exhaustive continuation-packet membership and radius on frozen contexts
- packet erosion at progressively deeper reachable prefixes
- exact semantic-chart comparison
- switched angular amplification and constant-generator controls
- per-context observability profiles
- repeated null-loop continuation and margin retention

The two inherited checkpoint seeds informed the development of this audit. Their v0.3 results are mechanistic calibration evidence, not an independent confirmation.

## Evidence firewall

Three result classes remain separate:

1. **Integrity:** checkpoint identity, deterministic banks, context/action alignment, finite serialization, and source hashes.
2. **Assay calibration:** synthetic cases where the expected mechanism is known exactly.
3. **Learned-model hypotheses:** gauge sufficiency, packet robustness, switched stability, and harmless-holonomy claims, each of which may fail informatively.

A failed learned-model hypothesis does not make the package invalid. A failed integrity or calibration test blocks interpretation.

Finite packets are task-relative and horizon-relative. Discovery-bank inclusion is descriptive by construction. Only disjoint continuation banks, perturbations, and future operators can provide predictive evidence.

## Retained v0.2 evidence

The package preserves the complete v0.1.1 and v0.2.0 lineage, including:

- terminal-only projective training on D4 lengths 1 through 4
- two-seed D4 accuracy of 1.0000 at depth 64, 0.9924 at depth 128, and 0.8477 at depth 256
- exact state and operator intervention success at depth 64
- cross-seed behavioral transport
- exact semantic-chart execution at every tested family and depth
- residual learned null-cycle holonomy and arbitrary-permutation failure

These parent results are historical inputs. They are not regenerated or silently reclassified as v0.3 evidence.

## Run on Windows PowerShell

Verify the full package:

```powershell
.\VERIFY.ps1
```

Run the fast ambient harness:

```powershell
.\RUN_AMBIENT_SMOKE.ps1
```

Run the complete developmental ambient audit:

```powershell
.\RUN_AMBIENT_PILOT.ps1
```

Both launchers write new outputs under `results/local/`, leaving the sealed
`results/ambient_pilot/` evidence untouched. Local outputs are intentionally excluded
from the release manifest. The deterministic default is CPU. No internet access or
model download is required.

## Reading order

1. `results/ambient_pilot/REPORT.md`
2. `AMBIENT_CLAIM_BOUNDARY.md`
3. `AMBIENT_TEST_PLAN.md`
4. `AMBIENT_PREREGISTRATION.json`
5. `RESULTS_SUMMARY.md`
6. `results/projective_pilot/REPORT.md`
7. `results/stability_pilot/REPORT.md`

## Strongest allowable conclusion

This block can identify whether the inherited recurrent computation occupies robust continuation-stable regions, how those regions erode with depth, and whether angular switching or delayed ambient return explains failure. It cannot establish spontaneous Neuralese, an infinite-horizon quotient, observer-independent meaning, architecture-independent emergence, or awareness.
