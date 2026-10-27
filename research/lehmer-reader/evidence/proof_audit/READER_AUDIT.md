# Critical reader audit, Series 07

Date: 9 October 2026. Reviewer: /root/lehmer_review, an AI agent.
Project-relative paths below are rooted at lehmer_set/.

**Semantic verdict: the readers preserve the exact scope of the reconstructed
side theorems and the recorded finite evidence. No unresolved mathematical
error was found in this pass. Lehmer's all-prime nonvanishing obligation remains
incomplete.** This report is not a proof-assistant verification, an exhaustive
literature or novelty check, or approval of a final PDF layout.

The normalized target is the fixed cusp form
\[
\Delta(q)=q\prod_{m\ge1}(1-q^m)^{24}
=\sum_{n\ge1}\tau(n)q^n.
\]
Prime reduction and the modulo-five congruence leave the precise obligation
\[
R(p)=\tau(p)\ne0\quad\text{for every prime }p\equiv4\pmod5.
\]
The present manuscript does not supply that implication. Its conditional
finishing inputs are explicitly labeled as further hypotheses.

## Material reviewed and revision identity

The complete mathematical and narrative source of the monograph was read:
opening.tex; chapters01_03.tex; chapters04_05.tex; chapters06_07.tex;
chapters08_10.tex; chapters11_12.tex; chapters13_14.tex; chapters15_16.tex;
chapters17_18.tex; chapters19_21.tex; chapter22.tex; appendices.tex;
appendix_operator.tex; appendix_workbook.tex; bibliography.tex; and main.tex.
The full visual/main.tex guide text, its captions, and its source section were
also reviewed. These files and the evidence contracts used for reconciliation
are pinned in reader_source_hashes.json.

This is a critical reconstruction against the raw packages and exact source
contracts, not a blind experiment. Historical verdicts were visible. The
separate RAW_PROOF_AUDIT.md records the reconstructed raw theorem inventory,
source locators, dependencies and remaining obligations. No historical
research file was changed in this audit.

The reviewer authored chapter22.tex at the root agent's request. Its review
here is therefore self-review, rather than an independent author-review
claim. The separate /root/lehmer_formal agent read that chapter in full and
passed its equivalences, strict sign premises, adaptive residue premises and
claim boundaries. That agent requested the explicit normalized-Frobenius
comparison premise, which was applied. The root agent separately reviewed its
scope. Other manuscript chapters and appendices were authored by other team
members and critically read here.

The final source reconciliation covered the reported second-build changes:
the aligned prime-reduction statement; removal of a redundant Chapter 5
bridge; relocation of the bounded 300-polynomial experiment; relocation of the
intact low-degree limitation from Chapter 8 to Chapter 9; the explicit
operator range m >= 2; the even/odd local exponent boundaries and R(1);
Chapter 22 table and closing-paragraph polish; the appendix recurrence,
zeroth-moment terminology and individual-review wording; and bibliography
spacing. The mathematical scopes are preserved by those changes.

## Mathematical scope checks

| Portion | Checked result and its boundary |
|---|---|
| Chapters 1–3 | Defining coefficient shift, exact recurrence, odd-square parity and prime-power zero criterion. The root-of-unity consequence is derived from a zero, with actual p = 2,3 handled separately. |
| Chapters 4–5 | The differential and Hurwitz/Catalan expressions are exact differences. Their universal algebraic/source inputs are separated from bounded output agreement. Imprimitive forms, exceptional weights, 6H and the t = 0 zeroth-moment half term are retained. |
| Chapters 6–7 | Packet residues, norm 10n, core size n−1, Vandermonde orientation and D/288 are consistent. Index-prime units do not imply unit total. Auxiliary U is not the prime index; the 300-prime factorization range is explicitly bounded and unused in universal arguments. |
| Chapters 8–10 | The harmonic theta input is vector-valued. The 3125-coset sign-line argument supplies the scalar full-level descent, with T = 1 and the group relation forcing S = 1. Harmonicity and valence justify universal nullness; a sign certificate additionally needs a strict nonzero contribution. |
| Chapters 11–12 | The all-depth dyadic first mixed-shell formula is proved by a lower bound and symbolic witnesses. The finite enumeration does not replace it and does not assert the boundary is prime. Sector defects are linear-space dimensions, not counts of failed signs. |
| Chapters 13–14 | Exact-content scaling includes chi_5(g)g^10. The refinement short exact sequence uses occupied-sector aggregation and its actual image. The p = 31 rational stages are finite certificates, not an all-prime transfer theorem. |
| Chapters 15–16 | Even primitive blocks survive for m >= 1; R(1) = 1 is separate. The tied valuation t = 5, a = 0 and p = 5 are controlled. Odd quotients are defined polynomially before evaluating a = 0, with m = 0 separate. R and tau have exactly the same zero set. |
| Chapter 17 | Every finite symmetric polynomial universal null conserves each exact-content total. Homogeneous harmonic decomposition and separation of finitely many quasimodular weights justify removing homogeneity. Infinite series and nonsymmetric functions are excluded. |
| Chapter 18 | Even invariants separate J-orbits, and homogeneous interpolation is constructive. Shell nullness is weaker than universal nullness; harmonic projection can erase shell values. Fullness remains unproved and, even if assumed, retains the unknown prime total. |
| Chapter 19 | Complex conjugation lies in the actual joint finite image. Chebotarev yields a positive-density set for each fixed M. The trace argument precedes reduction at ell = 2, M = 1 is handled, and no image independence is assumed. For all M, there exist primes does not imply one prime for all M. |
| Chapter 20 | The local trace-zero filtered module is weakly admissible because total invariants agree and there is no rational Frobenius-stable line. Crystalline realization does not identify it with the actual global Delta representation. |
| Chapter 21 | A synthetic multiplicative sequence can preserve every listed arithmetic premise and any fixed prefix/modulus while having a prime zero. It is a countermodel to that implication, not a counterexample to the fixed actual form. It is not unconditionally called nonmodular. |
| Chapter 22 | The remaining-family equivalence, adaptive residue input and strict sign input have correct quantifiers. The local-to-global comparison and cusp-form identification are explicit additional premises. Authorship and separate review are stated above. |

The coordinate operator appendix was also checked directly. The chart metric,
pairwise cancellation in the conjugated Laplacian, Newton reductions s_6,
s_7,s_8, and the rank-four top harmonic projection coefficients agree with
their definitions. These are polynomial constructions, not a global prime
nonvanishing mechanism.

For the exact workbook, workbook_exact_checks.json records this reviewer's
independent integer and rational checks of all 22 displayed B/C/layer rows
for 499 and 16249, the selected p = 31 totals and transfer values, and the
coarse-kernel basis used for the two-stage transfer. Its matrix kernel
identity is exact. Rank 13 over both displayed prime fields, together with
the structural upper bound, confirms that basis size. Its final source
revision is pinned there separately.

## Source and execution reconciliation

The external dependency review belongs to the separate literature agent.
This pass read its exact 16-contract record and matched the reader's uses to
those contracts. The source_contracts.json revision used here has SHA-256
4966eb2c00b7214da5a6a3f6c6195aef97d10da189a52ab0eda2ccf3dceeb04a.
No broader theorem, source title, inaccessible original proof or withdrawn
submission is imported as established evidence. Han, harmonic theta, valence,
representations, Chebotarev and Colmez–Fontaine remain distinct leaves with
their project-specific translation arguments.

The reproduction appendix's execution counts were matched to the current
SUMMARY.json and suite results. There are 16 fresh suites, 13 historical
scientific-output comparisons excluding only the three named elapsed-time
fields, and three additional independent suites. The appendix preserves the
differences between exact integer coefficients, residues modulo 2^19, selected
prime comparisons, constructed companion matrices, rational certificates and
bounded search failures.

The displayed CRT reconstruction inequality was independently recomputed:
1032191(524288−1)^2 = 283725419316756479 <
998244353·1004535809 = 1002772198720536577. This identifies an integer
convolution coefficient from the two field residues before reduction; it
does not reconstruct the large tau integer from a single residue. The
resource-limit prose matches the fresh modular_ntt version-two manifest.
Validation of all program executions, hidden failure accounting and resource
enforcement is the separate computation audit's responsibility; this pass
does not recast command success as proof.

The guide's text preserves the same object, quantifier order and boundaries.
Its numerical figure generation and individual data checks belong to the
computation/visual audits. Reading its captions here is not a claim to have
independently rerun every plotted dataset or inspected every guide page.

## Corrections made during review

Meaning-changing and provenance-sensitive corrections were coordinated with
their file owners before release. Four missing backslashes before qquad and
one formfeed byte in an intended frac expression in chapters11_12.tex were
removed. Explicit GKS, Hurwitz/Catalan and normalized differential source
citations were supplied. The operator/scalar T conventions were distinguished.
The workbook now says that a checksum pins bytes and provenance records
execution. The closeout's form-identification premise says holomorphic cusp
form, and its local comparison explicitly identifies the normalized
Frobenius trace with tau(p). The reproduction appendix now describes an
individual visual review, without asserting an unperformed human review.

Boundary corrections explicitly state the operator formula's m >= 2 range,
the scalar recurrence's r >= 2 range, the primitive even formula's m >= 1
range, the odd formula's m >= 0 range, and the constant residual R(1) = 1.
No undefined negative recurrence index is needed.

## Layout status and remaining obligation

This reviewer individually inspected preliminary physical pages 59–78 at
original resolution, from the 108-page snapshot with SHA-256
4a6fd87e3730836c729dc6ada04d4f96a8655cd093b99ba3cfced3e7bab2838e.
PRELIMINARY_PAGES_59_78.json pins every inspected image and records no
clipping, overlap, missing glyph, equation-number collision or scope defect.
Chapter-tail density observations were sent to the root agent. That snapshot
is superseded by an integrated revision; its inspection is not final PDF
approval.

The final frozen paper has 103 physical pages and SHA-256
67489fe4cba46d9a1f09010576b2dba182a29c1a8b44803f60e98068af6241de.
Every physical page 59–78 was then re-viewed individually at original
resolution. The range passed with no blocking issue, and its final
inspection record is evidence/layout/manual_paper_review.json. The record
pins each inspected image and explicitly covers only this assigned range;
other pages have separate reviewers. The reader-source inventory was
rechecked against the frozen sources, including the final copyedits, and all
41 input hashes remained current.

The unresolved obligation is mathematical rather than typographic: exclude
exact zero cancellation of the actual signed packet total at every prime
congruent to four modulo five. No finite range, compatible local realization,
uniform side theorem about squares or reversed pair of quantifiers closes
that gap. The reader correctly retains it as open.
