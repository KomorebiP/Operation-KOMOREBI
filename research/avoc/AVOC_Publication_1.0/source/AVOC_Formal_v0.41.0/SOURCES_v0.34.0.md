# AVOC v0.34.0 source provenance

Baseline: frozen `AVOC_Formal_v0.33.0.zip`.

New proof modules:

- `AVOC/AffineTerminal.lean`
- `AVOC/MultiLevelOperational.lean`
- `AVOC/AffineTerminalCodec.lean`
- `AVOC/CertifiedOperationalCatalogue.lean`
- `AVOC/OperationalExamples.lean`

New runtime/test sources:

- `tools/AffineTerminalMain.lean`
- `tools/execute_multi_level.py`
- `checks/test_operational_bridge.py`
- `checks/test_operational_policy.py`

All inherited non-audit AVOC modules are required to remain byte-identical to the baseline in the final collector.
