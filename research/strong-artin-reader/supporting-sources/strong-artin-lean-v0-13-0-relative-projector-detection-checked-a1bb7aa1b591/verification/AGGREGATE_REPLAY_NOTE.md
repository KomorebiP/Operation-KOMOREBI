# Aggregate replay note

A single outer replay invocation was attempted for all ten new modules. The first four modules completed with compiler exit code 0. The outer container command reached its 300-second wall while beginning the fifth module, so that aggregate invocation is **not** counted as a successful replay.

The remaining modules were then replayed in smaller dependency-ordered batches. Every one of the ten new modules has an individually recorded `.rc` file equal to `0` under `verification/replay_logs/`.
