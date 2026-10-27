# Changelog

## 0.1.1 — 2026-08-26

- Separates checkpoint-selection validation from the untouched IID test.
- Adds paired canonical/correct/scrambled calibration triplets and disjoint train/evaluation nonce pools.
- Adds matched correct- and scrambled-calibration training arms without formal operator labels.
- Freezes one shared tokenizer, verifies common initialization hashes, and evaluates final checkpoints after identical fixed budgets.
- Records exact effective-corpus digests, counts, token-length summaries, and presentation-independent semantic hashes.
- Adds deterministic label-independent surface markers so balanced large splits remain unique without semantic leakage.
- Balances hard splits across worlds and queries and reports minimum-cell metrics.
- Adds behavioral gate adjudication, counterfactual gates, and complete renaming-triplet calibration-use gates.
- Adds independent data/model seed replication and aggregate reporting.
- Makes project verification hermetic and verifies every saved checkpoint hash.
- Protects completed run directories before any rerun write and verifies arm/corpus identity on resume.
- Refuses heterogeneous replication cells by auditing config, package-manifest, and per-data-seed dataset hashes.
- Saves immutable record IDs aligned one-to-one with every retained prediction list.
- Bundles portable reproducibility metadata without local usernames or paths.
- Fixes SHA-256 fingerprint initialization in the neural training path and adds a direct regression test.
- Derives one shared answer ontology from the declared finite worlds so matched arms have identical output rows, parameter shapes, and initialized bytes.
- Audits tokenizer identity, exact answer-label ordering, parameter schema, and initialized-state hashes across the three central arms.

## 0.1.0 — 2026-08-26

- Added exact algebra, provenance, and consumable-resource worlds.
- Added deterministic executable text generation across nine controlled splits.
- Added full-query counterfactual bundles and episode-specific nonce renaming.
- Added exact replay, leakage, transformation, and shard-hash validation.
- Added majority, question-majority, and TF-IDF leakage controls.
- Added a randomly initialized compact transformer and five supervision arms.
- Added deterministic hashed-word tokenization for unseen identifier identity.
- Added best/last checkpoints, safe resume, per-split evaluation, and bootstrap intervals.
- Added exact quotient and fuzzy lumpability analyses with explicit claim boundaries.
- Added Markdown/JSON reporting, accuracy figures, manifests, and SHA-256 checkpoint hashes.
- Added Windows PowerShell workflows for setup, checking, generation, training, evaluation, resume, verification, smoke, standard, and full runs.
