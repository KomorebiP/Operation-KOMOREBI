# Contributing to a closed-scope release

Corrections and reproducibility improvements are in scope. Include the affected claim ID, the exact failing command or mathematical step, the smallest counterexample available, and the expected versus observed outcome.

Preserve the distinction between written arguments and finite checks. Do not weaken a test, expand a claimed tested domain without execution, or modify a frozen baseline solely to make a failure disappear. New results need a proof and independently specified tests before they can enter a later claim register.

New P-versus-NP ideas and large formalization projects belong to a separately scoped branch or release. They are not obligations of version 1.0.0. Historical source archives must not be edited in place. Do not retag a published release after corrections.

No contribution license or assignment is implied by this file; see `RIGHTS.md`.

## Explicit byte sealing

After a reviewed source edit, run `python scripts/seal_release.py --write`, then run `python scripts/verify.py --all`. The seal operation records bytes only; it does not approve a change or turn a failure into a pass. After recording new closure evidence, seal that separately with `python scripts/seal_release.py --write --evidence`. Baseline changes require an explicit scientific explanation.
