# Routes and implementation notes: SF-LEAN-B08

The primary route succeeded. The complex HasSum representations were mapped
to real series and back, giving exact real-axis embeddings. Real restrictions
of the actual complex derivatives then yielded ordered real equations. A
mean-value comparison on the final unit interval gave both lower products.
Termwise norm comparison supplied actual maximum-modulus attainment.

Scratch compiler corrections concerned API/typing: a real embedded power
must be rewritten through ofReal_pow before projecting to its real part;
the UReal/U/oddSum definitions were unfolded consistently on both sides of
the series bridge; the zero-index degree was reduced explicitly; sphere
membership reduced to the existing radius nonnegativity hypothesis; and
the generic nonnegativity functions needed explicit real binder types.
No mathematical hypothesis was weakened and no placeholder entered production.

The negative-radius preflight initially timed out while matching a complex
literal -1 against an embedded real -1 under the canonical infinite sum.
Writing the real embedding explicitly removed that irrelevant elaboration
problem. The intended control then checks the impossible nonnegative-radius
premise; no production theorem or resource limit was changed.

The generic mean-value proof compiled with its full interval and positivity
premises. The second row explicitly changes the derivative output to VReal
and the scales to a,b, while retaining UReal,VReal as the product inputs.
The logarithmic and threshold proofs preserve their different radius ranges.

The FTC/integral route remains deferred because no integral interface is
needed for the proved inequality. Revisit it for later integral bounds.
The direct coefficient/binomial route remains deferred at its all-degree
unit-shift inequality and derivative-series transport; revisit it for stronger
coefficient estimates. Neither route is classified as failed or exhausted.

Four rejection controls and the positive interface fixture are checked before
the public replay. Scratch preflight files stay outside the repository's
production and evidence directories. Fresh runs use new directories and any
failed fresh run is retained separately. IO_MANIFEST.json records the actual
accepted input/output inventory rather than a proposed run.
