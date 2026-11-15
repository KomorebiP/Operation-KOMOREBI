# Retained official OEIS bulk snapshot

`stripped.gz` and `names.gz` were downloaded directly from the official URLs
listed by <https://oeis.org/wiki/Download>. `snapshot.json` records retrieval
time, response dates, byte counts, and SHA-256 hashes. The original gzip bytes
and their embedded notices are retained. This snapshot has 401,422 term records.

Data attribution: The Online Encyclopedia of Integer Sequences, OEIS Foundation
Inc., <https://oeis.org/>. OEIS data are available under CC BY-SA 4.0:
<https://oeis.org/LICENSE> and
<https://creativecommons.org/licenses/by-sa/4.0/>. Reference matching, extracts,
and presentation are adaptations. This is an independent Komorebi interface.

The exports contain names and finite term excerpts. They do not contain the
mathematical offsets, full formulas, comments, or histories. Export positions
must never be substituted for mathematical offsets. A finite match is not a
proof of infinite sequence identity; absence of a hit is not a novelty result.

To obtain a newer snapshot, choose a new output directory:

```text
python tools/fetch_oeis_snapshot.py --output NEW_SNAPSHOT_DIRECTORY
```

Then retain the reviewed source files here and regenerate comparisons:

```text
python tools/update_sequence_library_oeis.py --source research/oeis-snapshot --output manifests/sequence-library-oeis.json
```

CI uses the retained files and checks their hashes. It does not fetch a moving
daily export. The public full-reference finder loads the compressed files only
after an explicit search, and scans them in a background worker without keeping
all decompressed terms in memory. Local queries are not sent to OEIS.
