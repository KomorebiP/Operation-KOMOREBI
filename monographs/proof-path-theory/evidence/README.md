# Evidence layout

Current formal run: `formal_1.7.0/`.
Current integrated release run: `release_1.7.0/`.
Current development failures/corrections: `development_1.7.0/`.

`lean/` and the earlier versioned directories retain historical runs. They
must not be reported as fresh verification of modified sources. The new run
uses pinned cached imports and Lean's own kernel; it is not an independent
validator or a full rebuild of Mathlib. Source hashes bind each record to the
files actually checked.
