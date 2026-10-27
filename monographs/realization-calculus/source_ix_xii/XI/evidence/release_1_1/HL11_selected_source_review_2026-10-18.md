# HL11 selected source verification

Checked: 18 October 2026. Source: Guy Henniart and Bertrand Lemaire, *Changement de base et induction automorphe pour GL(n) en caractéristique non nulle*, Mémoires SMF 124 (2011), DOI 10.24033/msmf.436. [Official publisher PDF](https://smf.emath.fr/system/files/2017-08/smf_mem-ns_124.pdf). Published version, 198 PDF pages. Printed page = one-indexed PDF page minus 8.

## Source extraction: verified selected inputs

III.1.1–1.2 (137–138): positive-characteristic cyclic induction, including wild degree. III.2.5–2.6 (141–143): character-transfer definition, uniqueness, conjugation, duality, central character. III.3.2–3.3 (144): Whittaker normalization and norm-compatible twisting. III.3.6 and its remark (147): existence and normalized pair L/epsilon identities for two essentially discrete inputs of the same rank. III.3.7 (148): inducing-orbit uniqueness, retaining genericity. III.3.8 remark (1) (149): cuspidality for a cuspidal input with trivial Galois stabilizer. III.3.9 (149): generic existence with unitary or orbit-regular-segment hypotheses. III.4.7–4.9 (158–160) supply the global proof route with cited dependencies.

Visual formula check: III.3.6(b) uses exponent `d m^2` on each left denominator factor, exponent `m^2` on each right denominator, and `psi_E = psi composed with Tr_(E/F)`.

## Project application: conditional on the preserved fixture

The application below is this reviewer's inference from the selected statements and the project's existing constructor argument. It is not another theorem attributed to HL11.

| Project stage | Source notation `(F,E,m,d,tau,pi)` |
|---|---|
| Inner cubic induction | `(K_1,M_K,1,3,xi_K,Sigma)` |
| Outer cubic induction | `(K,K_1,3,3,Sigma,Pi_K)` |

The selected theorem hypotheses match the preserved finite-normalized unitary source, its two genuine cyclic cubic stages, and the full-orbit arguments in `ARITHMETIC_CONSTRUCTOR_AUDIT.md`, lines 129–162. The outer-orbit argument uses the genericity of the inner character and the orbit-uniqueness clause. Every pair in the stated iterative self-pair calculation has matching input ranks. This does not support the rejected principal-series shortcut.

Remaining project dependencies are unchanged: exact source-character identification and irreducible source induction; tower-independence and naturality under the separately cited BH construction; invariance for the unramified degree-four descent; the BH tame-descent fibre and central normalization; and the stated conductor conventions. Those data were inspected in the existing project argument, not independently reconstructed here. No new missing HL11 hypothesis was found for the stated unitary rank-nine branch.

This verification closes the selected full-text access/re-reading gap. It does not prove full-character occurrence, identify a native type, or discharge H5 for the same candidate. The source's restricted pair theorem is stronger than a conductor-only identity, but its project application here remains the self-pair conductor calculation.

## Execution and preservation

Authenticated the official published source and read its relevant text, theorem hypotheses, normalization clauses, and proof references. Web source reference: `turn6view0`. Focused retrievals: `turn8view1`, `turn8view2`, `turn11view0`, `turn11view1`, `turn11view2`, `turn12view0`, `turn13view0`.

The first browser screenshot requests returned textual image placeholders without raster content. This inspection limitation was then resolved using the recovered official PDF, 2,952,761 bytes, SHA-256 `7af2940c75a75937c1bf9096eb329931d4245cf592e3572db0ff93ec6e76c5e0`. Poppler rendering and direct image review covered printed pages 143, 144, 147, 148 and 149 (PDF pages 151, 152, 155, 156 and 157). The denominator exponents, trace-character convention, central-character exponent, and hypothesis qualifiers were visually checked. No ambiguity remained in the selected formulas. The source PDF and temporary page images are excluded from the deliverable. No source or project manuscript was changed by this reviewer.

Verdict: **verified selected source interface; conditional project application under the preserved arithmetic fixture and separately cited classical inputs.** Overlap: known after translation of notation. No novelty search or full-source proof audit was performed.
