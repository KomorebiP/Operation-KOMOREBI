# OSL-Core 0.3 Example Catalog

The release contains **66 executable programs**. Files `01` through `42` are expected to execute successfully. Files `91` through `114` are expected to reject safely with the declared error substring. The suite also contains two paired public-projection audits over files `28`–`31`.

## Accepted programs

| File | Purpose |
|---|---|
| 01 | direct observation and observed memory |
| 02 | communicated evidence and planning |
| 03 | activation injection and quarantine |
| 04 | simulation provenance |
| 05 | projector certification and application |
| 06 | coordinate transport |
| 07 | semantic intertwiner check |
| 08 | fork lineage declarations |
| 09 | planner binding |
| 10 | inference provenance |
| 11 | foreign-memory preservation |
| 12 | action feedback receipt |
| 13 | forwarded shared-workspace content |
| 14 | reconstructed-memory type |
| 15 | tool-effect capability |
| 16 | proof-gated observed memory |
| 17 | composite proof-gated planning |
| 18 | bounded and expiring capability |
| 19 | feedback-deadline contract |
| 20 | transaction commit |
| 21 | manual transaction rollback |
| 22 | neural proposal admission |
| 23 | neural proposal rejection |
| 24 | two-agent session order |
| 25 | capability proof |
| 26 | always-on contract templates |
| 27 | communicated-memory ownership proof |
| 28–29 | safe paired metadata audit |
| 30–31 | deliberate secret-dependent metadata leak |
| 32 | two-use capability consumption |
| 33 | three-agent session protocol |
| 34 | explicit authorization proof |
| 35 | committed transactional memory write |
| 36 | larger static-check example |
| 37 | exactly-once linear planning proof |
| 38 | unused affine proof is permitted |
| 39 | graph-verified two-agent terminal session |
| 40 | explicit append-only receipt-chain verification |
| 41 | exactly-once linear autobiographical ownership proof |
| 42 | graph-verified three-agent terminal session |

## Expected safe rejections

| File | Rejection target |
|---|---|
| 91 | communicated content forged as direct observation |
| 92 | planning without endorsement or authorization proof |
| 93 | execution without effect capability |
| 94 | invalid projector |
| 95 | endorsement of quarantined packet |
| 96 | stale composite proof |
| 97 | session-order violation |
| 98 | missing feedback before contract deadline |
| 99 | incomplete neural-admission obligations |
| 100 | exhausted capability |
| 101 | expired capability |
| 102 | unknown proof caught statically |
| 103 | nested transaction |
| 104 | ownership proof without observation premise |
| 105 | endorsement before neural admission |
| 106 | proof used at the wrong authorization scope |
| 107 | automatic rollback after transaction failure |
| 108 | second use of a consumed linear planning proof |
| 109 | unconsumed linear proof at normal completion |
| 110 | second use of a consumed affine proof |
| 111 | reachable nonterminal session deadlock |
| 112 | terminal session state with outgoing transition |
| 113 | starting a terminal-declared session without verification |
| 114 | second use of a consumed linear ownership proof |

## Evidence layers

The catalog is checked in four ways:

1. declared source-level acceptance or rejection;
2. exact deterministic replay and source-statement boundary receipts;
3. independent receipt, proof, provenance, action, session, and transaction reconstruction;
4. focused regression tests and complete finite abstract-state certificates.

Run the complete evidence generator with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference \
  python reference/generate_v03_evidence.py
```

Run the unified certificate with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference \
  python reference/verify_osl_core_v03.py \
  --output V03_UNIFIED_VERIFICATION.json
```
