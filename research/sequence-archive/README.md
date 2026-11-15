# Recovered integer-sequence records

This is the sequence subset of the user-provided archive
`Komorebi_OEIS_Research_Expanded_v2_2026-11-15.zip`, SHA-256
`15c3511fcba9d27547da59cc0440dc6b79b9945ab0fd0b791cdb9167a9118d40`.
It contains 90 original KOM records and 5,487 finite exact terms across
18 families. The preserved registry, generator, b-file checksum list, source
notes, and historical numeric catalogue retain their recovered bytes.

KOM identifiers belong to this archive; they are not allocated OEIS IDs.
The 62 exploratory records carry no novelty claim. The source notes distinguish
classical constructions from newly specified illustrative models, including
the formal ladder recurrence and finite Clifford word-count model.

Reproduce the registry and generated b-files with Python 3.10 or newer:

```text
python reproduce.py --output regenerated
```

The preserved generator's historical CSV control expects the CSV in a sibling
`originals/` directory; that optional control is skipped in this subset layout.
The repository audit separately checks that historical CSV and compares every
generated record with the recovered registry. It also checks all 90 original
b-file hashes. These are finite implementation checks, not proof of novelty,
a Collatz or Carmichael result, or physical network realizability.

`reproduce.py` is the website's portable launcher. It calls the preserved
generator with an output-path class that explicitly writes UTF-8 and LF text.
The original generator uses platform-default newlines in some writes, causing
its b-file checks to fail on Windows. Its source bytes remain unchanged.

The website publishes the source subset and exact data. The complete 42.2 MB
historical ZIP remains in the task workspace. Existing KSEQ atlas identifiers,
generators and exact exports are preserved. Links between archive and atlas
records report only the checked overlap of stored values at equal indices.

Build integration: `tools/sequence_archive.py`. Browser arithmetic:
`website/assets/sequence-archive-core.mjs`. The shared search parser supports
KOM IDs and reports actual offsets for term matches; it never rounds integers.
