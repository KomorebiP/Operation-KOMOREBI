# Paper XI — Block 02 classical-input audit

Checkpoint: **P11-PUB-B02**. Prepared: 2026-10-10T16:36:21.290416+00:00.

Primary source: Bushnell and Kutzko, *The Admissible Dual of GL(N) via Compact Open Subgroups*, Annals of Mathematics Studies 129, Princeton University Press, 1993. The retained PDF and extracted text are pinned below. This is a selected statement-and-application audit, not a new proof of the book or a fresh Lean build.

| ID | Published statement | Printed / PDF pages | Use and exact boundary |
|---|---|---|---|
| BK-1410 | 1.4.10 | 38 / 50 | Minimal commutator exactness for rank-four field approximation. No wild integral bimodule splitting is inferred. |
| BK-227 | 2.2.6 and 2.2.7 | 55 / 67 | Literal perturbation refinement from a pure maximal derived field. Strict -2R > -n-q1. Final K is not identified with E[C]. |
| BK-317 | 3.1.7--3.1.10 | 90, 91, 92, 93, 94 / 102, 103, 104, 105, 106 | Actual recursive H/J groups and half-level thresholds. Floor and ceiling thresholds are not interchangeable. |
| BK-325 | 3.2.1--3.2.5 | 98, 99, 100 / 110, 111, 112 | Minimal characters and full shallow extension at maximal K. Intersection compatibility alone does not remove determinant and normalization conditions. |
| BK-332 | 3.3.2 | 105 / 117 | Full-character intertwining in the rank-two carrier. At full index zero and maximal minimal field: I_G(theta)=K^times J. |
| BK-3318 | 3.3.18 | 112, 113 / 124, 125 | Deep correction character Theta psi_delta. r<n; floor(r/2)<=m<=r-1, m=floor(r/2). |
| BK-341 | 3.4.1 | 114, 115, 116 / 126, 127, 128 | Actual nondegenerate simple-character commutator quotient. Alternating form is not a fixed native quadratic refinement. |
| BK-3614 | 3.6.13(ii) and 3.6.14 | 136, 137 / 148, 149 | Whole-character transfer preserves beta determinant. Normalized full indices are both zero. Scalar value is chi(u^p). |
| BK-622 | 6.2.2--6.2.3 | 203, 204 / 215, 216 | Actual extended maximal type yields same supercuspidal candidate. Compact type alone determines only the unramified-twist class. |
| BK-625 | 6.2.5 and following paragraph | 204, 205 / 216, 217 | Torsion number and complete principal order. This does not freshly audit all separate conductor formulas. |

## Source pins

### Odd explicit AS recursion, corestriction, native trace and field hypotheses
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_166/tower/TRACE_ZERO_AS_TOWER166.md`

SHA-256: `49a18fb733f0209b3e38118f5132839a060961edd0bdc0211e1f7b441a4e5653`. Size: 8,743 bytes.

### Earlier recursive parameter and profile proof; not confused with AS normalization
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_166/tower/RECURSIVE_TOWER166.md`

SHA-256: `6f39a077df18eb03f9fab2b6e426529dbe14cf4f7e1cfce95ddb0fcd187d7b33`. Size: 9,995 bytes.

### Whole-character transfer, correction and shallow extension
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_166/central/TRACE_ZERO_CHARACTER_INDUCTION166.md`

SHA-256: `99cb6e80c419e0bf7325e2b2b3fbaba1391903448a3b6a0c4cd9f3944ed406a1`. Size: 13,741 bytes.

### Leading layer and distinct source-defined arithmetic candidate route
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_166/capacity/LEADING_LAYER_CAPACITY166.md`

SHA-256: `b1e8b64c032e43c4c8e2343493935b4f151dc7e7b2318602b593cf2501d0f5b4`. Size: 13,553 bytes.

### Dyadic native trace one and defining sequence
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_167/tower/DYADIC_AS_TOWER167.md`

SHA-256: `2ea5941ada4e900bc600eb24198238c3555f0408b2857aa1f31342393472cd8e`. Size: 8,586 bytes.

### Dyadic depth and full character induction
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_167/central/DYADIC_FULL_CHARACTER167.md`

SHA-256: `a184a5e8cdd427419a204a85ec5a95693302f0c56b0cf6a50a7563e57dd3bcb4`. Size: 14,745 bytes.

### Actual rank-two compact group and full noncompact recovery
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_167/lowrank/RANK2_ENLARGED_CARRIER167.md`

SHA-256: `9db59d9472a7a85921bf1de2b1ea05697843e6917da5f5541216ce7eef5fe73a`. Size: 14,236 bytes.

### Actual rank-four group, scalar preimage and character orbit
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_167/lowrank/RANK4_ENLARGED_CARRIER167.md`

SHA-256: `1517e26138776fe0f32d74a174d309ec5dd6a0f572a979473d8af3d20b7a4155`. Size: 11,063 bytes.

### Actual K-normalization and fixed-candidate induction in stages
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/current_167/lowrank/RANK4_INDUCTION_BY_STAGES167.md`

SHA-256: `2d230406ee23a8451b8daa9bdbc0f53f8fe8253a95b4095d202d37024df88a4f`. Size: 4,731 bytes.

### Primary BK book: selected theorem pages inspected, not a new full-book audit
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/Paper_XI_All_Available_Work_and_Gap_Closure_Ideas_109/Paper_XI_Gap_Closure_Handoff_109/sources/the-admissible-dual-of-gln-via-compact-open-subgroups-am-129-volume-129-9781400882496_compress.pdf`

SHA-256: `811693b94c03fcbc2cfe33955bc5a00b0fc0b5645ca343f8cc1a3c6511de9c73`. Size: 12,773,776 bytes.

### Retained source text, matching historical hash d69db082...
`inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source/Paper_XI_All_Available_Work_and_Gap_Closure_Ideas_109/Paper_XI_Gap_Closure_Handoff_109/sources/BK.txt`

SHA-256: `d69db0827256707a34cd2562af68b9de11fc889ab3f43535ec47b620d58ca9c8`. Size: 759,171 bytes.

## Review limitations

- Independent end-to-end conductor source audit.
- Source-defined Bushnell--Henniart arithmetic induction/descent branch.
- Complete native marking and pre-fixed embedding audit.
- General H5 comparison.
- Fresh Lean/Lake compilation.

A search occurrence of 3.4.1 on PDF 133 was a later citation, not the theorem. The actual statement was inspected on PDF 127 with context 126--128.

The PDF image request for pages 215–217 did not return images. The retained local PDF was rendered and the images inspected instead. No OCR was used.
