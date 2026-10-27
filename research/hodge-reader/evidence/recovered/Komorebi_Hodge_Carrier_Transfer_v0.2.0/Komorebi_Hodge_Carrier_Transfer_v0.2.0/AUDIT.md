# Computation and proof audit

## Authority and arithmetic

The sole inherited authority for the degree-70 seed is the unchanged v0.1.0 ZIP included under `predecessor/`. Its hash is recorded in `MANIFEST.json`. No generated archive has been overwritten.

The new proof-critical arithmetic uses Python integers and `fractions.Fraction`. The frozen certificate is `results/transfer210.json`. Its solver metadata describes discovery, not the proof standard of the final replay.

## Recorded executions

1. `python checks/verify.py`: 46 exact checks passed. All 48 target unit conjugates and 24 source unit conjugates were checked. The target conductor is exactly 210. Every signed auxiliary factor was checked for middle balance.
2. The v0.1.0 `verify_certificate.py` was extracted in a separate working directory and run with `--out` pointing to the new block's predecessor replay record. All 24 checks passed.
3. `python discovery/search_transfer.py --seconds 15`: the portable discovery script was actually executed. It rediscovered the same 14-term certificate from 348 candidate generator columns, with exact integer replay. The output is `discovery/rediscovered_transfer.json`.

The manifest records interpreter, numerical library versions for discovery, actual runtime records, file hashes, and the declared arithmetic domains. Elapsed times are execution measurements, not future-work estimates.

## Universal claims versus finite premises

The global dual inequality at modulus 210 is not inferred from a bounded scan. It follows from a complete check of 27,131 nonnegative vectors of degrees 1 through 13 (143 invariant ones) together with the uniform inequality `31 * degree >= 434 > 420` for degree at least 14. A separate exact shortest-path computation on 210 residue states confirms minimum nonempty return cost 420.

The arbitrary-q obstruction is proved symbolically in `PROOF.md`. Tests at q=6 through q=80 are only benchmarks.

The character-power obstruction is a manuscript Hodge-theoretic argument. Its six numerical premises are exactly checked; no numerical check proves that a carrier is or is not uniruled.

## Failures and replacements

The first Hermite-normal-form membership experiment exceeded its 20-second execution bound and was stopped without a membership conclusion. It was replaced by direct bounded mixed-integer discovery, followed by an exact certificate replay.

Bounded degree-18 matrix scans failed to find the requested positive-weight carriers for the selected residual test cases. Failure of those scans alone is inconclusive. The manuscript subsequently gives global impossibility results only for the explicitly covered classes/families.

Some original publisher PDF and ancillary-log requests failed. The missing files were not used to certify any arithmetic or search completeness. In particular, the original Aoki PDF was not freshly inspected: its precise theorem statements were checked in an accessible primary research paper's appendix, with an independently accessible Fermat correspondence reference where applicable. This source-access limit is retained in the proof note.

## Review and provenance boundaries

No Lean compilation was attempted or claimed. No official mathbox manifest validator was available locally or run; `MANIFEST.json` is a custom provenance record with hashes checked locally. No general Hodge conjecture, complete Fermat census, or universal carrier-existence assertion is established by this release.

The combined degree-210 algebraicity result depends on the geometric proposition in the preceding release. Replaying the preceding arithmetic certificate does not formally certify its geometry. Classical operations used here are not claimed as Komorebi inventions. The target is new to this local proof chain, not asserted to be a previously unknown result across all literature.

An externally listed closed degree-210 character `(1,79,109,121,151,169)` is distinct from this block's target `(2,9,129,142,168,180)`. The latter appears as residual in the cited table. We make no completeness or historical-priority inference from that table.

## Reproduction limits

The final verifier needs only the Python standard library. Discovery requires NumPy and SciPy. A different solver version may produce a different valid identity or time out; neither affects replay of the frozen identity. Any alternative discovery output needs its own exact incidence and geometric-factor checks before use.
