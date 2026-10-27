# Core 8.3 — source and proof correspondence

## Input contract

`Model Z A` has finite safe and goal sets, `goal ⊆ safe`, finite running and ending action catalogues at each observed state, and the actual finite successor set for each state/action pair. Every enabled action has at least one successor. The source-facing theorem assumes `Fintype Z`; the action universe need not be globally finite because each supplied catalogue already is finite. Empty state types remain admissible. An empty action catalogue is a real deadlock.

`endStep` is precisely `U ∪ {x ∈ safe | ∃ a ∈ finish x, post x a ⊆ U}`. `endStage` starts at the goal. `runStep` is precisely `{x ∈ U | ∃ a ∈ run x, post x a ⊆ U}`. `runStage` starts at the computed ending region. These are definitions on the supplied system, not hypotheses that a winning region exists.

## Fixed points and ranks

`FiniteFixedPoints.increasing_stabilization` proves an inflationary finite-set sequence becomes fixed within the number of initially missing states. `decreasing_stabilization` bounds a deflationary sequence by the size of its initial set. The proof uses strict cardinality changes, not a timeout or an experimentally observed convergence. `fixed_tail` proves permanence of a fixed point.

`ending_stabilizes` and `running_stabilizes` instantiate these results. `endRank` is the least stage containing a state in the ending region. The outside value zero is never used as a certificate of ending. `endRank_spec`, `endRank_min`, and `endRank_zero_iff` prove the first-entry meaning. `rank_action` produces one action whose every successor has smaller rank.

## Policy semantics

A `Config` consists of the previous state/action pairs and the current observed state. A `Strategy` maps that configuration to an optional action. `edge` requires the selected action to be in the actual catalogue, the next history to include that same selected action, and the next state to belong to the supplied successor set. The action is selected before the adversarial successor.

`EndingGuarantee` requires safety and a legal action at every reachable non-goal prefix and excludes an infinite legal non-goal execution. Neither requirement alone is enough. The deadlock example has no infinite execution, but fails the local legal-action obligation. `ending_prefix_extends` uses nonempty successor sets to show every non-goal winning prefix really can advance.

`PolicyInput` has a running branch and an ending branch with the configuration at the command epoch and the complete subsequent history. One policy function receives this input before it selects its next action. `SwitchingGuarantee` requires safe legal running at every no-command prefix and the ending guarantee after a command at any such prefix. Therefore the necessary direction includes arbitrary history-dependent policies, not only memoryless policies. The authentication and delivery of a real-world command are not proved by this formal input type.

## Necessity and sufficiency

For sufficiency, the ending action is selected from the rank-decreasing witness and the running action from the viability fixed point. Every legal ending step decreases rank, every running step stays in the running region, and every reachable command epoch remains inside the ending region. `running_has_infinite_path` constructs actual no-command execution, excluding vacuous success.

For necessity outside the ending region, `outside_successor` produces a successor still outside after the strategy has selected its action. Starting from a presumed history-dependent winning strategy, `guarantee_mem_ending` recursively constructs a legal infinite non-ending path. Its contradiction proves ending-region membership without imposing a time bound on arbitrary winning policies.

For necessity in the running phase, the set of states occurring in histories reachable under the given policy is contained in the ending region. It has at least one running action whose entire successor set remains in that reachable set. `running_maximal` places it in the actual decreasing fixed point. No action is chosen after observing its successor.

`safe_continuation_iff` is the exact region/one-policy equivalence. `source_core83` packages that equivalence together with the same constructed policy's universal rank budget. `command_rank_arrival` gives the first-entry-rank arrival statement at every reachable command epoch. These proofs do not assume the desired region/policy equivalence as a field.

## First arrival and the manuscript hold action

The source permits a safe hold action at the goal. This development stops the ending specification at first goal arrival and does not need that additional premise. It therefore applies to the source setting and also to settings without post-goal continuation. It does not establish arbitrary post-goal safety. The printed manuscript is unchanged, and this difference is a recorded strengthening rather than a silently omitted assumption.

## Checked examples

A three-state system has goal 0, stop-capable state 1, and safely idling trap 2. Its ending region is `{0,1}` and its running region is `{0}`. State 1 can stop immediately but loses that option by running once; state 2 can run indefinitely but cannot end. A separate system shows deadlock is neither successful running nor successful ending. A Boolean quantifier example detects hindsight-dependent selection. Finally, a history-dependent policy waits once and then ends although the state's minimum rank is one. The rank bound belongs to the constructed policy, not to every winning policy.

## Admission and exclusions

Current-source final/fresh gates, source API checks, complete project axiom audits, own-kernel replays, all 161 control contracts, upstream object hashes, and byte-identical production objects determine admission. No proof placeholder, custom production axiom, or native-decision proof shortcut is introduced. The three earlier unformalized targets remain pending. The monograph's wider integration chapters and the Large Signal Model denominator are not enlarged by this result.
