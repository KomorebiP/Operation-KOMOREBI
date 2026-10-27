# Continue the checked formalization

Formalize **Core 8.3**, safe continuation that retains an ending strategy, from `source/core_v0.2.tex:918–927`, retaining the setup at 903–916.

Use a finite observed configuration space Z with finite running and ending action catalogues and nonempty successor sets for every admitted action. Keep the declared safe set S, target G⊆S and safe hold at G explicit. The stop command is authentic and observable before selecting the next action. This delivery/authentication premise is not proved by the fixed-point calculation.

Construct T₀=G and Tₖ₊₁=Tₖ∪{safe states with an ending action whose every successor lies in Tₖ}. Prove stabilization and characterize the sure-ending region, including a first-entry rank and its strict decrease under the chosen ending action. Then construct L₀=T* and Lₖ₊₁={states in Lₖ with a running action whose every successor remains in Lₖ}. Prove stabilization and the greatest safe-running invariant inside T*.

Prove the exact equivalence for one policy: indefinitely safe running without a stop command, and sure arrival at G after a command at any decision epoch using only ending actions. The policy may switch modes when the observable command arrives. Before the command preserve L*; afterwards follow decreasing ending rank. Necessity must handle arbitrary permitted policies, including history dependence if admitted by the policy definition. Every possible successor path is quantified; no action may depend on secretly seeing its successor first. Do not substitute two unrelated existential policies for the source's combined guarantee.

Finite fully observed configurations are the stated scope. Partial observation would need justified public possibility states and is not included automatically. Preserve nonempty successor sets to prevent vacuous sure-transition guarantees. Preserve the distinction between safety alone and continued availability of an ending strategy.

After 8.3, earlier source results 2.4, 2.5 and 3.2 remain deferred. Current 23/27 is a selected-source tally, not a complete-book claim or effort estimate. Verify the frozen package before editing and preserve all 63 substantive modules from Block 15.
