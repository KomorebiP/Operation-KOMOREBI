# H12 fresh finite computation and provenance audit

The selected fresh exact, floating regression, finite chart-data and source-integrity checks completed successfully. Historical provenance is **PASS_WITH_HISTORICAL_RECEIPT_GAPS**: four v0.2 receipt output claims remain **UNVERIFIED** because their referenced replay payloads were not preserved. This boundary does not affect the newly executed v014 results. Seven selected version-2 execution manifests validate against the executed workspace inputs and output hashes.

This packet records bounded computational evidence. It does not certify the infinite canonical product, a gamma/class-field arithmetic equality, or the historical directed phase/branch computation. In particular, the retained v0.6 decimal phase data and directed real-part/branch certificates were checked for archived file integrity, not freshly recomputed. Historical Lean execution receipts are retained provenance; fresh Lean compilation is recorded separately by the Lean companion.

## Fresh runs and precision

Execution environment: Python 3.12.14, SymPy 1.14.0, mpmath 1.3.0; deterministic inputs, no randomness. Times below are wall time measured by the bounded runner, including startup, rather than child-only timing.

| Selected run | Precision and finite scope | Outcome | Runner seconds |
|---|---|---|---:|
| `runs/exact` | Exact integers/Fractions/SymPy; 20 named checks, 5 negative controls; 2,197 triples with all seven lifts on `[-6,6]^3`; 92,480 family points for `n=1..16` | PASS | 1.569137 |
| `runs/numerical40` | Requested 40 digits, **actual 65 working digits**; 4 reflection/anchor identities, 1 finite-difference quadratic-jet diagnostic, 3 negative controls | PASS | 6.581156 |
| `runs/numerical70` | Requested 70 digits, **actual 95 working digits**; the same 4 identities, jet diagnostic and 3 controls | PASS | 6.833254 |
| `runs/independent_centered` | **Actual 80 working digits**, series design 50 digits; 9 named finite checks, 4 controls, 15 floating identities; 4,913 divisor triples, 15,125 family points, 3 exact polynomial samples, 135 complex family positions | PASS | 92.275617 |
| `runs/continuation_diagnostics` | **Actual 80 working digits**, series design 50; 2 original guard triggers reproduced and diagnosed, 3 overlap comparisons | PASS | 4.642578 |
| `runs/visual_values_final` | **Actual 90 comparison digits** against the generator's Decimal 80-digit data; 12 named checks, 175 plotted positions, 5 periods, 289 ceiling digits, 16 count rows, 36 figure payload hashes | PASS | 0.173013 |
| `runs/provenance_complete` | 17 archived source/evidence manifests; 709 output hashes; 11 historical receipts, 68 explicit receipt-file hashes; 3 intake ZIPs; 10 continuation ZIPs and 504 extracted payloads | PASS with 4 historical output claims UNVERIFIED | 1.880938 |

The v014 numerical script explicitly uses `workdps(digits + 25)`. The independent and overlap checks use `workdps(80)` with no additional ambient precision guard; their 50-digit series design parameter controls truncation design. The visual coordinate comparison uses `workdps(90)`. These quantities are distinct and should not be collapsed into a single “40/70-digit computation” label.

## Numerical diagnostics and limits

At requested 40 / actual 65 digits, the maximum recorded reflection/anchor relative residual is `1.920376208316545602734e-62`; at requested 70 / actual 95 it is `1.279199295190116115191e-92`. Maximum direct gamma-series cutoffs are 3,916 and 5,873, with recorded logarithmic tail estimates `3.44865402193332827752e-62` and `2.360118207562638968759e-92`.

The quadratic-jet finite difference uses offset `1e-7` and acceptance tolerance `1e-5`. Both runs record relative discrepancy `3.928429341205943777895e-11`. This is a fixed-offset finite-difference diagnostic, not a 70-digit determination of a derivative.

The independent checks compare transitions and reflection at `0.173+0.013i` and `0.307-0.009i`, plus the anchor and four algebraic/period carries, using the unchanged archived direct-series evaluator and a separately written bounded continuation wrapper. They have relative tolerance `1e-42`, observed maximum residual `2.123050382956265299075999e-72`, cutoff at most 3,719, and logarithmic tail estimate at most `2.960875074506054063696502e-72`. Actual continuation shifts lie between -4 and 20 within the declared `[-40,40]` cap. This is an independent finite check of the formulas and new arguments, not an independent implementation of the gamma evaluator.

Final visual finite-control SHA-256 is `5e19e57e2f8eb8ab0b6a6357bec0488839e459c7ebe0b048ddf3b12e786af74c`; generator SHA-256 is `12b63c73d88a292a46b43bf7164d2d08a67620b44a68173ff9836923c5e9e78c`. Every recorded family member, signed order, coordinate, matrix, cycle, rational coefficient and declared figure payload was checked. The maximum absolute coordinate discrepancy is `2.31621509742466878637968196322e-79`, below `1e-70`. The earlier `runs/visual_values` record is historical: subsequent display edits changed its pinned generator/control hashes; `visual_values_final` is the selected current record.

Floating residuals and the recorded analytic truncation estimates do not supply directed rounding enclosures. No canonical-product value, arithmetic unit, or infinite divisor count was numerically certified.

## Defining conventions and exact finite scope

The checks use `beta = cuberoot(7)*omega^2`, `tau = (beta^2+2 beta)/15`, `t=-tau`, `s=-(beta+2)/15`, and `delta=(tau+2s+4)/7`. The branch has negative imaginary part for beta and positive imaginary parts for t and s. Lattice coordinates are

`lambda(a,b,c) = (a*tau+b*s+c/5)/beta`

and the exact numerator basis in `Q[beta]/(beta^3-7)` is `((2a-b)/15, a/15, (3c-2b)/105)`. The strict chamber indicator is `H(x)=1` precisely when `x>0`, the pivot is `ceil((3c-2b)/7)`, and the smoothing weight is 4 when `5|c`, otherwise -1. The signed order is

`w(c) * (H(j)-H(2j-a)-H(a)+H(b))`.

Exact tests cover the declared integer boxes and growth-family ranges, including injections, disjointness, chamber orders, period carries, removable base points, local canonical coefficients, and reflection/transition/cube exponent extraction on the three stated rational polynomials. Finite complex embedding checks cover the actual n=3 family of 27 distinct zeros of order 4 and 108 distinct poles of order -1. Universal extensions rely on the manuscript proofs or stated formalization scope, not on these finite samples.

## Preserved guard failures and correction

Both first attempts remain in this packet, with their original stderr, commands, bounds and execution manifests. The original code snapshots are retained under `checks/history/`, with hashes matching the corresponding old execution-input records. Earlier manifests retain their executed workspace paths; those paths can now name the corrected script, so the preserved historical snapshot rather than the current script must be used for the old input hash.

1. `runs/independent`: at the first unit-transition denominator argument `beta*(1+(0.173+0.013i))`, the inherited evaluator raised `ValueError: No continuation in declared shift range`. Its declared shift window was `[-12,12]`; the centered admissible representative needs shift 18. The full triggering decimal complex argument is recorded in `runs/continuation_diagnostics/result.json`. This was a declared-domain guard failure, not a failed transition identity.
2. `runs/independent_final`: at `0.307-0.009i`, choosing the admitted representative with smallest absolute shift selected shift 0 too near the open strip boundary. Its predicted initial direct-series cutoff was 41,634, so the unchanged 20,000-term resource cap raised `RuntimeError: Explicit 20000-term resource cap exceeded`. The centered admitted representative uses shift 1. The cap was not increased.

The final wrapper checks only shifts `[-40,40]`, chooses an admissible representative closest to the middle of the original open strip, and evaluates the unchanged direct logarithmic series there. It transports the value by the existing relation `F(z+s)=F(z)/q_t(z)`: for positive k, multiply `F(z+ks)` by the product of `q_t(z+js)` for `j=0..k-1`; for negative k, divide by the product for `j=k..-1`. The analytic definition was not changed. Three overlap comparisons, including a nontrivial different representative at `0.307-0.006i`, pass at tolerance `1e-42`; their maximum residual is `1.03937911161454016250605e-73`. This overlap regression is finite evidence, not a universal continuation proof.

The final successful independent run remained within its 120-second wall / 90-second CPU limits. Its successful result covers all 15 declared identities; no declared transition remains unchecked in that run.

## Historical receipt boundary and source integrity

The four unverified v0.2 receipt output names are `exact_results.json`, `numerical_40.json`, `numerical_70.json` and `lean_results.json`. The receipt refers to replay hashes that differ from the preserved primary evidence payloads. Those primary payloads still match their archived source manifest. Full expected and preserved hashes, unique bare-filename path resolutions, and the exact receipt path appear in `runs/provenance_complete/result.json`. Intermediate strict provenance failures are preserved in `runs/provenance_final` and `runs/provenance_resolved`, with their executed script snapshots. They were resolved by recording the missing-payload boundary, not by modifying an archive or declaring the claims verified.

All 577 files present in the initial source snapshot remain byte-identical and present. Root subsequently added 154 foundation-source files, giving 731 archived source files in the final snapshot; none was altered by this task. `SOURCE_SNAPSHOT_BEFORE.json`, `SOURCE_SNAPSHOT_AFTER.json`, `SOURCE_INTEGRITY_AFTER.json` and `SOURCE_INTEGRITY_FINAL.json` record this distinction. The four copied executable source files also remain byte-identical to their archived originals.

The 17 source/evidence manifests verify their stated archived file hashes; legacy version-1 metadata does not authenticate historical execution, a repository revision, or machine-enforced runtime limits. ZIP hashes, CRC tests and extracted-byte equality establish package integrity only. These checks do not imply a mathematical theorem.

## Resources, records and replay

Each recorded run has a deterministic contract, command, input hashes before and after execution, declared JSON result, raw stdout/stderr, resource-limit record, output hashes and exit status. Fresh selected manifests were checked by the bundled Mathbox validator; see `FRESH_MANIFEST_VALIDATION.json`. Execution paths in those historical records are the actual workspace paths at execution. After relocation, hashes remain authoritative and new replay manifests use the extracted package's paths.

All runs declared one CPU core, one cooperative numerical-library thread, 1 GiB per-process address-space limit, and 1 MiB output cap. Exact, numerical, independent and provenance groups use 120 seconds wall time / 90 seconds CPU; chart-data and overlap groups use 60 seconds / 45 seconds CPU. Affinity and OS resource enforcement are recorded by the runner. No blocking tool wait exceeded the communication checkpoint interval.

Use `README.md` and `replay.py` for a relative-path replay from an extracted final package. The portable driver is syntax-checked; the listed fresh mathematical runs were executed with the recorded original commands, not claimed as an additional full portable-driver rerun. Installed dependency directories and generated Python caches are excluded from the final packet. The numerical code, selected evidence and finite-data hash pins are frozen at this closeout.
