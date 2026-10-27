# AVOC v0.26.0 — semantic representatives as reusable synthesis state

## 1. Exact semantic identity

The inherited pure language has constants, three variables, negation, conjunction, disjunction, and exclusive-or. For a program p define

\[
\sigma(p)=(\operatorname{run}(p,x))_{x\in\{0,1\}^3}.
\]

The ordered list contains all eight possible inputs. Lean proves

\[
\sigma(p)=\sigma(q)\iff\forall x,\operatorname{run}(p,x)=\operatorname{run}(q,x).
\]

Equal node counts or equality on a single input are not adequate substitutes. Checked counterexamples reject both shortcuts.

`Entry` contains an AST, cached eight-bit signature, cached node count, and proofs that both caches agree with the AST. These proof-carrying entries are constructed within Lean. They are not an assertion that an arbitrary external cache file is trusted.

## 2. A minimum representative per behavior

`insert` scans the semantic index. A matching signature keeps the smaller program, with stable incumbent-preserving ties. An unmatched signature adds an entry. `compact` builds such an index over an emitted list.

For every candidate p in that list, the output has q with

\[
q\equiv p,\qquad |q|\le|p|.
\]

Every retained q originates in the input list. Signatures are unique. There are at most

\[
2^8=256
\]

entries. This bounds the number of retained semantic representatives, not their total AST bytes or peak temporary allocation.

## 3. Feedback into the next grammar layer

Let P_d be the original grammar pool and E its expansion operation:

\[
P_0=\mathrm{atoms},\qquad P_{d+1}=E(P_d).
\]

The new library sequence is

\[
B_0=\operatorname{compact}(\mathrm{atoms}),\qquad
B_{d+1}=\operatorname{compact}(E(\operatorname{codes}(B_d))).
\]

The retained entries, not the entire previous raw list, become the operands for the next search layer.

The main pair of theorems is

\[
\forall p\in P_d,\;\exists q\in B_d:\ q\equiv p\land|q|\le|p|,
\]

and

\[
\operatorname{codes}(B_d)\subseteq P_d.
\]

The induction uses semantic congruence of every constructor and monotonicity of the additive node cost under replacement of children. A retained equivalent child therefore cannot worsen the parent construction.

For any reference r, query selection starts with r as an incumbent. Lean proves

\[
\left|\operatorname{select}(r,r,\operatorname{codes}(B_d))\right|
=
\left|\operatorname{select}(r,r,P_d)\right|.
\]

Both outputs are equivalent to r. This is equality of optimum node count, not necessarily of expression syntax on ties. The result holds at every natural depth in the formal model, not only at tested depths. Runtime limits separately bound executable requests.

Earlier knowledge is not lost: each representative at one depth is covered by an equivalent no-larger representative at the next. Minimum cost may improve as depth increases. Reaching every truth function does not prove that every representative is already globally smallest over unlimited depth.

## 4. Executed work and preflight budget

`insertMeasured` and `collectMeasured` execute the same index construction while counting index entries probed. Proofs connect their returned entries to the simpler specification. A candidate probes at most 256 entries when the incoming index is unique.

The structural tariff is

\[
C=E+10M+9P,
\]

where E counts emitted entries, M is their total AST node mass, and P counts index probes. The coefficient 10 prices eight semantic traversals and two size traversals. Nine is a conservative charge for signature/size comparison at each probe. This is not a full interpreter-instruction, CPU, memory, or wall-clock model.

For a prospective layer containing N candidates of at most m nodes each, the declared reservation is

\[
R(N,m)=N+10Nm+9\cdot256N.
\]

The executed charge is proved at most this reservation. The budgeted search checks reservation availability before generating the layer. Every returned `PaidRun` carries

\[
\mathrm{spent}+\mathrm{remaining}=\mathrm{initial\ credit}.
\]

Its bank has the exact optimum and coverage guarantees for the **attained** depth. An unaffordable requested next layer is not reported as completed. Reservation conservatism can stop a layer that its eventual actual charge would have afforded; depth allocation is not claimed optimal.

## 5. Query and promotion integration

The bank can answer multiple references without regenerating the grammar. Queries are rechecked against the full eight-input semantics. The declared query fee is

\[
C_q(r,B)=\sum_{e\in B}8(|r|+e.\mathrm{size}+1).
\]

For a funded query, this fee is removed before the inherited generated-program authority receives promotion credit. The existing contract check and utility criterion remain unchanged.

The theorem `bank_submission_total_cost` establishes

\[
C_{\mathrm{search}}+C_q+C_{\mathrm{evaluation}}+C_{\mathrm{switch}}
\le C_{\mathrm{total}}.
\]

`bank_submission_semantics` preserves the reference semantics of the active component; `bank_submission_replay` connects to the old in-memory prepaid journal. The new CLI does not persist this bank or deploy native code. Search modes report diagnostic query fees separately; the `campaign` mode includes its one selected query in the campaign envelope.

## 6. Controlled comparison

The two arms use the same atoms, operators, evaluator, exact semantic index, stable tie rule, and structural tariff. The frozen arm generates the next level from all preceding raw candidates. The feedback arm uses the retained semantic representatives. This isolates that feedback connection; it is not a comparison with the best available synthesis algorithm or with every implementation of the older target-specific search.

At depth 2:

| Quantity | Frozen | Feedback |
|---|---:|---:|
| New layer candidates | 21,845 | 901 |
| Cumulative emitted entries | 21,935 | 991 |
| Retained behaviors | 109 | 109 |
| Cumulative node mass | 144,885 | 5,081 |
| Index probes | 306,154 | 26,870 |
| Declared structural charge | 4,226,171 | 293,631 |

The frozen and feedback optima agree for all 256 query functions rendered in fixed DNF at each matched depth. The reduced depth-2 structural charge is about 14.4-fold. It is not a claimed 14.4-fold physical speedup.

Three process-inclusive timed executions per arm at depth 2 had medians 1.762 seconds (frozen) and 0.997 seconds (feedback) on this host. These small-sample timings include Lean startup and output; they are descriptive, not a robust or portable performance claim.

The executed feedback depth-3 build retains all 256 behaviors with 36,852 cumulative emitted entries. Frozen depth 3 was not executed. The formula predicts its raw final-layer size to be 1,431,655,765; that is an arithmetic size calculation, not an execution measurement.

## 7. Concrete promotion

For the six-node reference `not(or(not(x0),not(x1)))`, the depth-2 library returns the three-node `and(x0,x1)`. The executed campaign uses:

- search charge 293,631;
- query charge 10,520;
- final promotion evaluation 80;
- switching charge 1;
- total charge 304,232.

With one million **declared** future calls, the modeled endpoint gain is 3,000,000 - 304,232 = 2,695,768. Future calls are a chosen workload, not observed demand; the charges are structural tariffs. Known Boolean simplification and positive illustrative net value are not novel discovery or real LLM effectiveness claims.

## 8. Meaning for recursive improvement

The next generation of candidates is changed by the automatically retained results of the previous generation. This is a proved and executed feedback mechanism in the synthesizer's state. The checker and improvement algorithm remain fixed, and no model weights or source code edit themselves. The stronger claim that an improved improver autonomously produces further generally useful improvements is not established.
