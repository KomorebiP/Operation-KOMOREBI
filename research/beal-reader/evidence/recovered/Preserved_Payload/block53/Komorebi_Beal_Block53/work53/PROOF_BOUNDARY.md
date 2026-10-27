# Proof boundary, Block 53

## New written conclusions

B53.1 identifies local finite-precision diagonal characters under an exact
trace identity and residual separation. B53.2 is a DVR nilpotence/divisibility
lemma. B53.3 applies these, under H1--H5 and class field theory, to the actual
global diagonal correction eta_n: eta_n=1 mod 7^(floor(n/2)+1).

B53.4 describes its possibly nonzero remaining digits by an additive character.
It does not prove the remaining character lifts to the next precision.
B53.5 adds the actual scalar Frobenius input at 13 and proves good 13 ==>n=1,
without ordinary hypotheses. B53.6 adds the good-reduction order formula and
Weil bound, proving an order divisibility at every good place and forcing
11*31|C for n>=2. B53.7 excludes simultaneous depth-one beta ramification at
both places over 71, using the already compatible Kummer forms.

## Not proved

- No complete elimination of the reducible (3,5,7) branch, even when 13 is good:
  depth 1 and eligible support can still survive.
- No elimination of n>=2 when 13|C. The required integer divisor is not an
  upper bound, a density theorem, or a contradiction.
- No universal ordinary regime and no uniform upper bound on n.
- No eta_n=1 mod 7^n for n>=3. Local sharpness and surviving ray characters
  rule out using that shortcut without additional hypotheses.
- No inference that every divisor of C ramifies in beta.
- No actual semilinear comparison establishing a_3/a_5 in F7 or a conjugation-
  stable beta support. The paired71 result does not silently supply this map.
- No new result for the separate CM cover or higher Hilbert-level branches.
- No uniform exponent-signature reduction or full Beal proof.
- No global novelty claim or comprehensive literature search.

## Evidence distinctions

Theorems: complete written derivations with explicit external/geometric leaves.
Computation: exact finite checks and replayable certificates, with two
independently coded arithmetic models. Two programs written by the same
assistant do not constitute independent mathematical review.
Formalization: no new Lean source or compilation is claimed.
Review: explicit adversarial self-review only. Block50's interrupted review
is retained as historical interrupted review, not retroactively completed.

## Supersession

Earlier good 13 higher-depth scenarios were conditional possibilities. They
are now excluded under H1--H6 for ALL n>=2. The original statements about
ordinary depth 3 remain valid as implications, but their good 13 premises can
no longer all occur in the actual representation. They are retained unchanged
in the predecessor, with this live status clarification rather than deletion.
The old nonliftable ray family at n=2 is excluded as an actual diagonal for
every C. Its n>=3 bad 13 members are not excluded by the half-depth bound alone.
