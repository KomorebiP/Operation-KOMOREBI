# Proof census through Paper V

Author: Komorebi P.  
Census date: 2026-09-06

The headline count is **1443 mapped Lean proof declarations after removing known shared names and copied Paper IV proofs**. There are additionally **319 distinct mapped constructions in Papers I–IV**. Definitions and generated namespace declarations are not silently counted as new proofs.

| Paper | Manuscript theorem-like records | Mapped theorem declarations | Other mapped constructions | Release |
|---|---:|---:|---:|---|
| I | 32 | 73 | 11 | Projector_Resolved_Seed_Calculus_I_v1.2.1 |
| II | 18 | 117 | 43 | Projector_Resolved_Seed_Calculus_II_v1.2.1 |
| III | 30 | 88 | 55 | Projector_Resolved_Seed_Calculus_III_v1.0.1 |
| IV | 68 | 953 | 211 | PRSC_IV_v1.0.0 |
| V | 20 | 225 | Not separately mapped | PRSC_V_v1.0.0_Scoped_Lean_Completion |

The raw per-paper theorem count is 1,456. Two theorem names are shared by Papers I and II. Eleven Paper V targets adapt the Paper IV cyclic-series foundation. Removing those known duplicates gives **1,443**. The remaining 1,454 distinct fully qualified theorem names include those 11 renamed copies.

The construction rows for I–IV sum to 320, with one shared construction, giving 319 distinct mapped constructions. Paper V defines further spaces, maps, algorithms, and projective quotients, but its 225-target contract counts theorem declarations only; those additional definitions are not included in 319.

The manuscript count is **168** theorem/lemma/proposition/corollary records: 32 + 18 + 30 + 68 + 20. This counts the printed results, not unique mathematical ideas: results reused or specialized between papers can occur more than once. Definitions, algorithm specifications, conjectures, examples, and imported classical facts are not included in this manuscript denominator. Contract rows (35, 25, 41, 151, 20) count different things and must not be added as if they were theorem records.

Paper V has 20 completed **scope-explicit formal counterparts**, with 225 checked targets. The original 133 remain included; 92 were added, comprising 81 additional supporting proof statements plus the 11 adapted foundation targets. Neither 225 nor 92 is a count of additional manuscript theorems.

## Evidence and limits

- Papers I–III: counted from the authoritative v1.2.1/v1.2.1/v1.0.1 maps and classified against their source declarations. Every mapped name was resolved. Their completed build and trust-audit status is recorded in the bundled FINAL_AUDIT_REPORT.md and component audit logs.
- Paper IV: counted from lean_contract_v1.0.0.json, with the 68-result register and completed scoped map. Its bundled audit records the build pass and permitted axioms.
- Paper V: actual pinned combined build and direct/namespace axiom audit were run in this session. verification/verification_status.json is the authoritative result.
- I–IV were **not freshly rebuilt during this census**. Their counts are newly reproduced; their earlier build status is release evidence.
- This is a declaration census with known-copy removal, not an algorithmic test of mathematical independence, novelty, or equivalence of every statement. Supporting lemmas, reformulations and special cases remain legitimate separate Lean declarations.

## Known overlap

- construction `Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates` appears in Papers I and II.
- theorem `Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis` appears in Papers I and II.
- theorem `Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis` appears in Papers I and II.

The 11 adapted Paper IV proofs are individually listed in CUMULATIVE_COUNTS.json. Input-archive SHA256 digests and complete per-paper metrics are also recorded there.

Paper V v1.1.0 integrates the checked statements into the expanded full manuscript. It adds no Lean targets to the v1.0.0 census. The original numerical companion has now also been rerun.
