# Development failures and limitations

1. The first unsplit `j=49` audit exceeded the container call's 45-second wall-clock limit. It produced no scientific result file. No assertion failure was observed, but no completion is inferred. The identical mathematics is rerun in explicitly disjoint, shorter distance intervals. The initial script is preserved in `history/check_irregular_v5_initial.py`.

2. The original v4 bundle was checked before extraction into a mutable work area: all 42 manifest-covered files matched their hashes. Its exact audit was rerun through the imported `run()` function and its scientific results were saved separately. Historical v1-v3 execution counts are not represented as fresh v5 runs.

3. The block for `j=49`, distances 37 through 52, also exceeded the outer 45-second container limit before the wrapper retained its final manifest or scientific JSON. Its short initial log is preserved. The interval was successfully rerun as four disjoint four-distance blocks. The aborted block is not counted as completed evidence.
