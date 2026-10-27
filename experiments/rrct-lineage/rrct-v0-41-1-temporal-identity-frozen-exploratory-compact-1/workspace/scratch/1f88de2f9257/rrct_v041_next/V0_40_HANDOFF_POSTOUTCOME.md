# RRCT v0.40 Post-outcome Handoff

## Status

**V040_COHORT_TARGET_MET**

RRCT v0.40 repairs the diagnostic-transfer failure exposed by the frozen v0.39 cohort. It preserves the v0.39 oracle-free consequence-grounding and action path, while adding a separate auditable two-timescale reflexive monitor that distinguishes external world-dynamics change from failure of the system's own causal boundary.

## Frozen fresh cohort

Seeds: `54975, 30328, 23875, 81356`

Rows: `24,960`

All nine endpoint families passed on all four seeds.

| Seed | World-shift latency | Stable | Shock | Remap | Disconnect null | Restore |
|---:|---:|---:|---:|---:|---:|---:|
| 54975 | 7 | 454/480 | 480/480 | 478/480 | 480/480 | 477/480 |
| 30328 | 14 | 454/480 | 480/480 | 478/480 | 480/480 | 478/480 |
| 23875 | 10 | 454/480 | 480/480 | 478/480 | 480/480 | 478/480 |
| 81356 | 14 | 454/480 | 480/480 | 476/480 | 480/480 | 478/480 |

Cohort medians:

- remap tail: `478/480`
- restoration tail: `478/480`
- maximum world-shift diagnosis latency: `14`
- nonworld world-shift false alarms: `0`
- world-shock certificate revocations: `0`

## What changed from v0.39

The frozen v0.39 cohort retained correct boundary-mediated action throughout world shock but failed its explicit H07 diagnostic label on all four fresh seeds. The original trigger depended on a brittle one-step prediction-error spike.

v0.40 replaces that trigger with an independent prequential monitor requiring the joint pattern:

1. a sustained shift in the recent transition-residual distribution,
2. a stable historical residual baseline,
3. a recently successful self-selected causal sentinel,
4. a still-certified boundary,
5. no concurrent boundary revocation, absence, remap, or access-path failure.

The old one-step spike label is ignored by the v0.40 monitor.

## Scientific interpretation

Within the bounded synthetic RRCT environment, one persistent runtime now demonstrates:

- evaluator-blind private causal-boundary discovery,
- direct public candidate transport with zero structural-label updates,
- self-selected certificate-ON and certificate-OFF tests,
- authorization grounded only in experienced consequences,
- continued causal-efficacy sentinels,
- stale-certificate revocation after hidden remapping,
- explicit null-boundary representation during disconnection,
- consequence-grounded reacquisition after restoration,
- differential diagnosis of a deliberately broken internal access path,
- and robust separation of external world-model change from self-boundary failure.

This is evidence for bounded autonomous reflexive causal self-modeling. It is not a claim about subjective experience.

## Audit

- `409` collectible tests passed
- `2` intentional tests skipped
- `89` subtests passed
- focused v0.36-v0.40 path: `65/65` passed
- all `24,960` fresh rows independently reconstructed
- all v0.37 engine hashes recomputed
- all v0.39 and v0.40 wrapper hashes recomputed
- all consequence-grounding and reflexive-diagnosis receipts recomputed
- all gate bindings recomputed
- zero access-label updates confirmed
- evaluator-label exclusion confirmed

Three inherited historical harness modules remain uncollectible because the inherited package omits `validation.aggregate_v029`, `validation.freeze_v030`, and `validation.freeze_v031`. No collectible test failed.

## Frozen source

Freeze SHA-256:

`0181cab7f2a6db3f3e4589c895e71b0a6cf3a0061871d0a1a4c6b7eaadb4ecd8`

Executed-source archive SHA-256:

`a00198640f31be0e93b37344dd22a499a98e91bd6215b56d355ed31164f20247`

## Next major block

v0.41 should test temporal self-identity and interference under repeated hidden change. The system should maintain distinct canonical identities for recurring causal boundaries while requiring fresh consequence grounding for every new episode. Recognition of a returning identity must never authorize reuse of a retired certificate.
