# Paper XI — changes in revised edition 1.1.0

18 October 2026 · Komorebi P. · Operation Komorebi

This is a revised publication and verification release of **Tame and Wild Packet Geometry for Local Langlands**. The general arithmetic realization statement remains Conjecture 66. The conditional comparison still requires an actual candidate and H5 for that same candidate.

## Mathematical corrections

The main manuscript still contains 68 explicit proof environments. Comparison with the preserved v1.0.0 source finds 65 byte-identical proof bodies and three revised bodies. This is a source comparison, not a count of mathematical discoveries. Statement and convention changes are recorded separately in the complete source diff.

| Location | Change and reason |
|---|---|
| Breakwise phase product, `cor:break_phase` | The old display used the full-space phase although its hypothesis allowed fixed vectors. The formula now uses the moving spaces `M = im(g−I)` and `M_s = im(g_s−I)`, with `g ∈ Sp(V)` explicit. The proof establishes their nondegeneracy and applies the product theorem on those spaces. Zero moving spaces contribute one. The retained `PaperXI.BreakOddPhase.source` already proves this domain-correct statement. No order-prime-to-p assumption was added. |
| Nondegenerate twisted group algebra, `thm:twisted_matrix` | Replaced the unnecessary claim that an arbitrary complex cocycle is literally realized by a finite central extension with direct averaging of `u_a P u_a⁻¹`. The cocycle scalars cancel in conjugation, yielding an equivariant projection and semisimplicity. The theorem's conclusion is unchanged. |
| Type-side symplectic quotient, Section 10 | Defined the previously unbound additive character on `F_p`, identified with the p-th roots of unity. Its injectivity makes the displayed equation determine the pairing uniquely. The quotient is viewed over `F_p`; the stated simple-character input remains necessary. |
| Tensor refinement, `cor:gcd_lcm_count` | The least common multiple describes the induced carrier dimension and coset-cycle length. The interaction character can have a shorter orbit and the induced packet can split further. The caption and wording now distinguish these facts. |
| Projective cocycle form, `prop:projective_holonomy` | Made the scalar-holonomy setting explicit. Projective edge maps alone do not imply scalar loop holonomies. |
| Finite tame package, `prop:tame_package` | Added the tame rank-one Artin conductor cases and the trivial multiplicative-character Gauss-sum exception. Unit-modulus phase normalization is reserved for nontrivial multiplicative characters. Replaced “complete finite invariants” with “explicit finite invariants”; conductor and local polynomial alone do not classify tame atoms. |

These changes received a focused internal mathematical review, with exact passage hashes and the current main-file fingerprint in `evidence/release_1_1/staging_core_corrections_receipt.json`. Internal review is not external peer review. The review does not certify the entire external type-theory literature.

## Source restoration and exposition

Appendix B restores the approximation index `B^[j]` as `B^{[j]}`. An earlier Markdown parser treated it as a footnote. The original note fixes the intended expression uniquely. A fresh check of the Note, Subscript, Strikeout, Cite, Image and raw-inline parser hazards across all fifteen construction notes found no second Note corruption. The earlier dimension-factor repair and 44 superscript repairs remain intact.

The odd and dyadic transition formulas explicitly use `1 ≤ j < d`; the native objects remain defined through `j = d`. The broken “skipped- degree” spacing was repaired. A pagination control keeps the finite tame package's statement together. The three editable reader sources were rebuilt with their shared monograph style. A new bibliography entry supplies the verified Henniart–Lemaire reference. BibTeX case protection preserves mathematical group names, proper names and Roman part numbers. The Serre author spelling and the epsilon symbol in Henniart’s 1993 title follow the publisher records. The visual guide’s opening bookmark and literal `--output` command were corrected.

## Formal alignment and verification scope

`PaperXI.SingleCandidateComparison.source` gives the exact one-candidate implication used in the manuscript. It takes an admissible candidate and reference in a separating factor system, plus equality of each profile with the same expected profile, and concludes equality of their isomorphism classes. It never consumes an arithmetic-existence field. This supplementary module is separate from the unchanged 423-module selection, 4,342-name lexical catalogue and forty inherited teaching excerpts.

The recovered terminal `ActualMonomialLocalGlobal.lean` is a separate tame Weil-side attachment. Adding the missing explicit `PaperXI.RamificationPolyphase` import exposed further argument, declaration-syntax and proof errors. The repaired version also makes implicit arguments and required standing hypotheses explicit and repairs local proofs. Five private component lemmas factor a costly comparison proof, and its lower-inclusion witness uses the retained equality in the required forward direction. That factoring preserves the public comparison theorem's header and conclusion. Its intended mathematical conclusions and already-declared hypotheses receive a separate review. No successful original module build is available for a comparison of kernel declarations. The original source, failed import-only intermediate, exact repair diffs and execution history are retained. A current compiler result for this target does not recreate the absent historical receipt or provide a general wild automorphic realization.

Fresh compiler, ownership and transitive-axiom results are reported in the current verification receipts and the Lean guide. The pinned Lean and Mathlib versions identify the execution environment. Cached external Mathlib dependencies and fresh Paper XI targets are distinguished. A source census, compiler acceptance, axiom dependency audit and ordinary arithmetic proof have different scopes.

## Recovered classical-source check

The selected Henniart–Lemaire source interface was checked against the full official 2011 text. The bounded record identifies its characteristic, induction ranks, genericity, orbit, central-character and local-factor normalization conditions. Printed pages 143, 144, 147, 148 and 149 were also inspected visually. The source PDF hash and exact locators are retained in the review receipts.

This closes the previously recorded access limitation for those selected inputs. It does not prove H5 for arbitrary twists, corrected-character occurrence, tower independence beyond its separate inputs, or a native-marking certificate. The source PDF is not redistributed in this release.

## Presentation and preservation

The decorative top-right branch was removed from all three rebuilt covers. The two research companions retain their mathematical text and version labels. Their matching ornament was removed from five embedded covers by changing only the selected path-paint operators. Page count, text, links and all other content are checked separately in the presentation receipt. Their original binaries remain in the preserved historical archive.

All mathematical figures remain Python-generated vector assets. The publication build preserves those assets and does not claim to regenerate them. The full prior source-and-evidence archive is retained under `historical/`; its dates, source maps, unsuccessful attempts and earlier status records retain their original meaning. The complete missing Block 2 editable archive remains unrecovered.

## Open mathematical obligations

1. Construct a general actual common arithmetic realization for every admitted H1–H4 datum, with the prescribed actions, characters, transports, phases and recovery.
2. Prove the full characterizing local-factor identities, H5, for that same realized candidate.
3. Prove occurrence of the corrected full character in the fixed continuation113 automorphic-induction candidate and identify its required noncompact extension.
4. Where the stronger native contract is prescribed, compute the actual native square/section data and honest phases on the chosen dyadic type. The separate positive transported-marking construction retains its own hypotheses.

The ledger preserves these four tasks independently. No completion percentage is assigned to an unresolved mathematical conjecture.
