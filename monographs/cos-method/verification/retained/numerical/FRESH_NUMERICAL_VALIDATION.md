# Fresh numerical validation: Quadratic-Form Engine / K-COS final combo

Date: 2026-10-07 (UTC). Outcome: **58/58 selected Python test cases PASS**, plus two fresh extreme controls PASS. Zero unit-test failures, errors, skips, or numerical-run timeouts were observed.

## Contract and arithmetic

These are bounded executable checks of the staged final engine, not universal mathematical proofs. Structural and generalized-form checks use binary64 and stated tolerances. The strongest supplied-spectrum path uses exact literal decimal inputs, a positive central spectrum of rank greater than two, directed interval transform evaluation, analytic support/alias and infinite-mode remainder bounds, and a directed upper bound for the multiplicative interval ratio. The upstream verified-spectrum path treats the stored binary64 factor entries as exact dyadics and postchecks a full dense candidate eigensystem.

The coefficient convention is Q = sum(lambda_i Z_i^2). SKAT uses Q = 0.5 ||Gw^T y||^2, with the corresponding factor/spectrum scaling specified in source. Matrix factors and q values are mathematical inputs; uncertainty in a real-world data-generating model is not enclosed here.

## Fresh bounded runs

| Group | Tests passed | Recorded wall seconds |
|---|---:|---:|
| Structural, streaming, residual, realistic SKAT | 31/31 | 15.704 |
| Signed and positive noncentral | 8/8 | 9.774 |
| Directed interval extreme depths | 3/3 | 14.651 |
| Accuracy-driven targets and fail-closed cap | 2/2 | 52.309 |
| Verified spectrum and matrix-to-tail | 4/4 | 49.148 |
| Directed contract and serializer regressions | 10/10 | 0.331 |

Every scientific run had a 900-second wall cap, 900-second per-process CPU cap, 1 MiB combined log cap, one inherited CPU, and numerical-library thread environment values set to one. No hard memory cap was requested. Thread settings are cooperative. Independent groups used separate processes. Timings include imports and wrapper overhead and describe this environment, not a general performance claim.

The 48 production tests and the two numerical controls ran after the finite-domain accuracy and outward-serialization repairs. A final amendment then extended the serializer's infinity guard from the positive-infinity tuple to both infinity tuples and added one nonfinite regression. All 10 directed regressions were freshly rerun on the exact final files. The finite arithmetic paths were unchanged by that guard amendment. The original production-run manifests retain their true at-execution hashes; FINAL_SOURCE_PROVENANCE.json records the final source hashes and the exact amendment.

## Fresh advertised extreme controls

1. **0.02 chi-square with 80 degrees of freedom near p = 10^-5000.** The requested multiplicative probability accuracy was 10^-18. The directed ratio upper bound was **9.2014149826333253... x 10^-20**, with K = 256, L = 14, and interval precision 50 decimal digits. Runtime: **5.218 seconds**, including literal q generation and the independent control. An independently evaluated exact finite-Erlang survival-function interval at the same literal q, using interval precision 140 digits, is fully contained in the returned K-COS log interval. The recorded midpoint is approximately -5000 in log10 coordinates. The full exact q string, all options, returned endpoints, and reference interval are retained in recorded_runs/fresh_controls_final/controls.json.

2. **Exact binary64 dense 64 x 64 factor near p = 10^-16.** A normalized Hadamard basis and dyadic singular values construct a non-diagonal matrix with an independently known exact spectrum. The requested multiplicative accuracy was 10^-12. The directed combined ratio upper bound was **2.7829391894740692... x 10^-15**. All 64 known eigenvalues are contained in their verified intervals. Runtime: **34.618 seconds**. The q input is the exact decimal 131.33201485100517. Full parameters, outward endpoints, spectral certificate, and tail intervals are in the same controls JSON.

## Finalization repairs and decisive regressions

The original v1.9 code had implementation defects that did not invalidate the abstract spectral or stochastic-bracketing theorems:

- The matrix bridge parsed high-precision log endpoints at ambient mpmath point precision and could collapse a nonzero interval to zero width. At mp.dps = 15, endpoints -1.00000000000000000001 and -0.99999999999999999999 both parse as -1. The final bridge preserves literal outer endpoints and rejects the falsely tiny accuracy request in this witness.
- The accuracy wrapper used point expm1 and a default-precision tolerance parse for its acceptance gate. The final gate proves an upper ratio with mpmath.iv and compares it with the lower tolerance endpoint. Requested decimal tolerances are retained exactly in reported metadata.
- Ordinary str(mpmath.iv) uses nearest decimal formatting. For 1/3 and the exact binary64 singleton 0.1, those printed literals can move inward. The final serializer converts the exact binary endpoint tuples to rational integers and uses Decimal ROUND_FLOOR and ROUND_CEILING. Exact Fraction regressions cover signed thirds, the singleton, and exponents +/-5000 at several interval precisions.
- The raw positive backend formerly admitted unsupported negative q and did not prove all domain inequalities in interval arithmetic. The final backend rejects negative q, nonpositive eigenvalues, rank <= 2, invalid finite-input/resource conditions, and unproved tilt/upper-support/MGF inequalities.

The serializer relies on mpmath 1.3.0's exact binary tuple representation. The proof-level guarantee remains conditional on the correctness of the numerical libraries and their elementary directed operations. These tests do not supply a Lean proof of the Python interpreter, interval library, or runtime machine code.

## Provenance and reproducibility

Executed environment: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, pandas 2.2.3, mpmath 1.3.0 on Linux x86_64. The initial primary runtime lacked mpmath; the environment probe failed with PackageNotFoundError, and mpmath 1.3.0 was successfully installed into a scratch-only dependency directory. This was an environment repair, not a failed numerical result. No authoritative input archive was edited.

Each retained raw manifest records the actual argv, UTC start, exit status, enforced caps, original execution paths, execution-input hashes before and after, logs, and declared-result hashes. All seven finite-revision manifests validated with --root immediately after those runs. The final guard run separately validates against the exact final source. Older finite manifests naturally refer to the preceding nonfinite-guard revision; final source hashes and the narrow source amendment are explicit in the provenance sidecar rather than silently rewriting old execution evidence.

Some original generic unit-group contracts marked randomness used for all groups. Interval, accuracy, and directed groups actually use deterministic non-random controls. Structural, signed/noncentral and verified-spectrum groups use the fixed numpy.default_rng seeds present in the hashed test sources. This metadata limitation is recorded explicitly in the final provenance sidecar; the runner does not configure RNG seeds.

Recorded paths begin at the original executed workspace and are retained as provenance. Extracting this release changes that layout; raw manifest --root checking therefore requires the original layout or a path mapping. Their content hashes remain authoritative. The portable replay below uses the release's relative engine folder and writes new logs, results, source hashes, commands and statuses.

From the extracted release root:

```bash
python -m pip install -r verification/numerical/requirements.txt
python verification/numerical/replay.py --include-controls
```

For the focused serializer and acceptance regressions:

```bash
python verification/numerical/replay.py --group directed_contract
```

The portable replay driver was smoke-tested on the exact final engine: 10/10 directed regressions PASS with unchanged source hashes. Its thread caps are cooperative; it does not claim the original runner's OS CPU or memory limits. The full actual recorded runner argv is available in each raw manifest.

## Boundaries retained

The historical v1.8 baseline was 41/41, and v1.9 added four spectrum tests without claiming a fresh combined 45/45 run. The fresh final selection here includes those tests, three realistic-SKAT checks, and ten new directed-contract regressions. Historical benchmark CSV tables, large-scale matrix sweeps, independent heterogeneous Imhof/Davies-style controls, and memory/timing studies are retained historical evidence; they were not all regenerated in this finalization. test_formal_v02.py checks frozen CSV invariants and was not counted as newly computed numerical evidence.

Signed low-rank examples intentionally distinguish an accurate point result from an accepted analytic series certificate. The strongest directed probability contract remains the supported positive central path. Noncentral and signed analytic checks, ordinary floating residual envelopes, streamed factors and scalable range cores are not automatically elevated to a fully verified streamed matrix-to-tail implementation.
