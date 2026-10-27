# Publication v1.14.0 integration audit

**Primary verdict: proved as written**, within the integration scope below. All 24 in-scope obligations passed. No mathematical mismatch, overbroad coverage claim or unresolved source defect remains. This is not a fresh verdict on every unchanged theorem or a final PDF/archive verification.

The publication accurately marks all sixteen principal groups as having formal counterparts, while retaining limits for explanations, illustrations, background proof routes and unnamed written specializations. The new guide matches the actual infinite Hilbert model, full real-budget limit and exact rounded noisy schedule.

| Verified quantity | Result |
|---|---|
| Production modules / import roots | 160 / 4 |
| Preserved Lean proof-source/import files | 164, including all 156 parent files |
| Explicit theorem/lemma declarations | 1,846 = 1,693 + 153 |
| Exported declarations | 5,321 = 5,048 + 273; no overlap |
| Selected map entries | 109; 69 unchanged + 40 added |
| Added guide API references | 21, all resolved |
| Formalized principal groups | WR01–WR16, all 16 |
| Preserved chapter mathematical environments | 192 across 29 files |
| Changed TeX reviewed | 22 hunks in 12 files, including late typesetting refinements |

All 164 Lean files were compared byte-for-byte with accepted sources. The inherited 156 were also compared directly with the immutable parent ZIP and original audit receipt hashes. Both raw inventories contain only permitted recursive axioms and no unsafe/project-axiom declarations. These retained audits are not relabeled as a freshly executed combined audit.

**Obligation matrix**

| ID | Obligation | Result and evidence |
|---|---|---|
| I01 | Archive identities | Passed. Directly hashed immutable parent publication and exact accepted diagonal evidence archive. |
| I02 | Inherited Lean preservation | Passed. 153 production modules and three original import roots are byte-identical to the immutable parent ZIP. |
| I03 | Final Lean preservation | Passed. All 164 production/import Lean files equal accepted diagonal_evidence/lean bytes. |
| I04 | Module/root count | Passed. Independent path inventory gives 160 production modules and four roots. |
| I05 | Printed mathematics preservation | Passed. All 192 mathematical environments across 29 chapter files, and every chapter label, are byte-identical. Manual diff review covers changed prose outside those environments. |
| I06 | Changed-hunk scope | Passed. All 22 final hunks in 12 TeX files were read, including the two late typesetting refinements. |
| I07 | Explicit declaration count | Passed. Independent lexical recount under the stated predecessor convention: 1,846 = 1,693 + 153. |
| I08 | Parent inventory binding | Passed. Raw historical receipt binds all 156 current inherited source hashes to the 5,048-declaration audit. |
| I09 | Diagonal inventory and union | Passed. 273 unique added names; raw log equals inventory, module hashes match, and no name overlaps the parent. Union count is 5,321. |
| I10 | Axiom/safety scope | Passed. Every retained inventory row has allowed recursive axioms and no unsafe/project-axiom declaration. This does not claim a fresh combined audit. |
| I11 | Sixteen group statuses | Passed. Exactly WR01 through WR16 are Verified. Only WR10, WR11 and WR12 change status; the other thirteen statuses/sources are inherited. |
| I12 | Coverage is bounded | Passed. New prose explicitly limits coverage to stated results, retaining written backgrounds, illustrations, alternative proof routes, unit-vector/nonclosed-range examples and unnamed specializations. |
| I13 | Proposition 30.1 correspondence | Passed. Raw final types match actual infinite lp, n=j+1, exact range-K prefix, universal correction/global uniqueness, infinite norm identities, all four estimates and both nonnegative tails. Series-only versus full interfaces are distinguished. |
| I14 | Theorem 30.2 correspondence | Passed. Raw final theorem has M explicitly Real atTop, two pi/4 scalar limits, full budget limit and actual hard-prefix limit 1. Guide correctly describes sqrt(A(n+1)) and the mesh-transfer hypotheses. |
| I15 | Corollary 30.3 correspondence | Passed. Actual datum/bias, arbitrary s:H with //s-b//<=delta, 0<delta<=1, literal natural ceiling of real power, and both inequalities match. No bias hypothesis remains in the final corollary. |
| I16 | Inexact specialization scope | Passed. The revised appendix correctly calls it a written consequence. Adding epsilon/alpha to the formalized noisy bound and using epsilon<=kappa*alpha*delta^(1/3) gives the printed sqrt(2)+1+kappa constant. |
| I17 | Theorem map | Passed. All 109 unique entries match file hash, exact declaration line, module and accepted exported name. 69 inherited entries unchanged; 40 added. |
| I18 | New guide APIs/snippets | Passed. All 21 added API references occur in inventory and map; import and inspection snippets refer to actual final names. |
| I19 | Control histories | Passed. Parent 44 controls (14/28/2) and diagonal eight (2/5/1) remain separate. No fresh 52-control or parent-control replay is claimed. |
| I20 | Integrated build | Passed. Raw root-run log records both default entrypoints and successful completion of 3,820 jobs. Prose separates this compilation from retained declaration/control audits. |
| I21 | Change-history correction | Passed. Two intermediate no-fresh-rebuild replacements are explicitly superseded and contain exact final replacement text matching frozen manuscript. No source mathematics changed. |
| I22 | Table-spacing refinement | Passed. One group-local arraystretch=1.0 line only; removing it restores the previously reviewed map hash exactly. No row or mathematical text changed. |
| I23 | Inline-code spacing refinement | Passed. One leanexpr macro and 17 wrapper substitutions only; removing/reverting them restores the previously reviewed guide hash exactly. Expression arguments unchanged; existing code macro uses texttt/detokenize. |
| I24 | README/configuration/edition scope | Passed. Read main and verification READMEs, lean README/USAGE, lakefile, stats and preamble. Counts, pins, two defaults and accepted evidence paths agree; final PDF/metadata/archive work remains downstream. |

**Critical statement correspondence**

Proposition 30.1 correctly combines `proposition_30_1`, `a_unique_minimizer` and coordinate definitions. The scalar-series theorem alone is not presented as the optimizer theorem. Prefix `K` contains exactly printed indices 1 through K.

Theorem 30.2 has `M : Real` tending to infinity. The positive mesh `sqrt(A(n+1))` is an internal transfer device; the final conclusion is over all real budgets. The guide correctly states the mesh and profile hypotheses and explains the alternative decreasing-kernel proof route.

Corollary 30.3 uses actual `b`, `w` and `c`, arbitrary `s:H` under the norm bound, `0 < delta <= 1`, and literal `Nat.ceil(delta^(-2/3))` with real powers. Bias is proved within the model, and both bounds and constants match.

The inexact diagonal specialization is accurately described as a written consequence: add `epsilon/alpha` to the formalized noisy bound and use `epsilon <= kappa*alpha*delta^(1/3)` to obtain the constant `sqrt(2)+1+kappa`. No separately named specialized Lean declaration is claimed.

**Resolved record issue and late typesetting refinements**

Two intermediate no-fresh-build replacements in the editorial history are now explicitly superseded with final text matching the manuscript. The corrected record SHA is `39815214a15fc8e569483636f52bdde692e69583b241331f6c1b38dc20a76d22`. No source mathematics changed.

The map adds only a group-local `arraystretch=1.0` command; deleting it exactly recovers the earlier reviewed bytes. The guide adds one `leanexpr` macro and changes 17 wrappers without changing their arguments; reversing those operations exactly recovers the earlier guide bytes. The existing `code` macro uses `texttt/detokenize`, preserving intended spaces. Their PDF appearance remains root visual QA.

**Scope limitations and downstream work**

- This audit covers the exact integration changes and their source/statement match, not a fresh proof audit of every unchanged theorem or all sixteen groups.
- The thirteen inherited groups preserve their parent scope and source identities. The three new statuses were matched against raw accepted diagonal types and source-bound evidence; broad proof refereeing was not repeated.
- No Lean build, control replay, literature search, PDF compilation or rendering was run by this reviewer. The integrated build is root-run evidence inspected here.
- The 5,321 count is a disjoint union of two source-bound accepted inventories, not a freshly executed combined axiom audit or a count of distinct mathematical discoveries.
- Final PDF integrity/visual QA, refreshed EDITION_VERIFICATION and PDF-review records, archive manifests/CRC/safe paths and saved delivery bytes are downstream checks. The inherited current EDITION_VERIFICATION was not evidence for v1.14.0 counts.
- Compiler/kernel, the three allowed axioms and pinned compiled dependencies remain the trust boundary.
- Both final typesetting refinements are audited at source level; their visual success remains root PDF QA.
- Only the two owned review files were written. Later changes to hashed sources, guide, scope prose or map require a review update.

**Frozen changed TeX hashes**

| File | SHA-256 |
|---|---|
| `source/Komorebi_Space_Lean_Guide.tex` | `8cea2122aca9ff40aff7004bf2554a125ec60120d51eecc1b48a76407a8f1d49` |
| `source/Komorebi_Space_Monograph.tex` | `44606ab64c56ef3179ffb46d74e653a97b7f0dba8c7378511a0220424464a57f` |
| `source/Komorebi_Space_Visual_Guide.tex` | `fbadb2dc4405da14e5e3d2481b5dc1deedac8a266188ecd5b5e87e670b33ff38` |
| `source/chapters/05_geometry.tex` | `0ba4db5639a705111006d7e86524f3a207943c8fdd7af8c0bea40b90bd701334` |
| `source/chapters/05f_bounded_realization.tex` | `4743a765858edb9906f912fce931c19decab352d26a908d7b09f959e104c7969` |
| `source/chapters/05j_inexact_certificates.tex` | `fed4cc77878ba3bd2d77626ffdc3b312077dc2435562645f74fff2bf49a39738` |
| `source/chapters/06_boundaries.tex` | `65b0daea49db85df058a17e21f5c275b230a486b8bf3a1dbfd32971e28a74b16` |
| `source/chapters/10_hypothesis_atlas.tex` | `b1be0d02a249c4af8d8967847758b1336b4bc8ef263630cea9612eda808dae75` |
| `source/chapters/11_written_extensions.tex` | `b7c71c1f5e02c5d33779456e84300e53a7282c7717da6b6151d402a1883f14cd` |
| `source/edition_stats.tex` | `fe751f1de83810200011dc25f167a8a337e644e8948c2fd46f1bf62ff62dcad8` |
| `source/lean_guide_map.tex` | `0bddd040800132f8cff1a7f1f18f276fd5cc4b0cedf0738896d25aed93900e65` |
| `source/preamble.tex` | `24253ba7756295227d95b8d9606a1d33d2c3372bbfe3ef2289c2e1d707b8fd5d` |

The JSON counterpart records exact diff hunks, all 164 Lean hashes, every map-entry check, raw inventory provenance and the full obligation matrix.
