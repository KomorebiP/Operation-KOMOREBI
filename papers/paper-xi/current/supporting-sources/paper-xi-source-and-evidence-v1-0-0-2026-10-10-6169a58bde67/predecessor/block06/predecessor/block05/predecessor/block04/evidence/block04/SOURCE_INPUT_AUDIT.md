# Paper XI — Block 04 source and input audit

Checkpoint **P11-PUB-B04**. Updated 2026-10-10T18:00:01.921890+00:00.

The selected conductor, source-defined induction and native-marking inputs are reconciled in Part III, Sections 22–30. This is not an independent proof of the classical theory or a fresh Lean certification.

## Primary statements actually inspected

| ID | Exact locator | Status and scope |
|---|---|---|
| BH99-NORM | 6.1 setting and Lemma 2; printed 53, 54 | `fresh_page_image_review`. Actual central type and principal order. Native psi trivial on p; exponent nr/e. Standard conductor adds n. |
| BH99-TAME | 1.3 tame-lift properties; printed 15 | `fresh_page_image_review`. Actual tame descent fibre, character twists and central-character normalization. |
| BH99-PAIR | 1.7 conductor transfer; printed 18 | `fresh_page_image_review`. Keep pair exponent and tame ramification normalization; e=1 gives unchanged exponent. |
| BH99-MONOMIAL | 2.3 theorem and monomial construction; printed 23, 24, 25 | `fresh_page_image_review`. Originally characteristic zero. Standard epsilon factors and pair L/conductors. Tower independence is substantial input, not formal conjugacy. |
| BH99-LIMIT | Introduction, conductor versus full pair factors; printed 2 | `fresh_page_image_review`. Full pair epsilon equality is explicitly not established by this construction. |
| AP-NORM | Section 4 formula (5); printed 8 | `fresh_page_image_review`. Additive character conductor O_F; ordinary pair conductor is defined by epsilon ratio at 0 and 1. |
| AP-DEGREE | Formulas (17), (29); printed 19, 26 | `fresh_page_image_review`. Steinberg and actual compact-type degree with fixed Haar and central measures. |
| AP-PAIR | Theorems 6.5, 6.9; Remark 6.7; printed 27, 28 | `fresh_page_image_review`. General nonarchimedean local fields. Torsion r_t and delta; no HII conjecture used. |
| BH13-CHAR | Note on characteristic; printed 8 | `fresh_page_image_review`. Earlier characteristic-zero restrictions extended using HL11. Effective main construction not used to solve its own totally wild input. |
| HL11 | Henniart–Lemaire, Mémoires SMF 124 (2011), DOI 10.24033/msmf.436; printed metadata only | `metadata_checked_fulltext_not_retrieved`. Underlying detailed III.2/III.3 statements retain inherited audit status. Full PDF requests failed in this block. |

PDF pages in the JSON record are **one-indexed**. BH99 printed page p is PDF page p+5. The web screenshot API uses a zero-indexed value p+4. AP and BH13 printed page numbers match one-indexed PDF page numbers for the selected pages.

## Normalization and application conclusions

For the retained rank-nine source, standard Swan/ordinary conductors are 24/33. End(rho) has dimension 81, inertia invariants of dimension 1, Swan 152 and ordinary conductor 232. With psi trivial on p, its epsilon exponent is 151. The trace-zero adjoint has dimension 80 and exponent 152. AP delta also equals 152 in the torsion-one comparison, but is not defined as the BH epsilon exponent.

The principal-order formula uses the actual leading level and period. At rank nine, conductor matching permits period/level (3,8) or (9,24). The candidate must independently pass torsion and actual-order checks. In the certified period-nine family, self-pair conductor is 2c+224, so source matching forces c=4 rather than c=10. This does not construct the corrected stratum.

The full and skipped rank-eight profiles can have standard ordinary conductor 68, torsion 1 and self-pair conductor 342 with quotient dimensions 6 and 4. The parity identity explains the lost capacity information. The skipped profile keeps its inherited ordinary arithmetic construction status; only its grade consequences were freshly tested.

BH99 2.3 is explicitly characteristic zero. BH13 page 8 is the freshly checked bridge to positive characteristic through HL11. The full HL11 PDF could not be retrieved. Its detailed induction/base-change statements remain an inherited input, not freshly inspected text. No full pair epsilon/H5 conclusion is inferred from pair conductor preservation.

## Inherited source pins

### Q13 — read_and_reconciled
`sources/inherited/ADJOINT_CONDUCTOR_TEST161.md`

SHA-256: `0a106a9a6cc398fb9e904f8efbb88fdbbf2d7f5c7c466762e91c3c223dce0db9`.

Sections 22–23; actual-order and normalization hypotheses retained

### Q14 — read_and_reconciled
`sources/inherited/PRINCIPAL_ORDER_CONDUCTOR161.md`

SHA-256: `c98e3ccc824195a0cad835994d9498f144e97699fde513826365de419dceea06`.

Section 22; principal period, leading level, additive character

### Q15 — read_and_reconciled
`sources/inherited/ARITHMETIC_CONSTRUCTOR_AUDIT.md`

SHA-256: `80dad87abea2f753c0ddc93774fa29a8d5a3fa78c9c3e2feed4e90b81ef4d54d`.

Section 25; named classical inputs, no native occurrence conclusion

### Q16 — read_and_reconciled
`sources/inherited/DYADIC_MARKINGS167.md`

SHA-256: `c7100545a6d13d790f6aefa4f52166f9dde5a7060854128aa3cdb05b598dd1c4`.

Sections 26–29; fixed versus transported marking

### D167 — read_and_reconciled
`sources/inherited/DYADIC_CAPACITY167.md`

SHA-256: `714fac1a7d34ee9c4c28fcfcc08c8950ef75e108ee9f3cd39fbb50b75d174552`.

Section 24; conductor/capacity consequence of inherited arithmetic profile

### NEXT-PROOF — preserved_next_reading
`sources/inherited/PROOF167.md`

SHA-256: `97f66d4a3fa8c8218e3646fd7414b7591148dfe88480b49d382d70de6e9ee849`.

Future visual synthesis and native-marking arithmetic certificate

### NEXT-CHARACTER — preserved_next_reading
`sources/inherited/DYADIC_FULL_CHARACTER167.md`

SHA-256: `a184a5e8cdd427419a204a85ec5a95693302f0c56b0cf6a50a7563e57dd3bcb4`.

Retain complete character and noncompact extension

### NEXT-TOWER — preserved_next_reading
`sources/inherited/DYADIC_AS_TOWER167.md`

SHA-256: `2ea5941ada4e900bc600eb24198238c3555f0408b2857aa1f31342393472cd8e`.

Actual rank-eight parameter, not an abstract quadratic form

### NEXT-CONTRACT — preserved_next_reading
`sources/inherited/ORIGINAL_DYADIC_CONTRACT_EXCERPTS167.txt`

SHA-256: `04c28d3d3c1e1970efe5139087b841e43a72f1e32bda018edaf97c2eaba5b3a3`.

Original required finite marks and comparison contract

### NEXT-RECOVERY — preserved_next_reading
`sources/inherited/ENLARGED_CARRIER_CONTRACT167.md`

SHA-256: `40e143e7f0abc592c328aa3617595508a3f2d2d46a6af32421eb8cbae179fa2b`.

Do not conflate original quotient and changed assembly carrier

## Primary source locations

https://www.numdam.org/item/AST_1999__254__R3_0.pdf

https://arxiv.org/pdf/math/0302169v4

https://arxiv.org/pdf/1103.5316v2

https://www.numdam.org/item/MSMF_2011_2_124__1_0/

## Access and audit limits

Web page-image inspection succeeded for the selected BH99, AP and BH13 statements. Repeated full-PDF requests for HL11 failed. Requests from the container failed DNS, and the attempted direct HL download was rejected because no successful viewed URL was available. No nonexistent downloaded source or local PDF hash is listed.

The actual BK type-order/refinement inputs retain the previous selected audit. This block did not re-read the full BK book or rerun an arithmetic rank-eight/rank-nine matrix constructor. The finite extension and correction proofs are printed in full. Actual native lifts, their quadratic refinement and honest phase operators on a prescribed candidate remain separate arithmetic obligations.
