# Route record and implementation corrections

Route SF-B12-ENVELOPES starts at c6c529a58b70ebdedac1d0a7dc232153688735b3.
Target: full canonical F.3 under positive strict contraction scales.
Mechanism: affine power-factor limits, eventual epsilon envelopes, row
comparisons, strictly positive left weighted rigidity, then two-dimensional
fixed-space algebra. Discriminator: scaled transport without assuming
ordinary convergence of the type profile. Outcome: proved; route complete
for the registered F.3 contract. It does not close ancillary Appendix F.

Development compile diagnostics were implementation corrections, not
counterexamples: an unconstrained local exponent needed an explicit value;
the logarithmic little-o lemma is in the root namespace; neighborhood
restriction uses Tendsto.mono_left; explicit finite-sum simplification is
needed for matrix coordinates; the eventual-equality transport API is
Filter.tendsto_congr'. An unused ring/simp tactic and an ambiguous local
eventual proposition were removed or given explicit types. Addition bounds
were supplied with add_le_add to make the summand position unambiguous.
The final production module compiles with warnings as errors.

Route SF-B12-EXACT-TRANSPORT remains deferred: exact equalities of scaled
liminf/limsup require bounded variable-factor transport. The envelope route
proves every F.3 conclusion without those equalities. Resume if such
identities are needed independently; the route is not refuted or exhausted.

Route SF-B12-CLUSTER remains deferred: componentwise extremal cluster
points need not occur simultaneously. No simultaneous-extrema premise was
used. Resume only for a theorem with a separately proved compactness or
joint-accumulation input. No numerical experiment or novelty claim was used.

The website regression initially exposed a source-selection distinction:
new formal companions are maintained repository additions, outside the
frozen imported reading bundle. The subject hub now links the dated
maintained formalization guide and revision-resolved GitHub artifacts,
preserving the historical bundle receipt. The reader's coverage paragraph
uses the maintained status record instead of a stale hardcoded 68 names.

No delegated or delayed job exists. Formal replay attempts, including any
failure before the accepted run, are inventoried in IO_MANIFEST.json; earlier
Block11's resource-failed replay remains preserved in Block11 unchanged.
