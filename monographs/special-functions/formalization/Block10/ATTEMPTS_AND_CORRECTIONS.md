# Route and implementation record

Target/base: TARGET.md; 2661894c45768d240e9c2fcc4524061e404a0411.
Primary route: mean-value comparison -> geometric seed -> delayed induction.
Discriminator: actual full-radius product recurrence and bound at one.
Outcome: proved, including the manuscript's explicit upper constant, seed
index existence, canonical positive coefficients and two-sided ratio bounds.
Criterion: both canonical functions for every R>=e, with no rho>=1 premise,
unknown solution evaluations, placeholders or unproved seed assumptions.

Scratch corrections concerned elaboration: use add_le_add with an explicit
unchanged summand, prove radius nonnegativity through R_n>=1, normalize a
natural-number cast in the logarithmic recurrence, expose the upperDelay
definition to linear arithmetic, and remove unnecessary tactic sequencing.
These changed neither the contract nor any constant. The complete production
module compiled before controls and before the separate fresh public replay.
No failed fresh public replay was discarded.

The optional exponential-bounds module was not in the cache. Instead of
adding a dependency, the internal e<3 lemma was proved from the already
available exp(1/6)<=6/5 and (6/5)^6<3 with exact Lean arithmetic. This is
part of the proof and is not an approximate growth experiment.

Falsification controls reject negative R, worked N=0, omitted child-product
floors and a placeholder. The positive quarter-scale rho=1/2 example checks
the full delayed bound; exact Z_1=20 and Z_2=6416 check ladder indexing.
These finite examples test interfaces, not the universal growth theorem.

Deferred FTC alternative: integral/real-embedding API remains untried; resume
for later integral identities. Deferred weighted-supersolution alternative:
parameter-only seeds for rho<1 remain untried; resume for sharper constants
or another growth system. Neither route is exhausted or refuted. Earlier
reports preserve older alternatives. No delegated or delayed runs remain.
