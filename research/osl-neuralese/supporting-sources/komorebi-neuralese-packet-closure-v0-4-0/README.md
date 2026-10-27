# Komorebi Neuralese Packet Closure v0.4.0

**Author:** Komorebi P.

This block turns the v0.3 ambient-space diagnosis into a fresh-seed training
experiment. The parent work showed that projective normalization removes raw
radial explosion but does not remove angular drift, continuation-packet
erosion, null-loop holonomy, or large switched tangent gain. Version 0.4 asks
whether exact ambient operator control and a construction/return objective can
close those failure modes at finite depth.

## Core design

Every official model has a twelve-dimensional hidden space with an exact
rank-eight learned anchor plane \(P\) and rank-four orthogonal complement
\(Q=I-P\). This makes the ambient complement nonvacuous; in the inherited
eight-dimensional models, the eight anchors generically span the whole hidden
space and force \(Q=0\).

The official paired \(2\times2\) panel crosses:

| Axis | Level 1 | Level 2 |
|---|---|---|
| Operator | raw Euclidean-normalized matrix | hard polar retraction into \(O(12)\) |
| Objective | matched endpoint/construction supervision | supervision plus composition and delayed return (CR) |

The four arms are `euclidean_supervised`, `euclidean_cr`,
`polar_supervised`, and `polar_cr`. All four share initialization, accepted
training episodes, rejected terminal proposals, construction words, and
training budget within each seed.

The hard-polar cells apply

\[
A_g=U_g\Sigma_gV_g^{\mathsf T},\qquad M_g=U_gV_g^{\mathsf T},
\]

without determinant correction. Thus the executed matrices are Euclidean
isometries by construction, up to audited floating-point error, while the
pre-polar matrices remain learned. This is an architectural stability control,
not evidence that stability emerged from loss alone.

## Evidence firewall

Training D4 endpoints whose complete action is identity or \(r^2\) are
rejected and deterministically resampled. The construction bank likewise
excludes those action groups. Only after every checkpoint is written and
hashed does the runner materialize the exhaustive held-out bank: the empty
identity continuation plus all 170 nonempty binary words through length eight
in the two reserved groups. The empty continuation makes correct decoding of
the captured prefix itself part of packet membership.

The CR loss does use six deterministic return-only construction-side paths—two
each at lengths 2, 4, and 8—whose every nonempty prefix remains outside the
reserved action groups. They receive no endpoint label or packet loss. Thus the
audit is a reserved terminal-action holdout, not an assertion that the CR arms
never rolled out any length-eight path during training.

The pilot separates five kinds of outcome:

1. integrity and assay validity;
2. primary D4 packet closure and deep execution;
3. secondary zero-shot C8 and mixed-cycle transfer;
4. descriptive causal use of the ambient complement; and
5. a paired descriptive hard-polar-stratum CR-objective effect status.

Secondary transfer, ambient-\(Q\) attribution, and CR-objective benefit cannot
be hidden inside the
primary D4 result. Scientific gate failures are retained; only execution or
assay-integrity failures invalidate interpretation.

## Ambient-space causal test

For D4, C8, and mixed-cycle trajectories, the runner compares native rollout,
per-step confinement to \(P\), midpoint removal of \(Qh\), and a deterministic
rank-four random-projector ablation that removes exactly the same midpoint
energy. Ambient use is credited only when native accuracy is at least 0.75 and
removing \(Qh\) causes a meaningful accuracy drop beyond the matched random
control. \(Q\) is an anchor-plane
complement, not a presumed nuisance or observational nullspace.

State transplantation is compared with an exactly recipient-angle-matched
unit-sphere control and a wrong but reachable same-prefix state. Operator
replacement in the hard-polar arm is compared with an orthogonal
relative-conjugacy control and an independently emitted cross-context
operator whose visible slot is balanced deterministically by frozen bank-row
index and flipped only to exclude an exact concrete-table collision with either
the original or the main alternate. The former matches operator geometry, not
necessarily the induced state-space dose; the latter is independent but not
distance matched.

## Run on Windows PowerShell

Verify the sealed package:

```powershell
.\VERIFY.ps1
```

Run a local smoke test:

```powershell
.\RUN_PACKET_CLOSURE_SMOKE.ps1
```

Replay the developmental screen:

```powershell
.\RUN_PACKET_CLOSURE_SCREEN.ps1
```

The official pilot launcher was used once to create the retained canonical
result. In the completed package it safely refuses to overwrite that result:

```powershell
.\RUN_PACKET_CLOSURE_PILOT.ps1
```

Run a non-evidentiary pilot replay in a timestamped local directory:

```powershell
.\REPLAY_PACKET_CLOSURE_PILOT.ps1
```

The smoke, screen, and replay launchers write to timestamped directories under
`results/local/`, so a packaged retained run is never overwritten and repeated
local runs do not collide. They require no model download or internet access.

The one official pilot invocation is machine-restricted to the canonical
`results/packet_closure_pilot/` directory. That retained directory is nonempty
in the completed package, so the runner's non-overwrite guard blocks a second
official invocation. Any pilot run elsewhere requires `--replay`, is labeled
`non_evidentiary_pilot_replay`, and cannot receive a fresh-pilot gate
status.

The official run is sealed to the recorded CPU, Python, PyTorch, NumPy, and
numerical-library build receipt. A replay on another environment remains a
diagnostic and is not promised to be byte-identical.

## Reading order

1. `results/packet_closure_pilot/REPORT.md`
2. `PACKET_CLOSURE_PROTOCOL.md`
3. `PACKET_CLOSURE_PREREGISTRATION.json`
4. `CLAIM_BOUNDARY.md`
5. `DEVELOPMENT_LOG.md`
6. `results/packet_closure_screen_dev/REPORT.md`
7. `results/ambient_pilot/REPORT.md`

## Claim boundary

Even a complete pilot pass would establish only finite-depth packet closure
and causal operator execution in this explicit, small, table-conditioned
architecture. It would not establish spontaneous Neuralese, unlimited
stability, a universal ambient quotient, architecture-independent emergence,
the mechanism of a pretrained language model, awareness, or consciousness.
