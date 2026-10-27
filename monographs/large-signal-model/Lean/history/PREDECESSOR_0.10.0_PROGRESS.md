# Large Signal Model Lean — persistent progress ledger

**Current: 0.10.0 · Frozen theory: 1.0.0 · 36 complete / 87 · 51 outstanding.**

| Block | New numbered mappings | Cumulative complete | Remaining |
|---|---|---:|---:|
| 0.1.0 | P1, P2, P4, P5, P6, P7, P10 and P22; P3 was partial | 8 | 78 unformalized and 1 partial |
| 0.2.0 | P3 and P8 | 10 | 77 |
| 0.3.0 | P9 and P12 | 12 | 75 |
| 0.4.0 | P26 and P36 | 14 | 73 |
| 0.5.0 | P27, P28 and P30 | 17 | 70 |
| 0.6.0 | P29 and P38–P41 | 22 | 65 |
| 0.7.0 | P42–P44 | 25 | 62 |
| 0.8.0 | P13 and P18–P21 | 30 | 57 |
| 0.9.0 | P14–P17 and P25 | 35 | 52 |
| 0.10.0 | P45 rational finite-certificate search | 36 | 51 |

Block 10 proves rational feasibility by weak Fourier–Motzkin elimination, derives rational lift/initial/right-inverse witnesses, implements exhaustive natural-code search with exact checking, and connects accepted witnesses to P39's cone and all-word probability guarantees. Four modules add 30 named theorems, including eight examples; four new negative controls bring the total to 72.

Coverage is not difficulty weighted. All 74 predecessor proof files, 1,256 declaration records and 68 rejection-control sources remain unchanged. Source guides, histories, the frozen manuscript and the complete predecessor archive are retained. The executable search uses no hidden-state generator or supplied certificate as an input. Its completeness proof assumes that a rational-generator certificate exists.

Verification is recorded in `verification/block10_release_run/report.json`, with exact-archive verification supplied externally. Do not infer a successful run merely from this descriptive ledger. The progress JSON is finalized from the actual accepted report. Failed compiler attempts and source snapshots remain under `verification/development_block10/`; the prohibited-word preflight failure is separately preserved.

The roadmap's stale standalone remaining-count field was repaired, and an extra gate now compares it with the exhaustive list. Publication metadata is clarified by `PUBLICATION_STATUS.md`, without changing the frozen documents.

## Next restart

P32–P34: read the exact frozen linear-identification and stability statements and register proofs before selecting the next block. All 51 remaining propositions appear exactly once in `ROADMAP_1.0.json`. Do not jump from this semidecision result to a practical optimizer, complexity bound, universal rational-certificate existence, or completion of the curved-certificate track.

No production PR-LASM changes, training, empirical confidence tests, independent referee, second prover, full upstream rebuild or external publication was performed.

Accepted source run: PASS, all 231 stages; metadata PASS, 76 checks. Development records preserve 11 successful and 25 failed compiler invocations. The separate delivery report records the fresh-extraction outcome and archive identity.
