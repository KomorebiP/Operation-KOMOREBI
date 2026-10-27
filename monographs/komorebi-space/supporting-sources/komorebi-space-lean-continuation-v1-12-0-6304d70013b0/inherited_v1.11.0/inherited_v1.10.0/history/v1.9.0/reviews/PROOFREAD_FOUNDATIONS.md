# Foundations proofreading report

Date: 2026-10-12. Edition reviewed and edited: `monograph_v1.9.0`.

## Scope and result

The mathematical-proofreading skill was applied in edit mode to the complete contents of all six assigned source files. Every paragraph, display, proof, example, caption argument, local source callout, and local cross-reference was read. Shared definitions and macros in `source/preamble.tex` were inspected. The existing project voice, notation, theorem statements, labels, and diagram inputs were retained.

Seven correction groups were made across four files. Two files needed no changes. Five corrections concern precise mathematical wording or the placement of an already present exceptional case. Two are grammar corrections. No proof was replaced, no new theorem was introduced, and no hypothesis was silently weakened. The original formal source files were read but not modified.

This was a full proofreading pass over the assigned files, with focused source checks for the three issues described below. It was not a fresh theorem-by-theorem Lean compilation or an independent referee audit of every claim in these chapters. No new formal verification is claimed.

## Coverage by file

| File under `source/chapters/` | Entire file read | Original words | Final words | Changes | Unresolved issues from this pass |
|---|---:|---:|---:|---|---|
| `01_views.tex` | Yes, 179 lines | 1,771 | 1,771 | Variance description and one grammar correction | None |
| `02_obstructions.tex` | Yes, 214 lines | 1,843 | 1,844 | Quotient classes identified precisely | None |
| `02a_prescription.tex` | Yes, 115 lines | 1,256 | 1,256 | None | None |
| `03_towers.tex` | Yes, 488 lines | 3,571 | 3,573 | Explicit real scalar example and zero-bound proof branch | None |
| `03a_observation.tex` | Yes, 195 lines | 2,174 | 2,174 | None | None |
| `03b_repair_transport.tex` | Yes, 192 lines | 1,833 | 1,836 | One grammar correction and explicit linearity | None |
| **Total** | **1,383 lines** | **12,448** | **12,454** | **Seven correction groups** | **None identified within proofreading scope** |

Word counts use whitespace-separated source tokens, including mathematical source. They are a coverage measure rather than a reader-facing prose word count. The subordinate observation and transport files are included in `03_towers.tex` by LaTeX, but their contents are counted separately once in the table.

## Exact edits

### 1. Variance terminology in `01_views.tex`, line 11

Before:

> Equivalently, it is a contravariant functor \(F:\V^{\mathrm{op}}\to\Set\).

After:

> Equivalently, it is a functor \(F:\V^{\mathrm{op}}\to\Set\).

The opposite category already encodes the contravariant direction relative to the original category. The immediately preceding definition sends an arrow \(v\to w\) to a restriction \(F_w\to F_v\). The correction removes a double variance description while preserving the displayed domain, codomain, maps, and functor laws. It does not change the defined view system.

### 2. Grammar in `01_views.tex`, line 172

Changed “a two element set” to “a set with two elements.” This corrects the noun phrase without introducing an extra hyphen or changing KS07's example.

### 3. Quotient-class wording in `02_obstructions.tex`, line 68

Changed “Thus the two quotients agree” to “Thus the two quotient classes agree.”

The proof compares the two classes \([\delta\widetilde s]\) and \([\delta\widetilde s']\) in one fixed quotient group. It does not compare two quotient groups. No quotient definition or formula was changed.

### 4. Coefficient domain in `03_towers.tex`, line 289, source callout KS23

Changed “For constant identity towers” to “For constant real scalar identity towers.”

This makes the coefficient restriction of the cited formal example explicit. The preceding worked example uses real vector spaces, and the frozen cited theorem fixes a real scalar tower. The argument that the primitive grows as \(f_0+n\) and is unbounded is not presented as a statement over every complete nontrivially normed field. The displayed formula and the specific real example are unchanged.

### 5. Exceptional-case placement in `03_towers.tex`, lines 399–404, proof of KS27

Previously the proof multiplied a strict approximation inequality by K before mentioning the K = 0 case. The displayed strict inequality is valid for K > 0 and would read a false strict zero inequality when K = 0. The text already supplied the zero case immediately after that display.

That existing case is now handled first:

> If \(K=0\), the common operator bound gives \(\norm{Q_Nx}=0\) for every \(N\), so convergence is immediate. Suppose \(K>0\).

The approximation and the existing displayed inequality follow under this explicit positive branch. The original trailing zero-case sentence was removed because its argument is now placed before the step that requires positivity. No inequality sign or theorem hypothesis was changed, and the zero-dimensional possibility remains covered. The conclusion of KS27 is unchanged.

### 6. Grammar in `03b_repair_transport.tex`, line 5

Changed “Let \(d:E\to R\) be continuous linear between normed spaces” to “Let \(d:E\to R\) be a continuous linear map between normed spaces.” This supplies the missing article and noun while retaining the original linearity and continuity assumptions.

### 7. Map type in `03b_repair_transport.tex`, line 45, setup of KS66

Changed “A compatible change consists of bounded maps” to “A compatible change consists of bounded linear maps.”

The proof uses additivity and scalar linearity of the candidate and residual transformations. The source record explicitly declares both transformations as continuous linear maps. The insertion makes the source's actual hypothesis explicit in the prose. It is not a claim that the formulas hold for arbitrary bounded nonlinear maps. No equation or conclusion was changed.

## Mathematical-token and meaning changes

The precise mathematical changes are the five wording/branch clarifications in items 1, 3, 4, 5, and 7 above. In particular, the real coefficient restriction and linearity condition are recorded explicitly rather than treated as invisible copyedits. The additional local formulas in item 5 state the already justified zero case and restrict the following proof branch to K > 0.

No operator, sign, numerical coefficient, exponent, quantified conclusion, theorem label, or displayed theorem equation was changed. All 31 `theorem`, `proposition`, `lemma`, and `corollary` statement blocks in the six files are byte-identical to the inherited v1.7.0 versions. This check excludes their following proof environments and does not hide the surrounding-hypothesis clarifications listed above. Examples and definitions were reviewed separately, with the changes to the view-system definition and KS23 example disclosed here.

## Focused source and proof checks

The proof-audit skill was applied in read-only self-review mode to the local mathematical issues before editing. The parent approved the source-confirmed corrections. These checks are separate from a fresh Lean replay.

### KS66: linear presentation changes

**Normalized claim.** For continuous linear defect maps d and D, continuous linear transformations S and C with DS = Cd, and continuous linear right inverses A and B, the chart formula and repair mismatch are

\[
\chi_BS\chi_A^{-1}(u,r)=(Su+(SA-BC)r,Cr),\qquad
P_BSx-SP_Ax=(SA-BC)dx.
\]

**Verdict for the pre-edit phrase “bounded maps”: correct only after a stated restriction.** The required restriction is linearity, already part of the actual cited formal source. The local prose now states it.

The decisive source is `formal/KomorebiSpace/ResidualNaturality.lean`, structure `DefectMap`, lines 26–29: both `candidate` and `residual` have continuous-linear-map types. The exact repair identity is `repair_change` at line 77, and the chart identity is `chart_formula` at line 123. The proof explicitly invokes preservation of addition or subtraction. The operator-norm and limit claims use the same typed record. Thus the clarification propagates through the complete KS66 setup without changing the formal source.

Dependency check: typed continuous linear maps → commuting defect square and section equations → linear expansion → chart and repair identities. The map type, commuting square, and section equations were checked against the raw source. No external theorem leaf was introduced.

### KS23: a bounded residual without a bounded primitive

**Normalized claim.** On the real scalar identity tower, the constant identity residual has no bounded operator-family primitive.

**Verdict: proved as written with the explicit real scalar domain.** This is the domain used by the cited source and the corrected prose. No claim about arbitrary non-Archimedean or positive-characteristic fields is made.

The decisive source is `formal/KomorebiSpace/IdentityTowerObstruction.lean`: `realTower` is declared over ℝ at line 20, `primitive_growth` at line 43 evaluates the candidate operators at 1 and derives growth by the natural-number index, and `no_bounded_primitive` at line 55 contradicts the real norm bound. The counterexample's scope and its contrast with exact repair of bounded candidates are preserved.

Dependency check: real identity tower → adjacent primitive equation → real growth formula → Archimedean unboundedness → no bounded primitive. The coefficient and primitive definitions and the local proof were read. No new computation or external source was needed.

### KS27: the zero operator bound

**Normalized claim.** If the nested remainder projections have a finite uniform norm bound, the norm-recoverable vectors are exactly the closure of the finite core, including the case of a zero bound.

**Verdict: proved as written after explicit separation of the already supplied zero case.** The theorem statement was not restricted to positive bounds. Both nonnegative branches remain covered.

The source is `formal/KomorebiSpace/CascadeDensity.lean`. `recoverable_of_mem_closure` at line 51 assumes K ≥ 0 and proves the estimate using a strictly positive factor K+1. `recoverable_iff_closure_finiteCore` at line 75 supplies the exact conclusion. In the written proof, the zero case follows from 0 ≤ ‖Q_Nx‖ ≤ K‖x‖ = 0. In the remaining K > 0 branch, multiplying the strict approximation inequality by K is valid. The inherited proof already contained both ideas, and only their local ordering was corrected.

Dependency check: nested projection identity → increasing kernels → finite-core approximants; uniform bound plus closure approximation → vanishing remainder. The finite-core and remainder definitions and both zero and positive scalar-bound cases were checked.

### Source hashes for those checks

All paths in this table are under `work/Komorebi_Space_Monograph_v1.7.0/formal/KomorebiSpace/`.

| Source | SHA-256 |
|---|---|
| `ResidualNaturality.lean` | `accf1d105c612e673fcd508847d023f56d7939490a5416202873d7bde803b8e8` |
| `IdentityTowerObstruction.lean` | `026f9504c3c355070d0c813ae16d51fee27e97ecaafbbcc525db8c9cbe864819` |
| `CascadeDensity.lean` | `11d90a5995354d99c60e9fac6e78ece9b81a1adc86b3a9e1861ae432eb5c8725` |

## Validation and limits

- Read all six files in full. An initially truncated tool display of part of the KS63 proof was followed by a targeted untruncated read, covering the missing text before editing.
- Re-read all seven changed passages in context after editing and inspected the full source diff against the inherited v1.7.0 files. That comparison contained only the edits listed here.
- Checked every `ref` and `eqref` target in the assigned files against the current source labels. No unresolved target was found.
- Checked every `source{KS...}` callout in the assigned files against the current concordance anchors. No missing anchor was found.
- Compared all 31 principal theorem/proposition/lemma/corollary statement blocks with the inherited source. All remained unchanged.
- No standalone LaTeX build or fresh Lean build was run by this proofreading subtask. The parent task owns the complete synchronized document build and visual QA. Layout quality must be assessed on that rendered edition.

No substantive unresolved issue was identified within the assigned proofreading scope. This statement does not promote every written claim to formal coverage, assert exhaustive proof correctness, or replace the existing evidence boundaries.

## Reviewed file identity

These are the source hashes after the seven corrections and before any later coordinated layout edits.

| File | SHA-256 |
|---|---|
| `01_views.tex` | `5fc06575fd78316dbf0865f5895582c0fc8b8894f378881dd413b3e885d74a8c` |
| `02_obstructions.tex` | `6b837a0a7c03a2f3bc6d1c82ca3e7c63ef25a0f9d7bb81e7482b07a791abaa88` |
| `02a_prescription.tex` | `f4dbb208cb264a6aa0806e1841f2f95aff34484940b57e82fac9c86d1a42c7cd` |
| `03_towers.tex` | `f2c72fb3a176b5b111b31cc2e9a6cfb5df94ff8c85ec912a5d0d43f8356cd3e8` |
| `03a_observation.tex` | `d17f1b2b9a74703876ac5e78676dcfc96c31fd56673a681f842af77172a64943` |
| `03b_repair_transport.tex` | `5b90a3abbedd9271b79507b12295a229f1084bf7f23e8dd1d8216bfaa4a5d44a` |

The initial search for local `AGENTS.md` files returned no matches. No execution or edit failure occurred during this proofreading pass. The truncated output described above was corrected by rereading the omitted span and was not treated as completed coverage until that read succeeded.
