# Verification

Automated regression tests:

```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/generated/interface/models.py", line 32317, in hydrate_crdt_from_proto
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/remote.py", line 749, in __call__
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/client.py", line 150, in call
artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.
test_AT_action (__main__.StreamingSKATTests.test_AT_action) ... ok
test_A_action (__main__.StreamingSKATTests.test_A_action) ... ok
test_dual_action (__main__.StreamingSKATTests.test_dual_action) ... ok
test_kernel_action (__main__.StreamingSKATTests.test_kernel_action) ... ok
test_stream_gram (__main__.StreamingSKATTests.test_stream_gram) ... ok
test_tiled_gram (__main__.StreamingSKATTests.test_tiled_gram) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.009s

OK

```

Benchmark shape:

- n = 256
- m = 4096
- covariate rank = 4
- block-vector width = 8

Numerical checks:

- streamed Gram relative error: 2.857e-16
- 2D tiled Gram relative error: 2.933e-16
- maximum exact light-cone leakage outside distance k: 0.000e+00

All matrix identities are tested against explicitly formed reference matrices.

The memory table is an algebraic working-set model. It excludes allocator,
CUDA library workspace, cache, and backing genotype storage.
