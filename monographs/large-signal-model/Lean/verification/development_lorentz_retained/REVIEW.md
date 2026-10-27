# Lorentz base norm: scoped self-review

Claim: on the actual Fin 3 real state and the Lorentz cone sqrt(x²+y²) <= t, the positive-decomposition infimum is max(abs(t),sqrt(x²+y²)). The mass is the first coordinate. The model-cone and mass equivalences are explicit.

Verdict: proved for this exact subclaim. This does not by itself prove regular polygon invariance or P47's record-law bound.

The ProbabilityCone instance is constructed from proved cone closure, generation, strict positive mass and topological closedness. Generation uses actual positive differences. For every positive decomposition z=u-v, the mass triangle inequality and the spatial norm triangle inequality give cost >= max(abs(t),radius). For M=max(abs(t),radius)>0, q=spatial(z)/M has norm <=1; a=(M+t)/2 and b=(M-t)/2 are nonnegative, and u=(a,a*q),v=(b,-b*q) are cone points with u-v=z and cost M. The M=0 case is separately proved to be the zero state. These yield the actual sInf equality without assuming attainment or norm laws.

The original rational rotation/probe model is a complete instrument on this actual cone, via its proved positivity and mass identities. Initial membership in the normalized base is proved. The dedicated counterexample checks that zero signed mass does not imply zero base norm for a purely spatial vector.

Compilation passed with warnings treated as errors; all 42 explicitly named declarations passed the allowed-axiom audit; kernel replay passed. The negative control rejects at False. This is author self-review, not independent external verification. The parent coordinator owns cumulative verification and English correspondence.

Development failures were proof-engineering diagnostics: the first minimal complex-norm import did not expose the real module structure; it was replaced by Complex.Basic. Direct Complex.ext was used where the ext tactic had no applicable registered theorem. Definitional unfolding of real scalar multiplication into complex multiplication was controlled by typed change statements. The zero-cost branch used explicit max bounds rather than over-simplified simp expressions. A non-variable equality was destructured by retaining its equation rather than rfl substitution. A source-index helper initially received a relative path where it requires an absolute path; the path was corrected. None required a mathematical restriction or a changed conclusion.
