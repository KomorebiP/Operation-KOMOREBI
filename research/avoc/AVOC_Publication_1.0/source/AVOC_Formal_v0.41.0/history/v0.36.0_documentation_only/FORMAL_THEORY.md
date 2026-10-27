# AVOC v0.36.0 — staged proof-carrying affine operations

## 1. Objective

Earlier affine controllers treated a checked warm-cache plan or cold-generated plan as an
immediately available terminal choice.  This block inserts the missing operational stages:

\[
\text{inspect and validate cache}\to\text{warm plan ready}\to\text{deploy},
\]

\[
\text{generate and validate candidate}\to\text{cold plan ready}\to\text{deploy}.
\]

The setup operations are paid, may fail, and do not themselves produce deployment benefit.

## 2. Proof-carrying options

A staged option contains a `Deployment`, its exact source and kind proofs, and a declared
success probability in `[0,1]`.  The deployment proves

\[
\forall x,\quad d_{\rm selected}(x)=d_{\rm source}(x)
\]

and

\[
C(d_{\rm selected})\le C(d_{\rm source}).
\]

For `N` declared calls, gross execution saving is

\[
G(d,N)=N\left(C(d_{\rm source})-C(d_{\rm selected})\right).
\]

The operational fee is the deployment setup charge.  Lean proves

\[
-\operatorname{setup}(d)+G(d,N)=\operatorname{payoff}(d,N).
\]

Thus splitting setup and deployment into two actions preserves the inherited net-payoff
semantics on a successful path.

## 3. Controller state and actions

The state contains warm/cold status, remaining operational budget, accumulated spend, the
frozen total envelope, and a halt flag.  Each option is in one of

\[
\{\text{untried},\text{failed},\text{ready}\}.
\]

Actions are

\[
\{\text{stop},\text{inspectWarm},\text{generateCold},
  \text{deployWarm},\text{deployCold}\}.
\]

A setup action is available only when its option is untried and its fee fits the remaining
budget.  A deployment action is unavailable until its corresponding status is `ready`.

The setup observation is Boolean.  Its declared success probability is the staged option's
probability; failure has complementary probability.  Both branches pay the setup fee.

## 4. Exact finite-horizon control

The executable action enumeration, Boolean observation distribution, transition, and reward
functions realize the inherited state-dependent guarded Bellman system exactly.  Therefore

\[
\boxed{\operatorname{Evaluate}(h,s).\operatorname{score}=V_h(s).}
\]

For positive depth its chosen action is feasible and Bellman-optimal.  The inherited
complete-plan theorem gives a legal deterministic adaptive observation tree attaining the
finite-horizon optimum and dominating every legal competitor of the same horizon.

## 5. Budget invariant

Define

\[
\operatorname{BudgetSafe}_B(s)\iff s.\operatorname{budget}+s.\operatorname{spent}=B.
\]

For every allowed action and every Boolean observation branch,

\[
\boxed{
\operatorname{BudgetSafe}_B(s)
\Longrightarrow
\operatorname{BudgetSafe}_B(\operatorname{step}(s,a,o)).
}
\]

The optimal adaptive plan therefore preserves the envelope on every branch, including
zero-probability branches.

## 6. Operational acknowledgement

Operational outcomes are typed as either an actual Boolean report or a fault.  Faults do not
become model observations.  A report advances the state only when the action is currently
available and the report has positive probability in the declared model.

Successful warm/cold reports produce `ready` states.  A ready state exposes the model's
proof-carrying deployment; deployment still cannot bypass its action guard.

## 7. Checked example

The example uses the inherited exact rank-one implementation over `ZMod 5`:

- original per-call tariff: `36`;
- selected per-call tariff: `21`;
- 1,000 declared calls;
- warm setup: `133`;
- cold setup: `196`.

Hence gross saving is `15,000`, warm net is `14,867`, and cold net is `14,804`.

The executed evaluator returns:

| State/model | Horizon | Choice | Continuation value |
|---|---:|---|---:|
| certain warm and cold success | 1 | stop | 0 |
| certain warm and cold success | 2 | inspect warm | 14,867 |
| warm success probability 1/2; cold certain | 2 | generate cold | 14,804 |
| after successful warm inspection | 1 | deploy warm | 15,000 |
| budget 132 | 3 | stop | 0 |

The `15,000` continuation after warm success excludes the already-paid `133`; the complete
path value is `14,867`.

## 8. Executable boundary

The JSON entrypoint constructs proof-carrying warm and cold options by validating both
certificates before running the in-memory staged planner.  Their *logical* setup fees are
inside Bellman control, but physical validator startup and this eager model construction are
outside it.

Consequently this release proves the staged decision theory and executes it on checked
options.  It does not yet provide a lazy filesystem process where the planner invokes only
the selected validator operation and then resumes from its actual checked report.
