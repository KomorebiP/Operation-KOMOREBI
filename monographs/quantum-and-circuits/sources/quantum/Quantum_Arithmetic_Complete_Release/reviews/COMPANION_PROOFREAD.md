# Conservative mathematical proofreading: companion documents

Checked 2026-10-07 UTC. Review-only mode using the `mathbox:proofread-math` workflow. No companion source file was edited.

## Scope and frozen revisions

- `visual/Quantum_Arithmetic_Visual_Body.tex`: all 263 physical source lines and all 25 visual sections. SHA-256 `633c61bde1f2629ea872e8424ffdbb3cb85e0a7fcaafef3a0f176861de07fd37`.
- `lean/Quantum_Arithmetic_Lean_Guide_Body.tex`: all 939 physical source lines, including every literal source block, the manuscript concordance, trust boundary, and complete active theorem inventory. SHA-256 `b5141ae9880dd7841e254393bb6b7608238e6fddc42d0f38362fa8330023cf76`.
- Nearby definitions and macros: `preamble.tex`; relevant preserved Lean source ranges; archived final report; current source reconciliation; current fresh-Lean status; visualization result record.

## Findings

No objective mathematical typo, meaning-changing grammatical error, inconsistent Fourier convention, or LaTeX environment error was found in the reviewed bodies. No correction is required by this review.

Routine edits: none.

Mathematical-token changes: none.

Unresolved mathematical issues found within this proofreading scope: none. This is local consistency and source-concordance proofreading, not a new referee audit or kernel verification.

## Exact fixed-example consistency

The twelve-entry signed vector, its absolute-value vector, chosen complementary component, and input agree across the companion prose, displayed formulas, preserved Lean definitions, and current exact-result record. In particular:

- Signed signal: `(4,0,2,0,-2,0,-4,0,-2,0,2,0)`.
- Input: `(9,2,1,2,3,2,-5,2,3,2,1,2)`.
- Squared energies: retained 48, complementary 102, full input 150.
- Selected normalized-input probability: `8/25`; complementary probability: `17/25`.
- Unnormalized negative-sign DFT of the signed signal: 12 on `{1,5,7,11}`, zero elsewhere.
- DFT of the unsigned signal: `(16,0,4,0,4,0,16,0,4,0,4,0)`.
- Transformed unsigned-state probabilities: `4/9` at 0 and 6, `1/36` at 2, 4, 8, and 10, zero elsewhere. Their sum is one.
- Shell dimensions in divisor order `(1,2,3,4,6,12)`: `(1,1,2,2,2,4)`.
- Occupied shell energies: 48 in order one, 54 in order four, 48 in order twelve.
- The three polyphase lanes match the stated addresses and input values.

The positive-sign normalized Fourier matrix, negative-sign analysis matrix, and negative-sign unnormalized DFT are consistently distinguished. The common ambient divisor-projector denominator is twelve. The state scales `1/sqrt(48)` and `1/sqrt(12)` match the exact coordinate scales `sqrt(3)/12` and `sqrt(3)/6`.

The continuous relative-phase formula, its endpoint states, selected probability `sin²(theta/2)`, and sample-six amplitude `exp(i theta)/sqrt(3)` are locally consistent. The text correctly separates the new continuous illustration from inherited endpoint formal coverage. The repeated quarter-turn endpoint at `2*pi` is the same phase as zero, so it does not require an additional unique-phase assertion.

## Formal freshness and counts

The guide's module counts total 96 and match `SOURCE_RECONCILIATION.json` and the later archived final report: 22, 17, 30, 17, and 10. The earlier overlapping 59-theorem revision is not added to that total.

The prose consistently preserves the archived-check versus current-replay boundary. `FRESH_LEAN_STATUS.json` says `NOT_RUN`, with three HTTP 502 runtime-materialization failures and no compiler process. The visual body makes no fresh Lean-pass claim. The Lean body gives the same failure cause and identifies the inherited proof receipt rather than manufacturing a new one.

The control discussion is appropriately narrower than “three false propositions refuted”: it discloses the opaque `Decidable` reduction failure for the false-mode control and separates that rejected attempt from the positive correct-value theorem. The stated axiom union and kernel-replay trust boundary match the archived report.

## Validation and limits

- Both body files' `begin`/`end` environment stacks were checked and are balanced.
- All 20 distinct visual figure references resolve to existing PDF assets.
- All 15 literal Lean excerpts match the exact stated physical source-line ranges in `lean/checked_checkpoint`.
- The exact-result data and current freshness record were read and compared with the companion statements.
- No Lean compiler was run by this proofreading review.
- No PDF compilation or rendered-page inspection was performed by this review. The release coordinator's separate publication QA supplies that check.
- The final traditional body was not present under the requested conventional filename when searched. Therefore the QA01–QA18 row descriptions were read for internal consistency, but this review does not claim a final cross-document label check against the traditional paper. That remains a release-level consistency check.

Any subsequent edit to a reviewed body changes the frozen scope above and should be checked proportionately.
