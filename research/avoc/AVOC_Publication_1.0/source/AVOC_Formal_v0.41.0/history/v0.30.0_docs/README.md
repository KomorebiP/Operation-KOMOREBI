# AVOC v0.30.0 — checked affine reuse and preflight economics

Complete cumulative semantic-feedback source release through v0.29, with four new Lean modules and a real-file GF(5) certificate cache.

- 64 new named theorem/lemma declarations; 1,612 total, including helpers/examples.
- Revalidate a saved minimum-width certificate, match its exact linear map, retarget arbitrary affine offsets, and reselect against the current source.
- Proved one-sided opportunity bounds can skip factor searches/revalidation that cannot produce positive remaining gain in the declared cost/menu model.
- Actual cold/warm example: 240 versus 149 declared setup units, both selecting cost 21 instead of 36 per call. Cold/warm break-even: 16 / 10 declared calls.
- A passing preflight can still lose money. This limitation is proved and tested, not hidden.

Start with REPRODUCE.md. Run `python tools/affine_cache.py run examples/affine_cache/cold.json --store /tmp/avoc-affine-new` after building. Reuse that store with shifted.json. Runtime binaries and dependency caches are not included.

These are exact finite-field semantics and declared arithmetic tariffs, not measured physical speedups or an arbitrary affine-circuit optimizer. Read PROOF_BOUNDARY.md before applying guarantees to a real workflow.
