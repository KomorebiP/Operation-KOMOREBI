# Quantum Seeds and Effective Dynamics

**Symmetry, geometric transport, quantum channels, and bounded refinement towers**  
Paper VII · Komorebi P.

| Read | Pages |
|---|---:|
| [Traditional manuscript](papers/Paper_VII_Traditional_Final.pdf) | 159 |
| [Visual guide](papers/Paper_VII_Visual_Guide_Final.pdf) | 42 |
| [Lean and evidence guide](papers/Paper_VII_Lean_Guide_Final.pdf) | 85 |
| Total | 286 |

Open [START_HERE.html](START_HERE.html) for the reading index.

## Selected edition and scope

This distribution freezes the accepted October 18 final prose edition. The
selected archive's nine current reader copies and their exact hashes bind to
the current source, navigation and final review records. Same-title standalone
uploads with different bytes are distinguished in the freeze reader audit;
upload dates alone do not select a newer mathematical body.

All nine mathematical parts, six supplements, three retained alternative
proofs, 40 worked visual pages, 38 vector plates and 67 exact Lean excerpts
remain intact. The accepted prose edition has 147 statement records, including
142 numbered records, and 107 proof bodies. It preserved 1,795 mathematical
spans exactly; 73 proof bodies are byte-identical to their predecessor and 34
contain the recorded reviewed prose edits. These overlapping inventories are
not independent-discovery or formal-coverage counts.

The inherited September 6 v0.6.0 formal contract has 19 scoped finite items,
323 named theorem declarations in 25 active modules, six separately audited
constructed objects and nine dependency pins. These are distinct units. The
full expanded manuscript and Part II's physical continuum program are outside
that contract. Bounded-operator and geometric results retain their individual
analytic hypotheses. No fresh Lean compilation is claimed by this freeze.

- [Editable manuscripts and guides](editable/)
- [Accepted prose and proofreading report](PROOFREAD_REPORT.md)
- [Accepted validation](verification/final_prose_2026-10-18/RELEASE_VALIDATION.json)
- [Original reproduction instructions](README.txt)
- [Freeze record](FREEZE_RECORD.json) and [progress ledger](PROGRESS_LEDGER.md)

## Verify the frozen package

Extract this single complete ZIP, enter its root directory and run:

```sh
python3 -B scripts/verify_frozen_integrity.py --strict
```

The primary portable standard-library checker validates canonical safe paths,
duplicates, exact regular-file membership, sizes and SHA-256 values. It is
byte-identical to the accepted Paper VI checker. Its exact 21-control receipt
and harness accompany the freeze as reused tooling evidence, not a new VII
control run. The original VII checkers remain unchanged; the earlier checker
uses platform-native path strings. No native Windows execution is asserted.

For the current source, navigation, reader and recorded review/rebuild bindings:

```sh
python3 -B scripts/check_publication_consistency.py
```

That command also needs PyMuPDF. It performs the closed source-preservation
comparison and authenticates recorded source/report pins and reader navigation.
It does not compile Lean, build PDFs or run scientific/control suites. Use a
separate working copy and external output directories for other reproduction
commands in README.txt. Some documentation generators write in place.

The accepted October 18 packaged replay compared exact extracted text and page
counts, with PDF byte equality reported separately. Earlier numerical, rational
and symbolic evidence retains its October 9 date. No Lean, finite experiment,
generator, control suite, TeX rebuild or whole-paper proof audit was rerun by
this freeze. Compiler/Mathlib, Python/TeX dependencies and declared fonts remain
external prerequisites; older environment-availability statements describe
their dated events.

## Research and open use

Five physical continuum targets remain open: anomaly-free refinement, uniform
Feshbach control for the proposed tower, Lorentzian reconstruction, an Einstein
infrared limit, and a positive physical massless spin-two sector. The finite,
bounded and conditional results do not assert these targets.

The author's confirmed open licensing is expressed here as MIT for original
software/machine-readable material and CC BY 4.0 for original writing, figures
and editable writing sources. [LICENSE.md](LICENSE.md),
[LICENSE_STATUS.json](LICENSE_STATUS.json) and [LICENSES/](LICENSES/) give the
full grants, third-party exceptions and embedded-font notices. The STIX notice
omitted by the baseline is supplied; PDF and scientific source bytes are
unchanged. Historical original-project absent-license statements are superseded.

This distribution is frozen as of October 20, 2026, America/Chicago. Actual
checks retain their UTC timestamps. Next sequential freeze: Paper VIII.
No public website or repository was published by this task.
