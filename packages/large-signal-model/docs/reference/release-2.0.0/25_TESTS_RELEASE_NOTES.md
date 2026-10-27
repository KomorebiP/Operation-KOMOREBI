# 25-test edition release notes

The 25 supplied ARC-AGI-3 local environment trees are bundled directly under
`environment_files/`. No import path or game download is required.

This edition adds:

- static syntax, class, import, and hash validation for all 25 trees;
- official-wrapper smoke testing across the complete suite;
- quick, balanced, and thorough per-game budgets;
- easiest-first, hardest-first, and game-ID order;
- five-game pilot and single-game launchers;
- checkpointed continuation after each game;
- automatic rerun of prior runtime errors;
- optional rerun of all unsolved games;
- per-game failure records without aborting the complete suite;
- JSON and CSV plans, indices, and summaries;
- the original `tests.zip` preserved under `source_inputs/`.

The bundled environment sources are kept byte-for-byte identical to the
contents of the supplied archive. Their hashes are recorded in
`25_TESTS_MANIFEST.json`.
