# Collatz conjecture monograph source map

Prepared 2026-10-08. Author/release name: Komorebi P.

This file records source recovery and claim scope. It adds no mathematical theorem. The manuscript uses readable saved source files and audit records. Historical Lean results are attributed to their saved checkpoint verification records. No fresh complete Collatz Lean rebuild is claimed by this monograph.

## Recovered project sources

All line windows below refer to the complete read metadata saved alongside each text in `evidence/`. A complete read means that all returned textual lines were recovered. It does not mean that every import, original archive byte, historical compilation environment, or source dependency was recovered.

| Original filename | Library identity | Read scope | Source date and role |
|---|---|---|---|
| CollatzBlocks.lean | libfile_02c4015a1f9481919b9b02fbcd78c0f6 | Complete, lines 1–454 of 454 | Saved 7 September 2026. Exact accelerated odd map, run laws, repeated pair families, and induction bridge. |
| Komorebi_Collatz_Serious_Audit_2026-09-11.md | libfile_a8d99785726c819189c4e5071672df3a | Complete, lines 1–378 of 378 | Audit dated 11 September, saved 12 September 2026. Frozen v0.19 checked source closure, with two v0.18 archives compared separately. |
| README(20260911-003925).md | libfile_1ecd7e2b97708191a342199d62442629 | Complete, lines 1–84 of 84 | Saved 11 September 2026. Bounded deficit v0.5.0 claim and recorded verification boundary. |
| README(20260911-014123).md | libfile_cf724b89c3808191b8cccfa6a4e4c724 | Complete, lines 1–77 of 77 | Saved 11 September 2026. All bounded deficit v0.6.0 claim and recorded verification boundary. |
| GAP_REGISTER.md | libfile_e3348492063c8191ab21e978b06896e4 | Complete, lines 1–87 of 87 | Saved 12 September 2026. Corrected open obligations after v0.19 and the serious audit. |
| Komorebi_Collatz_Global_Route_Notes_2026-09-12.md | libfile_e7ad9a533af0819180bcff382b91e5cc | Complete, lines 1–184 of 184 | Saved 12 September 2026. Written research route deductions. Not a new global closure certificate. |
| FINDINGS(20260918-232154).md | libfile_b7270981a9a481918ef4bcfa69b2a3e9 | Complete, lines 1–17 of 17 | Saved 18 September 2026. Proof Atlas v0.14 finite coverage findings. |
| FINAL_VERIFICATION(20260918-232234).json | libfile_fe6c509fe95c8191a999e4e977932dc6 | Complete, lines 1–35 of 35 | Saved 18 September 2026. Proof Atlas v0.14 verification report and explicit nonclaims. |
| CollatzDeepResidueCertificate.lean | libfile_a487dc49c45c819184c54874133fc35a | Partial, lines 1–1000 of 1867, has_more=true | Saved 18 September 2026. Read window of the deep residue certificate. Lines 1001–1867 were not recovered in this evidence snapshot. |
| CollatzFixedHorizonObstruction.lean | libfile_18f0025b983c81918832b782a5c4bba8 | Complete, lines 1–114 of 114 | Saved 19 September 2026. Proof Atlas branch, fixed horizon obstruction. |
| CollatzUnboundedRunFamily.lean | libfile_98b8f05e0f9c8191b4252a4a05d608ad | Complete, lines 1–123 of 123 | Saved 19 September 2026. Proof Atlas v0.16 explicit seed family. |
| CollatzParametricRunExit.lean | libfile_191044739f488191afc775b6bdf6d0f8 | Complete, lines 1–133 of 133 | Saved 19 September 2026. Proof Atlas v0.17 arithmetic progression lifts. |
| AUDIT_BOUNDARY.md | libfile_d23cac48d59c8191b3e14f36d4aa4ddb | Complete, lines 1–24 of 24 | Read version_id=14, modified 19 September 2026. Proof Atlas v0.17 scope and import dependency boundary. |

Every recovered read other than `AUDIT_BOUNDARY.md` returned `version_id=null`. No version number is inferred from a filename, checkpoint label, or timestamp. Source checkpoint labels such as v0.6.0 and v0.17 identify their respective research packages, rather than Library revision numbers or a universal sequential certification status.

## Historical certification scope

The serious audit reports a fresh build of 54 of 54 local modules in the frozen v0.19 closure, with pinned Lean 4.34.0-rc2 and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. It reports an axiom traversal of 1,612 local environment declarations and explicitly distinguishes source declaration counts from independent mathematical contributions. These are historical audit statements read from the saved report, not fresh checks performed for this monograph.

The later Proof Atlas v0.17 audit boundary reports a freshly compiled twelve-module source closure, separates type-only dependencies from body dependencies, and limits its transitive internal edges to that closure. It expressly excludes fresh rebuilding of every inherited record and independent validation of the compiler and trusted Mathlib binary caches. The v0.19 Collatz audit and v0.17 Proof Atlas scope should not be merged into a claim that every historical source was rebuilt together.

The v0.14 final verification report gives 1,804 covered odd residue classes out of 2,048 modulo 4,096, with 244 unresolved classes. It explicitly says that the unresolved-class list is finite computation evidence rather than a Lean enumeration theorem, and that no complete finite cover or Collatz theorem is claimed. The partial read of the deep certificate is not represented as a complete source recovery or an independent reconstruction of the enumeration.

The Proof Atlas audit records also include Physics claims. The Collatz monograph uses only their Collatz scope and does not import the physical interpretations as support for its arithmetic conclusions.

## External literature dependencies

The shared `../shared/LITERATURE_CHECK.md` records authenticated primary source checks, exact versions, and acquisition limits.

| Reference in bibliography | Consulted evidence | Use and boundary |
|---|---|---|
| Tao, arXiv:1909.03562v7, 16 July 2026 | Author preprint introduction, Sections 1.1 and 1.2, stated results | Classical and Syracuse map conventions, almost all logarithmic density statement, and precise quantifiers. This does not imply universal orbit termination. |
| Terras, 1976 | Publisher metadata and historical attribution in the checked Tao introduction | Finite stopping time of natural density one. The original full proof was not reread because original PDF acquisition failed. |
| Terras, 1979 | Publisher metadata and historical attribution in the checked Tao introduction | Density clarification, cited with the 1976 paper. The original full proof was not reread because original PDF acquisition failed. |

The metadata are exact: Terras 1976, Acta Arithmetica 30, 241–252, DOI 10.4064/aa-30-3-241-252. Terras 1979, Acta Arithmetica 35, 101–102, DOI 10.4064/aa-35-1-101-102. Tao's published paper is Forum of Mathematics, Pi 10 (2022), e12, DOI 10.1017/fmp.2022.8. The version pinned for this source check is its 2026 arXiv v7, not a claim that its original publication occurred in 2026.

## Access and reproduction boundary

Readable project records were recovered through the exact full or partial windows listed above and retained with their read metadata. Original Terras PDF acquisition produced HTTP 403 or fetch failures, and the checked modern primary text supplies the density statement used for orientation. No inaccessible original body is represented as having been reread.

The recovered Proof Atlas audit boundary itself reports that original v0.14 full archive bytes remained missing in that historical package. This is a saved provenance limitation. It is not a statement that those archive bytes were downloaded or inspected during creation of this monograph.

This evidence collection is sufficient to describe the stated arithmetic results, formal hypotheses, and open global obligations. It is not a complete portable Lean dependency archive. Any new replay must resolve the original project dependencies and pins separately.
