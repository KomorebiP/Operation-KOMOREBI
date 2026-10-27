# Streaming Polyphase Factor Decomposition / SKAT

**Edition guide · 27 October 2026 · Software: beta / work in progress**

Start with the [45-page illustrated manuscript](../../research/streaming-skat/FINAL_MANUSCRIPT.pdf), then read the [v0.9 verification record](../../research/streaming-skat/VERIFICATION_V09.md) and [simulation audit](../../research/streaming-skat/PROOF_AND_SIMULATION_AUDIT_V09.md). The manuscript is **v0.8**; the latest retained simulation continuation is **v0.9**. These identify different artifacts in the same development.

## Edition map

| Material | Edition and role |
|---|---|
| [Manuscript PDF](../../research/streaming-skat/FINAL_MANUSCRIPT.pdf) and [LaTeX source](../../research/streaming-skat/FINAL_MANUSCRIPT.tex) | Illustrated manuscript v0.8, dated 23 September 2026 in the source. |
| [VERSION](../../research/streaming-skat/VERSION) | Package version marker `0.8.0`; it has not been silently changed to match the later simulation notes. |
| [v0.9 verification](../../research/streaming-skat/VERIFICATION_V09.md) and [audit](../../research/streaming-skat/PROOF_AND_SIMULATION_AUDIT_V09.md) | Later synthetic simulation continuation and cumulative regression record. These do not identify a new v0.9 manuscript. |
| [Original README](../../research/streaming-skat/README.md) | Begins with the v0.5 heading and contains later v0.7 and v0.9 additions. Read each section as its own checkpoint. |
| [v0.6 README](../../research/streaming-skat/README_V06.md) | Historical scheduler checkpoint and its original reproduction instructions. |
| [Theorem index](../../research/streaming-skat/THEOREM_INDEX.md) | Written statement map. It is not a Lean compilation receipt. |

## Recorded tests and their scope

The retained v0.9 record reports the following **31 passing tests**. These are historical source records; this navigation update did not rerun the tests or simulation battery.

| Test file | Recorded pass count |
|---|---:|
| [test_streaming_skat.py](../../research/streaming-skat/test_streaming_skat.py) | 6 |
| [test_approximate_lightcone.py](../../research/streaming-skat/test_approximate_lightcone.py) | 5 |
| [test_budget_scheduler.py](../../research/streaming-skat/test_budget_scheduler.py) | 4 |
| [test_spectral_tail_bridge.py](../../research/streaming-skat/test_spectral_tail_bridge.py) | 5 |
| [test_residual_trace_cap.py](../../research/streaming-skat/test_residual_trace_cap.py) | 5 |
| [test_residual_completion.py](../../research/streaming-skat/test_residual_completion.py) | 3 |
| [test_realistic_skat.py](../../research/streaming-skat/test_realistic_skat.py) | 3 |

The older [test_formal_v02.py](../../research/streaming-skat/test_formal_v02.py) is separate from this 31-test census. “Formal” in that filename does not denote Lean verification.

For a new replay, use a separate checkout, record Python and dependency versions, and run the seven named unittest modules from the component directory. The modules use NumPy, with SciPy and pandas required by parts of the suite. Record the exact source commit and complete output. A successful replay of these tests would not reproduce the larger simulation battery or rebuild the manuscript.

## Corrections and remaining work

The v0.9 record corrects the earlier copy-LD simulator's use of `np.empty` followed by `+=` by initializing with zeros. **Earlier copy-LD benchmark numbers are not authoritative validation.** Use the corrected record and its source.

The recorded simulations concern Gaussian SKAT-style quadratic forms under synthetic rare-variant LD models. External cohort replication, finite-sample logistic calibration, and native GPU performance remain separate tasks. The deepest adaptive queries also produced overflow warnings in an intermediate rejected certificate-growth calculation; the recorded accepted certificates were finite and matched the reference, while log-domain hardening remains open.

The completion label remains **Active development**, Lean coverage **No Lean claim**, and confidence **Written / finite evidence**. Navigation consolidation does not upgrade these scientific classifications. The next steps are a pinned replay, review of the spectral-tail and simulation contracts, and the documented numerical hardening.

[Status and evidence](../STATUS_CATALOG.md#streaming-skat) · [Source directory](../../research/streaming-skat/) · [Finalization queue](../FINALIZATION_QUEUE.md) · [Research index](../../research/README.md)
