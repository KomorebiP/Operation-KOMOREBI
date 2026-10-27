# 0.8.0 attempts and repairs

See RELEASE_AUDIT.md for the complete context.

1. SymPy structural matrix comparison failed before expansion. Replaced by expanded zero-difference equality; the test remains and passes.
2. Exploratory eta=1/64 failed a requested positive-margin certificate. No certificate was released for it. A separate exact supporting functional rules it out for the final required margin 1/64.
3. An overfull theorem-heading line (3.31165pt) was fixed with a paragraph break. Final logs report zero overfull boxes.
4. The initial 14-page visual draft stretched figures. Explicit keepaspectratio constraints repaired the 8-page final version. All pages were rerendered.
5. Final proof review made sigma>0 explicit in the new regression setup. Its use was already implicit in the proof. The two mathematical PDFs were rebuilt and checked.

No execution failure was counted as a passed check. The final general proofs remain written mathematics, not Lean-verified statements.
