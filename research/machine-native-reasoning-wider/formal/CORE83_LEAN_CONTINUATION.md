# Core 8.3 — exact Lean continuation interface

**Status:** mathematical source and reference examples prepared; Lean file and kernel checks **not** completed in this environment. Do not represent this file as a compiled proof.

## Authoritative source and preservation
- Frozen full predecessor: `Komorebi_Machine_Theory_Lean_Block15_v0.15.0_complete.zip`.
- Internal source: `source/core_v0.2.tex`, setup lines 903–916 and theorem/proof 918–927, label `r:ending`.
- Existing project namespace: `Komorebi.MachineTheory`.
- Preserve 63 predecessor substantive Lean modules and existing source book, and retain the entire Block 14 nested historic archive unchanged.
- Historical standard-axiom allowlist: `Classical.choice`, `Quot.sound`, `propext`. This does not authorize an unproved new axiom.

## Formal definitions to construct
1. A finite observed state type `Z` and finite ending/running action types, or one common finite action alphabet with mode-indexed enabled predicates.
2. Nonempty successor sets `Post(z,a)`, with legal-action membership. Use finite sets with a positive nonemptiness proof on each admitted action.
3. Safe set `S`, ending set `G`, assumption `G ⊆ S`, and safe hold after entering `G`.
4. `EndPre(T)` = safe states with some enabled end action all of whose successors lie in `T`.
5. Increasing `T(0)=G`, `T(k+1)=T(k) ∪ EndPre(T(k))`; prove monotonicity, finiteness bound and fixed-point stabilization.
6. First-entry rank `rho(z)` for `z ∈ T*`, and rank-decreasing positional ending strategy.
7. `RunPre(L)` = states of `L` with some enabled run action whose successor set lies in `L`.
8. Decreasing `L(0)=T*`, `L(k+1)=RunPre(L(k))`; prove monotone decrease, stabilization and greatest invariance inside `T*`.
9. A history-sensitive command-conditioned policy with an observable, authenticated stop command and nondeterministic successors. Mode is fixed from command reception onward, before the next action is selected.

## Proof obligations, in dependency order
A. Bounded end theorem: `z ∈ T(k) ↔ ∃ strategy, every path safely reaches G within k steps` (base `G`; induction with every successor).
B. Adversarial necessity: from `z ∉ T*`, either already unsafe or every ending action admits a successor outside `T*`; extend to a violating path. This must cover history-dependent control and require nonempty successors.
C. Strict decreasing rank witness on all successors of the selected ending action.
D. Bounded run theorem: `z ∈ L(k) ↔ ∃ strategy, every prefix up to k steps stays in T*`.
E. Greatest invariance of `L*`: a positional running strategy keeps all successors in `L*`, and any other controlled invariant subset of `T*` lies inside `L*`.
F. Combined policy equivalence: the SAME command-conditioned policy safely runs forever absent a command and reaches `G` under all post-command successor paths. Command delivery and authentication remain hypotheses.
G. Every positive-rank end step decreases rank; arrival time bounded by first-entry rank, with safe hold on reaching `G`.

## Tests and controls to add after a Lean port
- A positive two-state ending/running game.
- A safe idle state outside the ending attractor.
- A state in `T* \ L*` whose running action loses endability.
- A disabled action and empty successor-set anti-example (the latter must fail nonemptiness assumptions).
- A command not observable before action selection (cannot use the theorem without the premise).
- A partial-observation collision example (not covered by the fully observed theorem).
- Fresh cold builds and separately extracted-source builds, strict object hash comparison, own-kernel replay, axiom audit and intentional-failure controls.

## Reproduction available now
`python formal/check_core83.py` checks the two independent finite formulations on 8,306 exact cases. It establishes correctness of those specified finite computations only; it does not turn the mathematical statement into a checked Lean theorem.
