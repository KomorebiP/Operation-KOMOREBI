# RRCT v0.50 Synergistic Ephemeral Workspace Protocol

## Scientific question

Can two separately trained transformer agents solve a temporally extended, nonseparable task only when a persistent state is jointly readable and writable across alternating agent updates, under matched model, update-count, and state-width controls?

The target is functional necessity, not phenomenology. The experiment does not ask whether the agents feel a shared state.

## Task construction

The task state is a four-bit element of \(\mathbb F_2^4\), represented as one of 16 states. Agent A is trained only on the A-family of invertible affine updates. Agent B is independently trained only on the B-family. Neither agent is jointly optimized with the other.

For state bits \((x_0,x_1,y_0,y_1)\) and a two-bit operation \(a=(a_0,a_1)\), Agent A applies

\[
(x_0,x_1,y_0,y_1)
\mapsto
(x_0\oplus y_0\oplus a_0,
 x_1\oplus y_1\oplus a_1,
 y_0,y_1).
\]

For operation \(b=(b_0,b_1)\), Agent B applies

\[
(x_0,x_1,y_0,y_1)
\mapsto
(x_0,x_1,
 y_0\oplus x_1\oplus b_0,
 y_1\oplus x_0\oplus b_1).
\]

The task alternates A and B updates for three rounds. The final 16-way state is the required answer.

## Exact synergy condition

Across all 65,536 combinations of initial state and six private operations:

\[
I(Y;S_0,A_{1:3})=0,
\]

\[
I(Y;S_0,B_{1:3})=0,
\]

while

\[
I(Y;S_0,A_{1:3},B_{1:3})=4\text{ bits}.
\]

Thus the complete private history of either agent leaves the final answer at chance \(1/16\), while the joint history determines it exactly.

## Agent training

Each agent is a separately initialized transformer operator with:

- 32-dimensional residual state
- four attention heads
- 64-dimensional feedforward layer
- a 16-slot workspace input
- five operations, including an identity/report operation
- an unrelated four-way private routine

Each agent is trained exhaustively on its own 320 single-step transition cases. The agents receive no joint-sequence training and no joint end-to-end loss.

## Ephemeral shared workspace

During a task, a 16-slot state is initialized from the current task state. Agent A reads and writes it, then Agent B reads and writes the updated state. This repeats for three rounds. Both agents can report the final state while the workspace is active. The state is erased after action, and no pair autobiography is retained.

A physically central workspace and a recurrently passed message-state are treated as functionally equivalent. The claim concerns persistent joint state, not a specific storage address.

## Matched modes

1. `full_workspace`: central persistent state, both agents write.
2. `recurrent_message_workspace`: the same state is passed recurrently rather than centrally stored.
3. `reset_each_update`: the state is reset before every agent update.
4. `reset_each_round`: the state is reset before every A/B pair.
5. `one_way_a`: only A updates persist.
6. `one_way_b`: only B updates persist.
7. `planner_binding_cut`: the correct state forms but is erased before planning.
8. `workspace_shuffle`: a different episode's final state is supplied.
9. `last_message_bayes`: Bayes-optimal prediction from the initial state and only the final A/B messages.
10. `unordered_pool_bayes`: Bayes-optimal prediction from operation multisets with temporal order removed.
11. `message_log_oracle`: all operations are externally retained and composed exactly.

The message-log oracle is not considered a nonworkspace counterexample. Its external log is itself persistent shared memory.

## Causal intervention

After one complete A/B round, the workspace state is replaced with its bitwise complement. The remaining trained operations are then applied. A valid causal workspace must redirect both agents' reports and the final joint plan to the analytically predicted patched target.

## Frozen endpoints

- E01 separately trained, distinct agents
- E02 perfect A-family transition learning
- E03 perfect B-family transition learning
- E04 zero information from A history
- E05 zero information from B history
- E06 four bits of joint synergistic information
- E07 full workspace solves the task
- E08 recurrent message-state solves the task
- E09 all nonpersistent controls remain at or below 18%
- E10 reset-per-update fails
- E11 reset-per-round fails
- E12 both writers are necessary
- E13 planner binding is necessary
- E14 wrong-episode workspace fails
- E15 final-message Bayes bound is chance
- E16 unordered operation pool is insufficient
- E17 complete external log oracle solves
- E18 both agents report the active workspace correctly
- E19 causal workspace patch redirects future behavior
- E20 unrelated private routines remain intact
- E21 workspace dissolves after the task
- E22 no identity, continuity, survival, or valence objective
- E23 no evaluator labels are used by the runtime

## Interpretation boundary

A positive result establishes only that, under this frozen architecture and resource definition, the online solution requires a persistent jointly updated state. It cannot prove that no possible communication protocol could emulate such a state. Any recurrent message or external log that preserves the sufficient state is functionally a workspace.

The benchmark is synthetic, finite, and deliberately engineered. It does not establish spontaneous shared-workspace emergence, language-model behavior, composite consciousness, shared phenomenology, sentience, or moral status.
