# Smith / RLC reading continuation, 12 November 2026

Author: Komorebi P.

This publication reconciles the supplied Codex handoff with the existing reader.
The [reading hub](READING.md) and six source-bound chapters expose the exact-six
closure, composition and open-family results, obstruction propagation,
quantitative transfer and the effective Hughes-margin derivation.

`manifest.json` binds five byte-preserved authored checkpoint ZIPs, six chapter
members, and three handoff state records. The full private handoff, its unrelated
historical archives, personal continuation prompts and third-party reference PDF
are not part of this publication. No license is newly selected. Existing notices
remain in their original archives.

The build authenticates all ZIP bytes before rendering. It validates member paths
and resource caps, verifies the selected Markdown hashes, and serves all authored
members under `documents/smith-rlc/` with their relative paths. Original Markdown,
images, certificates and software remain byte-identical to the selected archives.
The reader rewrites resource links and adds current-status panels and navigation;
it does not edit the retained mathematical statement. The old 172-file research
archive, original manuscript, 42 figure sources and earlier formal receipts remain
unchanged. Five historical sections receive a notice linking to the later closure.

## Evidence and limitations

The fresh [Windows portable replay](verification/portable-windows/summary.json)
passed all eleven standard-library task commands under Python 3.12.14. Read the
raw logs individually. The source runner compared inherited hashes before and
after each isolated replay and reported unchanged sources. The first launch hit
a Windows temporary-directory permission error before any test ran; rerunning
with a writable workspace-local TEMP/TMP directory completed successfully.

This is **result reproduction without independent implementation validation**.
The exact-six checker reconstructs the finite graph equations, checks the
rational root box and positivity, and checks the reduced target degree; its
separate audit supplies derivative and malformed-input rejection controls.
The universal lower-bound/transfer deductions remain self-reviewed written work
with external theorem and physical-reduction obligations. JSON arithmetic PASS
does not discharge them. The three optional solver regressions were not rerun.
No new Lean or hardware validation, minimum resistor count, novelty audit or
general synthesis result is claimed.

The narrower [exact-six replay record](verification/exact-six-v2/manifest.json)
uses the computation-audit v2 schema, records all 52 input hashes before and
after, and has `run.status=completed`. It was validated against the supplied
handoff extraction, its declared source root. Its two tasks repeat the witness
and rejection controls with a bounded runner. This extra provenance check is
separate from the eleven-task portable replay and does not increase proof scope.

Publication checks passed: six new binding/fidelity/link tests, ten existing
research-reading tests, ten laboratory tests, and seven metadata tests. All
1,668 historical mathematical spans remain intact. The new source chapters
contain 216 rendered mathematical spans; the hub adds nine. Browser checks cover
all seven pages at 1440, 390 and 320 pixels, 125% text size, keyboard navigation,
and three representative pages without JavaScript. No unrendered expressions,
MathJax errors, broken chapter images or page-level horizontal overflow were
observed. Full repository CI supplies the complete site build and link audit;
the local checkout is sparse, so unrelated manuscript-dependent tests cannot
all execute locally.

Mathematical self-proofreading covered the new hub, status notices and navigation.
The retained statements were reproduced without mathematical-token edits. This
publication did not independently review their full proofs or external sources.

## Reproduce

From a fresh extraction of the supplied handoff, use its documented commands:

```text
python -B scripts/verify_integrity.py --archives
python -B scripts/run_checks.py --suite portable
```

On Windows, set TEMP and TMP to a writable workspace-local directory if required.
Each individual checkpoint download also retains its own replay instructions.
To validate publication bindings from this repository:

```text
python -B -m unittest discover -s tools -p 'test_smith_chart_continuation.py' -v
python -B -m unittest discover -s tools -p 'test_smith_chart_research.py' -v
```
