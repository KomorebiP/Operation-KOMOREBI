# Failure ledger — v0.29

## Runtime/frontend

An attempted interactive/streaming container invocation was rejected with `StreamingExecNotEnabledContainerError` before execution. Assembly and all compilation were run synchronously afterward. All seven runtime parts and their combined SHA-256 were checked. Runtime extraction returned exit code zero.

## Rejected development drafts

Failed drafts were not counted as proofs. The accepted sources were subsequently replayed from a fresh source/output tree.

- `ContinuousGaugeCoboundaries`: compiler return code `1`. Exact diagnostics: `development/logs/ContinuousGaugeCoboundaries.1789180730327694160.log`; source hash `388c747a990e5a5c8f02bc7773da5f417e2faf3a90bb333f61f6558a95cceed2`.
- `ContinuousLocalGaugeComplex`: compiler return code `1`. Exact diagnostics: `development/logs/ContinuousLocalGaugeComplex.1789180795087701632.log`; source hash `be1cb4759d24793629f45acc94646bc10527456891032ccff446217ee255ed52`.
- `KernelGaugeCorrection`: compiler return code `1`. Exact diagnostics: `development/logs/KernelGaugeCorrection.1789180880882798421.log`; source hash `9d0420827a57df841ec81497e9c604ec5701b5b4b3832f64d25f84a9d4079234`.
- `LocalGaugeExactSequence`: compiler return code `1`. Exact diagnostics: `development/logs/LocalGaugeExactSequence.1789181116589124112.log`; source hash `b436a7459cfee9ccba419ebc0415388e6caf304d98679e589ab3246416658b28`.
- `LocalGaugeInvariance`: compiler return code `1`. Exact diagnostics: `development/logs/LocalGaugeInvariance.1789181200834068717.log`; source hash `820a4cfd1016f64caadeb0c638915c2222a75e98542f6cd053f44a0a06ecc1f3`.

The failures were two unused-section-variable warning failures, one quotient-normalization proof failure, one omitted argument in a submodule API call, and one semireducible pullback/type rewrite failure. All were corrected without weakening the theorem statements or disabling warnings.

## Verification interpretation

Batch limits deliberately stop with PARTIAL and are not treated as a completed PASS. A replay is accepted only after every source module and every named-constant axiom report have completed. Extracted-archive replay has its own result manifest.

## Mathematical boundaries retained

Absolute vanishing does not imply local-conjugacy vanishing. Strict obstruction zero implies gauge zero, but the converse is false. Both failures of converse implications are witnessed by checked examples. They are not counterexamples to Strong Artin.
