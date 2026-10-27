# RRCT v0.59 — Reliable Continuous Open-Set Offline Lab

## Status

- Version: `0.59.0.dev1`
- Major blocks completed: **2**
- Deliverable: offline research workbench plus bounded persistent-runtime integration
- Scientific-scale training campaign executed here: **No**
- Bounded smoke, contract, resume, freeze, sweep, wheel, and package validation: **Yes**

## Block A — reliable local control plane

The workbench now implements:

- source-backed feature-truth contracts and strict nondefault-setting enforcement
- atomic checkpoint and run-state writes
- restoration of controller, fuzzy-packet, model, memory, counter, event, and RNG state
- exact interrupted-run resume for the continuous family
- process-parallel sweeps with stable cell IDs, retries, GPU-worker limits, and completed-cell skipping
- cooperative timeout and Python-memory guards
- version-2 source/configuration freezes with exact source-set verification
- frozen execution and post-run audit commands
- PowerShell and Bash launchers for local operation

A deterministic 24-episode continuous run was interrupted after episode 12 and resumed. It matched an uninterrupted reference on metrics, semantic row history, and trajectory digest:

```text
8a9726bd2e6a43e0aed164ec64e8b7bef92e4aaebd36f977d13fd9403fe2e52c
```

A two-cell sweep completed with two workers, then skipped both completed cells on its second invocation. A 43-file freeze verified, ran an 8-episode frozen smoke cohort, and passed its audit.

## Block B — continuous open-set integrated runtime

One controller now persists through a hidden changing event stream:

```text
anonymous observations and prediction residuals
        ↓
moving fuzzy packet field
        ↓
workspace formation, sharpening, or dissolution
        ↓
self / world / partner / provenance hypothesis
        ↓
bounded active probe when uncertain
        ↓
coordinate or model repair
        ↓
provenance-aware memory write or quarantine
        ↓
planner-bound action
        ↓
consequence-driven memory and evidence update
        ↺
```

The evaluator may introduce ordinary intervals, world shifts, internal coordinate shifts, partner/sensor remapping, memory corruption, and changing task demands. Event names and correct answers are not supplied to the controller.

The checkpoint state preserves fuzzy memberships, packet lifecycle, self/world/partner estimates, autobiographical and quarantined memories, repair history, continuity state, counters, evidence budgets, and RNG state.

## Package surface

- Registered settings: **286**
- Major feature switches: **36**
- Scientific experiment families: **8**
- Smoke matrix: **1**
- Presets: **14**
- Sweep templates: **6**
- Canonical archived releases: **14**

## Bounded validation

| Layer | Result |
|---|---:|
| Regression tests | **15 passed** |
| Smoke families | **8 / 8 passed** |
| Presets and sweeps checked | **20 / 20** |
| Python files parsed | **42** |
| Resume trajectory | **Exact** |
| Parallel sweep | **2 / 2 completed; 2 / 2 skipped on rerun** |
| Freeze source set | **43 files verified** |
| Frozen smoke | **8 episodes completed and audited** |
| Installed-wheel probe | **12 episodes completed** |
| Archived releases | **14 verified** |
| Vendored wheels | **2 verified** |

## Claim boundary

This is an engineering/integration release and a bounded synthetic runtime. It does not establish open-world functional awareness, phenomenal consciousness, subjective experience, sentience, valence, welfare, desire, self-preservation, or moral status.

Network access, external-tool autonomy, autonomous persistence, self-preservation reward, valence, negative welfare-like state, and unrestricted file writing are hard-blocked.
