# Paper III final release calibration review

**Reviewer:** analytic audit agent. **Checked:** 2026-10-20, approximately 14:12 UTC. **Verdict:** PASS for the release-language and source-continuity checks below; the single material wording correction has been applied.

This is a final read-only calibration and provenance check, not a new mathematical proof audit or compiler run. The earlier `analytic_review.md` and `formal_composition_review.md` retain their original reviewed hashes and scope. No production source was edited during this check.

## Release claims

The calibration read covered active `README_FIRST.md`, `metadata/RELEASE_NOTES_v1.0.0.md`, `metadata/FAILURES_AND_LIMITATIONS.md`, `guides/lean/chapters/00_current_release.tex` and its generated receipt inclusion, the supplement's verification/status section, and `formal/verification/FINAL_VERIFICATION_SUMMARY.json`.

The only material wording defect was omission of pairwise annihilation from the Lean guide's description of coordinate analysis and synthesis. The current guide, line 15, now says **“finite complete pairwise annihilating idempotent family”**, matching the actual packet-system assumptions. The added `\phantomsection` is present at the current chapter label. Current guide SHA-256: `5b79ea99421ceeb16361ee5cb611aab45b9e6d11ae75fa0c110fe8bed14cac0f`.

No other material calibration correction was identified in the requested files. They distinguish the ordinary manuscript from its formal subset; the literal inherited range bound from the ambient bound; and accepted norm results from separately unformalized restricted-product/Hilbert corollaries. Taylor and the Stirling count remain outside the project formal closure. Actual derivative composition has the stated differentiability hypotheses and canonical ordered-partition convention; the real/complex symmetry explanation and one-way support conclusion are correctly scoped. Historical checkpoints and unrecovered historical claims are distinguished from current receipts. These findings do not expand the mathematical coverage of the earlier audits.

## Mathematical source continuity after layout adjustment

The current Section 17 byte slice begins at `\section{Packet jets and higher composition}` and ends immediately before `\section{Rooted tree expansions}`. Exactly one `\clearpage` line follows `\label{fig:packet-jet-example}` and `\end{figure}`. Removing **only that anchored inserted line**, with no general whitespace normalization or other alteration, reproduces the previously audited Section 17 hash. Applying the same one-line removal to the complete chapter also reproduces its previously reviewed full-file hash.

| Source/state | SHA-256 |
|---|---|
| Current complete manuscript chapter 03 | `4fd9f0146473d4411cb39f485bc2524d738a858f92f1ffbe714c0ce6818d6862` |
| Complete chapter after removing only the inserted line | `075b8d329d9f0518149a200d590efd8972460cb5f4ab8052211e9bd221179375` |
| Current Section 17 | `da470cb6c58c82cf56f49f381c755df13062a3f408c0608420c05b2c9ecf4b27` |
| Section 17 after removing only the inserted line | `e564f9b71c07b334b1e0a3b62da949b5ae3d779a4b9d89fa0065e9513e96076d` |
| Supplement mathematical sections 1–4 | `a9d082e83a434a69cba93ea319190772be52c13ae40e20de6cb6f133c78e2110` |
| Current complete supplement | `8bb4854eb266315613b1cdd16730ccff7e516f0ca7def9b20988475791758e57` |

The supplement mathematical slice runs from `\section{Two distinct contracts}` to immediately before `\section{Verification and reproduction}`. Its hash still matches the prior review exactly. Both complete-chapter hashes match `evidence/review/LAYOUT_SOURCE_DELTA.json`. The layout edit therefore leaves every audited statement, proof and formula unchanged.

## Formal receipt cross-check

The checked final summary has SHA-256 `4fa5e0d2dc4a985e5daab29a4b2a6bc17c4dc2300f5552fc64226c72d1d1e24e`. All four referenced report files exist and their actual byte hashes match the values recorded in that summary:

| Accepted phase | Report SHA-256 |
|---|---|
| Full build | `8de6d41d6bb1cae20d97025f928d0cb7d2ddc3e2b5473632624cdf51dd9d09a7` |
| Ownership audit | `a450ebefddb682505ec1fbacc41e05c98341acfff8664739843173f55da1da72` |
| Kernel replay | `6cbdd99f3f58da8dfd6e7da94d2d669be415dfcc9e3a71fc21d838afecad5833` |
| Controls | `104956faa652c23657329216aabbe70b6b92538db6708e644c198468f2d1543b` |

The current four added packet-module source hashes also match the summary and the previously reviewed revisions, including `ContinuousPacketJets.lean` at `63f96e83190b694b27b00a9649fc87cac9a3b0a6d65830c2a2b5249e76cad924` and `PacketJetComposition.lean` at `06e1d95456304561dd967bb924d23ff45b1c2fe8b710fc472a9d002fde7f0b3e`.

The release's current counts agree with the summary and generated guide receipt: **16 production modules; 608 owned declarations; 594 replayed logical declarations; 14 generated runtime helpers; 33 owned declarations outside the primary namespace; 14 accepted controls.** The declaration-kind counts sum to 608, as do replayed declarations plus runtime helpers. Every control has its expected outcome accepted, including expected rejection cases. Earlier 14- and 15-module checkpoints are explicitly historical. This cross-check validates the consistency and binding of the cited receipts; it does not represent an additional execution of the compiler or kernel replay.
