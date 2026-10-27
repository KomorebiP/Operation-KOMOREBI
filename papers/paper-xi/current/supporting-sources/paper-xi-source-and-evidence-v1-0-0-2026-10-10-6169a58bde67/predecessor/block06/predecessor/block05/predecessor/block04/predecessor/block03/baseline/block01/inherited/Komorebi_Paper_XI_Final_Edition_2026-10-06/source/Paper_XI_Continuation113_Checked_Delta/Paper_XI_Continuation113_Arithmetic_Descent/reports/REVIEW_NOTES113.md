# Final editorial and provenance notes

The new mathematical reports were reviewed under the conservative
proofread-math workflow. The original-versus-corrected character distinction,
conjugation directions, field traces, scalar phases and original H5 boundary
were also checked substantively in the separate independent proof audits.

Routine edits in root integration: explanatory wording and mathematical
display/inline delimiter checks. No Lean source was changed after its final
frozen verification. No mathematical-token correction was made as a purely
editorial shortcut. The lattice additive-character sign was a substantive
integration correction, retained and reviewed as such, not silently treated
as a typo.

Explicit erratum to one descriptive JSON string: the phrase
`inside ker psiL=pL^-3` in central_normalization_result113.json should read
`inside the conductor ideal pL^-3, which is contained in ker psiL`.
The entire additive kernel is not asserted to equal that fractional ideal.
Only the correct implication that psi_L is trivial on pL^-3 is used anywhere
in the proof or computation. The frozen script/result are retained to preserve
the audited hashes; this note is the delivered correction to their wording.

The old v1 arithmetic computation manifest was overwritten during development
before it had been archived. That original receipt is not recoverable here.
The first-passing script was recovered with its exact previously recorded
hash, and the overwrite is disclosed in evidence/arithmetic/FAILURES113.md.
The final v2 run is a genuinely new replay with actual before/after input
hashes, not a reconstruction or upgrade of the lost receipt.

Mathematical proof status remains split: four abstract modules are Lean-checked;
the explicit arithmetic and its exclusion/correction use ordinary source-backed
proofs and exact computations. No report implies that the local-field analysis
was formalized in Lean. The original theorem remains at65/66.
