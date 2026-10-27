# Komorebi transfer map for Block 47

This records the selected source material actually inspected. It is not an
assertion that every Komorebi manuscript or theorem was exhaustively audited.
The source copies are included in `toolkit/`; package hashes identify their
exact bytes. No source theorem becomes an arithmetic input by analogy alone.

| Source capability | Actual transfer | Boundary retained |
|---|---|---|
| Block15 coefficient sections and polyphase reconstruction | Exact seven-section equations for the actual hypergeometric period; coefficient selection for the sextic cube | Exact reconstruction preserves information, but cannot create an arithmetic contradiction |
| Block15 fold kernels, selectors and split lanes | Fixed candidate labels, joint trace relations, finite exclusion interface | Norms, supports and minimal polynomials can lose information; selector hypotheses must be supplied |
| Factorial lanes and p-adic unit normalization | Tested on the actual period recurrence | Transfer fails for the raw series because c1=-16/315 is not 7-integral; no automatic unit-tail theorem |
| Stratification and refinement | Complete squarefree-coefficient local solvability criterion; Cartier ordinary versus 7-rank-zero strata | Primitive Z_p points at all places do not give a primitive global solution |
| SRIC exact repair descent | Used to identify the missing global compatibility obligation | Its sheaf/torsor and effective-descent hypotheses are not established for these integer solutions; it supplies no automatic local-to-global gluing |
| Local/global reuse inventory | Guided checks of unramified base change, inertia and Frobenius conventions | Inventory entries are source pointers, not imported formal theorems |
| Exact finite certificates | 12 Lean interface/correlation theorems and 9 actual mod-seven polynomial/matrix theorems | Modular attachment, exhaustive arithmetic coverage, geometric interpretations and nonexistence remain outside the formalization |

The central improvement is to retain one global label or character when
combining local information. In the modular route this means one form,
one prime above seven and a consistent embedding. In the reciprocity route
it means the same residual character at two and seven. Allowing a different
compatible label at each prime changes the quantifiers and weakens the test.

## Source identities

- `block15_section.tex`: selected Library file
  `libfile_bb8607160a2c81919908b67d0756e158`, version 2.
- `From_Factorial_Lanes_to_Padic_Transfer.tex`: selected file
  `libfile_bd36a038214481918e2dbfdcf9432dab`.
- `Stratified_Recursive_Improvement_Closure_v2.4_Block23_Final.tex`:
  selected file `libfile_c3dc2dea60948191861b0e7762aa692e`.
- `KOMOREBI_LOCAL_GLOBAL_REUSE_AUDIT_2026-09-15.md`: selected file
  `libfile_4aa3684a73f8819193664f4fc2591be1`.

These are internal provenance identifiers. Selection does not assert that
an uninspected later revision does not exist. No whole-toolkit novelty claim
or formal dependency on an unimported module is made.
