# SF-LEAN-B12: Perron proportions of the type vectors

For the actual canonical pair with 0<q,r,a,b<1, this block proves Theorem
F.3 in the manuscript's real maximum-modulus type convention. There are
finite real scalars 0<tauLower<=tauUpper such that

\[
\underline t=\underline\tau w,\qquad
\overline t=\overline\tau w,\qquad
\frac{\underline t_0}{\underline t_1}
=\frac{\overline t_0}{\overline t_1}
=\frac{r^\rho}{1-q^\rho}=\frac{1-b^\rho}{a^\rho}.
\]

Here rho is the positive characteristic exponent; w is the strictly
positive max-normalized right vector already constructed in Block07.
The real types are the actual liminf/limsup of log(M_i(R))/R^rho, where
M_i is the spherical norm supremum identified in Block11. Either both
ordinary type limits exist or neither does. Given one component limit,
the real profile vector converges to a positive multiple of w. The actual
maximum profile has the same eventual values and the same types.

**Ordinary type convergence is conditional.** This block does not prove
tauLower=tauUpper, convergence of log U/log V under persistent oscillation,
or uniform angular growth. No such unconditional claim is attributed to F.3.

The production source `lean/CoupledTypeProportions.lean` adds **26 named
theorem declarations**, including supporting lemmas, for **299 registered
names**. All twelve coupled modules are freshly compiled, axiom-audited
(260 declarations) and kernel-replayed. The finite core's 39-name evidence
is inherited. The pinned Mathlib environment is cached, not freshly rebuilt
or replayed. All 51 fresh verification steps pass, including four expected
rejections and one positive fixture. Review provenance is self-review.

## Argument and source correspondence

Authority: Theorem F.3, `monograph/sections_v11/coupled_growth_full.tex`,
lines 354-422 at base `c6c529a58b70ebdedac1d0a7dc232153688735b3`.
The base merges the preceding F.2 evidence with GitHub main
`85cfa6f01fe7f820e7a957c9df0c5bed39efc7c7`; no mathematical source was
changed in that merge. Prior blocks and manuscripts retain their bytes.

For p>0, p(R-c) tends to infinity, and
(p(R-c))^rho/R^rho tends to p^rho. Factor a scaled logarithm into the
canonical growth ratio at p(R-c) and this positive power factor. For each
epsilon>0, the F.2 real bounded profiles eventually lie between their lower
type minus epsilon and upper type plus epsilon. These envelopes transport
through the affine arguments without assuming convergence of the ratios.

Apply the final-unit lower recurrence with c=1 to both rows. Compare its
right-hand growth profile to the sum of the two envelope functions, whose
limit is explicit. Real liminf monotonicity uses the proven upper bound
on the canonical profile and the lower boundedness of the convergent
comparison. Let epsilon decrease to zero. This proves P(rho)*lowerType
<=lowerType. For the full upper recurrence use c=0; the additional
(log R+log 2)/R^rho tends to zero since rho>0. The dual comparison gives
upperType<=P(rho)*upperType, with all real boundedness premises supplied.

The left-vector identity preserves its dot product under P. A coordinatewise
nonnegative difference with zero dot product against two strictly positive
weights is zero in both coordinates. Both type vectors are therefore fixed.
The first row, q^rho*x0+r^rho*x1=x0 with 1-q^rho>0, identifies any fixed
vector as (x1/w1)*w. F.2 positivity gives positive scalar types, and its
lower<=upper comparison orders them. The two fixed-row equations give both
displayed component ratios; their denominators are proved nonzero.

For a bounded real profile, an ordinary limit exists iff its lower and upper
types agree. Equality in either component is equivalent to equality of
the two scalars because that coordinate of w is positive. This supplies the
equivalence of component limit existence and, conditionally, the vector
limit. Block11's eventual maximum-modulus equality transports the conclusions.

The proof uses epsilon envelopes instead of separately proving exact scaled
liminf/limsup equalities. This is a sufficient complete route to F.3; it
does not register unproved exact-transport lemmas as results.

## Evidence and continuation

`CLAIM_MAP.json` covers each new theorem exactly once. `declarations.json`
binds exact names/lines and the production-source hash. `SELF_REVIEW.md`
records the focused self-audit; `PROOFREADING.md` covers changed exposition.
`IO_MANIFEST.json` distinguishes formal inputs, packaged raw outputs,
unbundled generated objects/source copies and the remaining-work assessment.
`SOURCE_MANIFEST.json` seals immutable sources, records and dated guidance.

Replay `tools/verify_coupled_type_proportions.py` with the pinned Lean and
Mathlib environment and a new work directory outside the release. The
verifier performs no installation or network access. No input changed during
the accepted replay. Root archive manifests remain earlier release snapshots.

The registered F.1, F.2, F.3, G.1 and guarded G.2 contracts are complete.
Ancillary Appendix F identities, H.1 operator classification, I-J analytic
and evaluator certificates, and broader A-E analytic coverage remain.
`REMAINING_WORK.md` gives the source-bound inventory. No manuscript-wide
completion percentage is inferred from the declaration count.
