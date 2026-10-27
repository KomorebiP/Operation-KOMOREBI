# IUT author-side response and the 2026 compatibility target

Checked 2026-10-25. Base checkpoint: RR4, archive SHA-256
`689847eefd2cf75b9804b574d6613c13d10606e6e805a979cd74facb998ea8ae`.

This is a primary-source literature extraction and a proposed audit contract. It is not a verification of IUT III, a repair of Corollary 3.12, or a proof of abc.

## Author position and development

**September 2018, Cmt2018-08, comments C12–C14, pp. 3–4.** Mochizuki distinguishes abstract prime-strip pilots from concrete representations in log-shells and the ring structures on opposite sides of the theta-link. He argues that the simplified identity version removes hypotheses needed by the multiradial algorithm. His response also distinguishes linear relations between value-group real lines from the generally nonlinear effect on log-volumes of enlarging regions by indeterminacies. These are the author's claims, not conclusions independently proved here.

**October 2025 report, §§2.1–2.2, pp. 7–10, and §3.2, pp. 26–28.** The report identifies the central dispute as obtaining nontrivial height inequalities from the setup, rather than existence of the log-theta-lattice itself. It describes distinct copies as ordinary distinct set-theoretic objects. It presents Lean formalization as ongoing and expects substantial further work, including the management of black boxes. It does not supply a completed machine-checked abc proof.

**April 2026 formalization progress report, pp. 3–4 and §4, pp. 9–11.** This describes early skeletal work on the implication from Theorem 3.11 to Corollary 3.12, with code not yet ready for public release. The author introduces “3.11.5” as a reorganization rather than an original theorem number: apply descent and then hull/determinant before the final comparison. The first part invokes algorithmic parallel transport (APT) and the input prime-strip link property (IPL). The final comparison invokes simultaneous holomorphic expressibility (SHE) and IPL. These are stated project components, not independently verified leaves in our proof ledger.

## A more recent explicit target

**Project LANA interim report, revision 1.0.1, July 20, 2026, §9.2–9.3, p. 46, equation (9-1).** It isolates the proposed compatibility

\[
\exists\text{ suitable }S:\qquad
\eta^q=\eta^{\mathrm{anab}}_S:
\mathbb R^{\mathrm{val}}\longrightarrow\mathbb R^{\mathrm{ss}}.
\]

The first map comes from the q-pilot in its native arithmetic structure. The second uses the reconstructed action, a region/integral structure \(S\), and allowed indeterminacies. The report interprets the condition as membership of the native q-pilot comparison in an orbit of possible reconstructed comparisons. It explicitly says it has no proof of this compatibility and withholds a final verdict on IUT. It also distinguishes this condition from merely requiring the Scholze–Stix hexagon to commute. The official July 17 announcement confirms that the project had not concluded whether IUT proves abc.

## Concrete repair contract for our next route

The following is our proposed research obligation, not a theorem established by the cited reports.

1. Specify the input category, every allowed isomorphism and indeterminacy, and the precise admissibility conditions on \(S\). “Suitable” cannot mean simply that the desired equality holds.
2. Construct both maps with the same source and target, including their normalizations and pilot markings. Record all transport maps rather than replacing different ring structures by an identity without a comparison theorem.
3. Prove that the native map belongs to the admissible output family. Prove this with the required compatibility with changes of auxiliary choices. Existence of an arbitrary scalar isomorphism between real lines is insufficient.
4. Retain the quantitative region/hull estimates throughout this comparison. A construction that matches degrees by arbitrarily enlarging the output has not established the desired bound.
5. Translate the resulting inequality back to the elliptic-curve height/conductor statement, with the exact quantifiers needed for every positive abc exponent excess. This translation is still a dependency to verify, not supplied by naming IUT.

Our earlier determinant and height-accounting results suggest useful tests for step 4. They do not establish the IUT categorical comparison in step 3. Conversely, a counterexample to a simplified scale-only model would not by itself refute the above orbit-membership condition.

Disposition: open, with a precise unverified compatibility target. No global abc exponent or finiteness theorem changes as a result of this source pass.

## Version and authentication notes

Sources were obtained from the author's official Kyoto site, the official ZEN announcement, and the repository it links. The LANA TeX source was read at commit `293bdd89463473ae13d40834d70fb4b7ba81da1f` (“revision 1.0.1”, July 20, 2026). Public PDFs were inspected in memory and their byte hashes recorded in `SOURCE_RECORDS.json`; no full external text is included in this checkpoint. This was source authentication and extraction. The IUT-to-abc mathematical implication remains unverified here. No Lean code was run.
