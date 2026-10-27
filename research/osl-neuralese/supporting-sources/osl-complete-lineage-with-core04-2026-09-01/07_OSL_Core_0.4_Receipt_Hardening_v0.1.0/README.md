# OSL-Core 0.4 Receipt Hardening v0.1.0

This is the next executable OSL development block. It does **not** replace or
rewrite the frozen Operator Symbolic AI Language v0.5 / OSL-Core 0.3 release.
It keeps that source grammar and its 42-accept / 24-reject corpus outcome while
hardening evidence production and verification.

## What changed

- every attempt begins with an exact-source `program_open` receipt;
- parse and static failures now end in auditable rejection terminals;
- exactly one terminal is required and it must be last;
- every executed source statement owns a global, contiguous effect span;
- terminal receipts bind the source, AST, counts, phase, and semantic state;
- default and explicit capabilities share a replayable grant ledger;
- revoke, expiry, finite-use decrement, duplicate execution, and duplicate
  feedback are checked;
- packet constructors, proof resources, memories, and protected actions are
  reconstructed by a fail-closed dictionary verifier, with exact same-runtime
  replay reported separately for delegated interpreter semantics;
- quarantine/rejected/provisional packets cannot be laundered through inference
  or communication;
- rollback restores private secrets and protected kernel tables without erasing
  append-only evidence;
- malformed numeric literals become explicit parse rejections rather than raw
  Python exceptions.

## Verified release facts

| Gate | Result |
|---|---:|
| Frozen source corpus | 66/66 |
| Accepted / rejected | 42 / 24 |
| Native v2 receipts | 1,825 |
| Independent protected-state/lifecycle traces | 66/66 |
| Supplementary exact runtime replays | 66/66 |
| Discovery Bridge programs | 3/3 (71 receipts) |
| Fixed adversarial witnesses | 24/24 |
| Tests | 93/93 |

Start with [CORE04_RECEIPT_SPEC.md](CORE04_RECEIPT_SPEC.md),
[PROVENANCE_AND_PROOF_RULES.md](PROVENANCE_AND_PROOF_RULES.md), and
[CLAIM_BOUNDARY.md](CLAIM_BOUNDARY.md). The complete native traces are in
`CORE04_TRACE_BUNDLE.jsonl`, and the bridge gate is recorded in
`CORE04_DISCOVERY_BRIDGE_REPORT.json`; frozen Core 0.3 reports are under
`legacy/v03_evidence/`.

## Offline verification

PowerShell one-liner:

```powershell
python -m pip install -r requirements.txt; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; .\verify_core04.ps1
```

Bash:

```bash
python -m pip install -r requirements.txt
./verify_core04.sh
```

Successful verification requires no network after dependencies are installed.
