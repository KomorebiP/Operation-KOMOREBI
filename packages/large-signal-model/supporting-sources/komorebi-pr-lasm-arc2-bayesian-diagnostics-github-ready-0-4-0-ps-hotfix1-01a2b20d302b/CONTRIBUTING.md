# Contributing

Changes should be small, typed, executable, and benchmarked.

1. Add or modify a proposal family.
2. Add synthetic unit tests that isolate its semantics.
3. Run the complete test suite.
4. Benchmark only on the public training split.
5. Record exact gains, regressions, runtime, and candidate counts.
6. Do not tune against the public evaluation split.

A pull request that changes the frozen solver must increment the version and
create a new freeze record. Do not overwrite the version 0.2.0 benchmark files.
