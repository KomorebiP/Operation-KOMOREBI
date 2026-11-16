# Generated explorer-link audit

This audit checks the exact finite readouts reached by the record pages. It
does not infer an infinite identity, mathematical novelty, or correctness of
unimplemented analytic families.

## Assertion and conventions

The population is every parameterized family-explorer link emitted by
`tools/sequence_generalized.py` from the preserved 2,292-record catalogue:
2,169 links, with no sampling. The other 125 family memberships link to a
readable definition and are counted without numerical evaluation. A record
may have more than one family membership.

Each emitted link requests 24 terms. The audit compares the complete requested
window against the stored window, taking the shorter length, and requires at
least eight terms. In this revision 2,160 links have 24 preserved terms, six
have 20, and three have 19. The resulting finite assertion therefore compares
52,017 integer values and their source degrees. It separately checks all
local offsets and any original rational values retained by a record. The
catalogue coefficient hash must also match the preserved OEIS-comparison
snapshot before any link is evaluated.

Coefficients cross the Python/JavaScript boundary as decimal strings. Rational
values are reduced with positive denominators; there is no floating tolerance.
The Python catalogue supplies the preserved coefficients. The actual browser
family engine computes the linked readout. Source-degree maps are reconstructed
from the records' indexing conventions, independently of the URL parameters.
In particular, a supported Appell column selects the ordinary coefficient of
`x^k` at polynomial row `N*n+k`; a point specialization uses its ordinary row
index. The source factorial normalization is retained.

This is an implementation comparison with the preserved catalogue, not an
independent proof of every catalogue formula. Browser layout, event handling,
URL restoration, and download behavior have separate browser tests.

## Reproduction

Python 3.10 or later and a Node.js version supporting ES modules and `BigInt`
are sufficient; no Python or Node packages are needed. From the repository
root, run:

```sh
python tools/audit_sequence_links.py --node node --output .sequence-checks/reports/link-audit/result.json
```

A mismatch or rejected link makes the command fail. The JSON report records
every checked case, the tested index bounds, and separate SHA-256 digests of
the expected and observed finite readouts. Its digest convention is UTF-8
JSON with sorted object keys and compact separators over the object
`{offset, terms, source_degrees, rational_terms}`. `rational_terms` is `null`
when the record does not retain original rational values. It also records
hashes of the complete in-memory input and engine-output streams. Those
streams can be reconstructed from the pinned source files; they are not
duplicated in the report.

## Provenance record

`contract.json` states the finite assertion, conventions, bounds, software
versions, and declared execution/source dependency set. A fresh bounded run
uses the computation-audit skill's `scripts/run_experiment.py`, with every
`execution_artifacts` path passed as `--input`, the chosen fresh directory as
`--output`, and its `result.json` as the single `--result`. The child command
is the reproduction command above with that result path. The recorded limits
are a 240-second wall timeout, a 210-second per-process CPU limit, at most two
cores, one numerical-library thread, and 4 MiB of combined logs. No random
sampling is used.

The runner records the revision and dirty state, actual runtime, before/after
input hashes, exit status, and output hashes in a version-2 `manifest.json`.
Validate that file with the skill's `scripts/validate_manifest.py` and the
repository root. A manifest with a completed process still requires inspection
of the report's assertion and pass/fail status; it does not certify a theorem.
The audit hashes the files used by the computation and its bound sources.
Browser UI files and mutable release documentation are outside this command's
execution dependency set and its mathematical claim.

## Diagnostic origin

The earlier first-four-term development diagnostic found 92 problematic
emitted links: 84 supported Appell columns opened point evaluation, four theta
specializations with `x=9..12` exceeded the accepted bound, and four theta
columns with `k=9..12` exceeded the accepted bound. That diagnostic motivated
the explicit Appell column readout and corrected theta bounds. It was a
limited diagnostic, not a recorded full-prefix baseline audit.

The complete finite-prefix audit below supersedes that limited check and
records the corrected implementation's tested scope and provenance.

## Recorded result: 2026-11-16

The [bounded run manifest](run-2026-11-16/manifest.json) validated as a
completed version-2 evidence record. The [finite comparison report](run-2026-11-16/result.json)
has no failures: all 2,169 links reproduce 52,017 integers, 52,017 source
degrees, 16,032 retained original rational values, and all 2,169 local offsets.
The expected and observed digest agrees separately for every case. This is
finite implementation agreement within the stated windows.

The run took 26.900515 seconds with Python 3.12.14 and Node.js v24.22.1. All
33 declared input hashes were unchanged before and after execution. The
manifest records base revision `eba7991d97e2485c3f1a203760a0f28dc5a1059d`
and its dirty working tree, with exact hashes for the tested modifications.
The preserved catalogue term hash is
`ed9224065b5004fb1e2d9b6cfa42ca286764228760fa9bd271305add6f0eb299`.
The report SHA-256 is
`d29b8b3bffab6e47ec927305f018b97b4b12496073700b42f56a6855676f89bc`.
