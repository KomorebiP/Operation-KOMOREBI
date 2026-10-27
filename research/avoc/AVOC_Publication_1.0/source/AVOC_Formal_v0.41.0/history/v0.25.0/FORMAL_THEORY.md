# AVOC v0.25.0 — generated candidates, exact checking, paid promotion

## 1. Protected semantic domain

An input is exactly three Boolean values. Programs contain constants, variables 0/1/2,
negation, conjunction, disjunction and exclusive-or. `run` is a total pure interpreter.
`runCount` eagerly visits both children of each binary expression. Lean proves:

\[
\operatorname{runCount}(p,x).1=\operatorname{run}(p,x),\qquad
\operatorname{runCount}(p,x).2=\operatorname{nodes}(p).
\]

There are exactly eight inputs. The executable checker evaluates every one, and the
library proves both directions:

\[
\operatorname{check}(p,q)=\mathrm{true}
\iff \forall x,\ \operatorname{run}(p,x)=\operatorname{run}(q,x).
\]

This is a complete decision procedure for this finite input semantics. It is not a
sampling claim or a general equivalence checker for arbitrary software.

Source: `AVOC/BooleanProgram.lean`.

## 2. The candidate pool is generated from primitives

The seed pool is false, true, x0, x1, x2. At the next depth the generator retains the
previous pool and adds negations and all ordered pairs under AND, OR and XOR.

\[
N_0=5,\qquad N_{d+1}=2N_d+3N_d^2.
\]

Thus N1=85 and N2=21,845. These are list-entry counts; duplicate expressions at deeper
levels are not deduplicated and remain charged. The maximum candidate node count is
B0=1, B(d+1)=2B(d)+1. `bounded_grammar_complete` proves that every program with expression
height at most d occurs in the depth-d pool. The runtime limits d to 2; the formal
recursive definitions and theorems are not restricted to those two depths.

The correct replacement expression is not passed as a candidate argument. It arises
from grammar enumeration; the grammar and its operators are nevertheless supplied by
us. Discovering the Boolean identities themselves is not a novelty claim.

## 3. Bounded proposer contract

The incumbent begins as the reference. An examined candidate replaces it only if the
checker accepts and its node count is strictly smaller. Ties retain the earlier result.
For result p*:

\[
p^*\equiv r,\qquad |p^*|\le |r|.
\]

For every examined equivalent candidate p:

\[
p\equiv r\Longrightarrow |p^*|\le |p|.
\]

A changed result must have come from the generated examined pool. If the complete pool
is funded and the trial limit covers it, then p* is no larger than any equivalent
program of height at most d. This is optimality over the incumbent plus the examined
pool, not unrestricted global program optimality. A truncated prefix has only the
prefix guarantee.

### Generation and evaluation charges

The declared generation tariff is G0=5 and G(d+1)=G(d)+N(d+1). It counts a conservative
number of constructed pool entries, not complete CPU work. The pool is materialized
once even when only its prefix is tested. If its generation tariff cannot be funded,
no synthesis enumeration is performed and the reference is retained.

The protected per-candidate evaluation tariff is

\[
T(r,d)=8\bigl(|r|+B_d+1\bigr).
\]

This covers the two eager expression traversals and comparison across eight inputs
under the specified abstract convention. Real short circuits do not refund the tariff.
It omits ancillary enumeration, comparison, parsing, allocation and arithmetic costs.
If b is the search credit, the examined prefix length is

\[
k=\min\left\{N_d,\ell,\left\lfloor\frac{b-G_d}{T(r,d)}\right\rfloor\right\}
\]

when Gd<=b, and zero otherwise. Lean proves

\[
G_{\mathrm{spent}}+kT(r,d)\le b,\qquad k\le\ell.
\]

Source: `AVOC/BoundedSynthesis.lean`.

## 4. Generated ASTs instantiate the existing upgrade authority

The new authority is over `Program`, not the old three-version enumeration. Its
contract is exact equivalence to the frozen reference. For a declared replication
count M, utility is the integer -M*nodes(program), with exact lower and upper bounds.
The final independent gate check costs 8*(reference nodes+candidate nodes+1), switching
costs 1, and the strict margin is 1. Candidate JSON cannot supply its own scores or fees.

After synthesis, remaining campaign credit is total credit minus generation and trial
charges. The generated candidate is submitted using the inherited `DurableUpgrade.begin`
and `finish`, with actual proof terms establishing successful command replay and safety.
If final evaluation is unfunded the reference remains active. A search result is not
an admission by itself.

For the complete campaign:

\[
C_{\mathrm{search}}+C_{\mathrm{gate}}+C_{\mathrm{switch}}\le C_{\mathrm{total}},
\qquad p_{\mathrm{active}}\equiv r.
\]

The inherited endpoint bound includes all search charges. It does not imply every
campaign is profitable. The fixed objective string names the metric; the actual target
and M are fixed in the authority closure and protected job, not uniquely identified by
that string alone.

Source: `AVOC/SynthesisPromotion.lean`.

## 5. Exact checked examples

For r=NOT(NOT(x0) OR NOT(x1)), |r|=6. Depth one contains 85 candidates. The actual
synthesizer returns x0 AND x1 with three nodes. At M=10,000:

- generation: 90;
- all 85 candidate checks: 6,800;
- final promotion check: 80;
- switch: 1;
- total charge: 6,971;
- declared use benefit: 30,000;
- endpoint net: 23,029.

The generation result, promotion and net are kernel-checked concrete equalities. The
independent bitset oracle additionally reports two equivalent and 83 inequivalent
entries among the 85 examined.

With M=1 the exact same search and valid smaller candidate have net -6,968. This
negative-net equality is also kernel checked. A valid smaller deployed component and a
profitable improvement campaign are different properties.

For the three-flag reference NOT(NOT(x0) OR (NOT(x1) OR NOT(x2))), nodes decrease from
9 to 5. The actual demonstration tests 400 entries from a 21,845-entry generated pool,
charges 76,456 in total, and has net 323,544 at M=100,000. These numeric demonstration
results are executed and independently checked; the general semantic/budget guarantees
are proved separately.

Source: `AVOC/SynthesisExamples.lean`.

## 6. Link to the existing retry decision

Map the symbolic inputs to: positive planning horizon, enabled resources, and positive
immediate expected retry gain. Under the inherited `Retry.NoRevival` hypothesis, the
three-flag reference equals the complete retry evaluator's action decision. Composing
that theorem with synthesis soundness and promotion soundness proves:

\[
\operatorname{run}(p_{\mathrm{active}},\operatorname{flags}(m,n,s))
=\operatorname{Retry.choose}(m,n,s).
\]

This holds for every applicable model, state and horizon, not only tested probabilities.
It preserves the action, not the exact lookahead value report. It optimizes a redundant
Boolean formulation of an already-known threshold and is not claimed to improve the
already-specialized native threshold component. Costs of producing the three flags are
not counted as expression visits.

Source: `AVOC/SynthesisRetry.lean`.

## 7. Executed generation, durable dispatch, and replay

`tools/SynthesisMain.lean` executes the proved `search`, `campaign`, equivalence check
and inherited replay gate. The Python coordinator accepts only bounded AST data.
Before a new search, `run` persists a full credit-envelope reservation in a new protected
SQLite store. After the Lean process returns, one transaction publishes the checked
result, complete charge record and accepted AST. `invoke` replays the generated-program
journal and runs that AST through the fixed interpreter on all eight inputs.

Incomplete search has no certified result or active dispatch; its envelope remains
reserved. No automatic retry or refund is implemented. After a complete result, unused
credit is released according to the recorded charges. Reopening and invocation do not
rerun synthesis, but parsing/replay/checking still require computation.

This is a separate one-shot generated-program campaign, not an automatic migration or
integration with the prior live scientific proof stores. Stored AST execution is not
arbitrary source installation. The exact semantic gate is formally verified; Python,
serialization, physical snapshot origin, protected storage and SQLite remain trust
boundaries supported by the stated tests.

Source: `AVOC/SynthesisRuntime.lean`, `tools/synthesize_upgrade.py`.

## 8. Evidence and conclusion

The release contains 74 new named declarations and 1,310 total. Current compilation and
exact-name axiom reports cover the final local sources. Independent tests compare
747 campaigns, 255 equivalence queries, all eight executions in each campaign, ten
invalid wire requests and sixteen live-store scenarios. These are synthetic exact
workloads, not empirical LLM productivity evidence.

This closes a first bounded generated-candidate proposer with protected checking and
promotion. It does not close autonomous proposal discovery outside the grammar, efficient
general synthesis, multi-generation improvement of the proposer, or full physical-cost
optimization. The honest progression is generated programs instead of supplied complete
versions, not open-ended recursive intelligence.
