# Block 02 — mathematical route through the proofs

**Source book:** *Machine-Native Reasoning: Evidence, Methods, and Accountable Revision*, Reviewed Core 0.2. The source result numbers below belong to that unchanged book.

## 1. Static reporting sufficiency (Core 3.4)

There are three different objects: a fixed candidate model `m`, a raw observation `o`, and the stored report `z`. The reporting channel is specified by `B(o,z)`, not by `B(m,o,z)`. Its conditional independence is a typed part of the model, rather than a conclusion learned from an example.

The relevant law is

\[
J_m(o,z)=L_m(o)B(o,z),\qquad Q_m(z)=\sum_o J_m(o,z).
\]

For prior `p`, `weights p l` is the unnormalized vector `l(m)p(m)`. `evidence p l` is its mass and `update p l` is its algebraic normalization. Statements that call it a posterior always restrict to positive-probability events. `Instrument.posterior?` makes the impossible-event boundary explicit with `none`.

For a positive pair, conditioning on `(o,z)` gives the same model posterior as conditioning on `o` because the common reporting channel's factor cancels. Suppose exact equality with the posterior after `z` holds for one full-support prior. Define

\[
\rho(o\mid z)=\frac{\sum_m p(m)J_m(o,z)}{\sum_m p(m)Q_m(z)}
\]

when the denominator is positive. Summing over `o` proves a normalized row. Equality of the posteriors and positivity of each `p(m)` then give `J_m(o,z)=Q_m(z)rho(o|z)`.

Zero pairs require a different argument: nonnegative terms in a zero-mass sum are zero, and full prior support transfers that zero to each model's likelihood. If the entire `z` column is impossible, any normalized row is a valid reverse row because both sides of the factorization vanish. The implementation chooses the uniform row on the nonempty raw-observation type. This does not construct an invented posterior on `z`.

Conversely, such a factorization gives a model-independent factor that cancels under any prior on every positive pair. This proves the all-prior direction. A finite nonempty model type has an explicit uniform full-support prior, closing the existential equivalence.

**Endpoints:** `ReportingModel.all_iff_full_support_prior`, `all_iff_exists_full_support`, `all_iff_reconstruction`. The separate construction is `reconstruction` and its verification is `reconstructs_of_full_support`.

## 2. Why Bayesian closure forces a likelihood split

A partition can be represented by a surjection `pi : X -> Z`. Suppose a positive likelihood `l` has a fixed positive coarse counterpart reproducing the aggregated posterior for every fine prior. Two states `x,y` in one retained block must have equal likelihoods when a second retained block exists.

Choose `z` in a different block and compare the two priors `(delta_x+delta_z)/2` and `(delta_y+delta_z)/2`. Their coarse priors are equal. Their coarse posteriors must therefore be equal. Looking at the first block gives

\[
\frac{l(x)}{l(x)+l(z)}=\frac{l(y)}{l(y)+l(z)}.
\]

Strict positivity makes the denominators and `l(z)` nonzero, so cross multiplication yields `l(x)=l(y)`. No numerical approximation is involved. With only one block there is no comparison block. `one_block_still_corrects` demonstrates the resulting failure of the necessity claim under that weakened premise.

For sufficiency, a likelihood constant on every fibre factors as `l=g∘pi`. Finite summation then preserves both the unnormalized numerator and its mass. Normalization commutes. Coarse likelihoods are only required to reproduce each separately specified positive update. They need not be uniquely determined because multiplying one likelihood by a positive scalar leaves its Bayesian update unchanged.

**Endpoint:** `BayesianLumping.fixed_positive_coarse_iff`.

## 3. The actual least refinement (Core 3.5)

A `Setoid X` is a partition. The order `P <= Q` means P is **finer** than Q, since any pair equivalent under P is equivalent under Q. This order direction matters in the coarseness statement.

Start with

\[
I=P_0\cap\ker(x\mapsto(l_o(x))_o).
\]

The next partition retains the current relation and equates two states only when all their probabilities of reaching each current block agree. `step_rel_iff` verifies that the quotient-based code is exactly the manuscript's displayed finite block-sum construction, with current state representatives naming the blocks.

Every strict step increases the number of blocks. `blockCount_strict` proves this using the surjective quotient map from a finer partition to a coarser one: if the partitions are distinct, that map cannot be injective. A partition has at most `card X` blocks. Thus `bounded_stabilization` proves a stable index at most

\[
|X|-|X/I|.
\]

`stopIndex` selects the first index satisfying the bounded fixed-point predicate. `terminal` is the actual partition at that index. The theorem does not assume a terminal partition exists as input.

At stability, the successor-block sums are well-defined normalized stochastic transition columns. `stable_iff_prediction` obtains the actual coarse law from Block 01's `Instrument.quotient_exists_iff`, using one trivial report for a plain state transition. Initial splitting keeps all likelihoods constant in terminal blocks, so positive coarse likelihoods also exist.

To prove leastness, take any operationally admissible refinement Q of the mandatory partition. Bayesian necessity forces Q to refine I. If Q refines a current partition, every current block is a union of Q blocks, so Q's exact prediction implies equality of masses into each current block. Q therefore refines the next partition. Induction proves Q refines the terminal partition. Antisymmetry proves uniqueness of the partition, not of arbitrary block labels.

**Endpoints:** `Refinement.admissible_iff`, `bounded_stabilization`, `least_prediction_correction_refinement`.

## 4. A finite witness for backward propagation

Encode states 0,1,2,3 by pairs of Boolean bits. The deterministic successors are `(0,2,3,3)`, and the mandatory partition is `{0,1,2}|{3}`. The likelihood is constant one, so correction adds no distinctions.

The first transition split is `{0,1}|{2}|{3}`: state 2 reaches the protected block in one step. The second split separates 0 from 1: state 1 reaches 2 while state 0 stays at 0. The discrete partition is stable. The module proves both strict changes and that every operationally admissible refinement is discrete. This is a future-prediction distinction, not a newly obtained measurement.

## 5. How this advances the book's formal dependency chain

Block 01 establishes a quotient's exact joint report/state and feedback laws once the relevant fibre condition is supplied. Block 02 characterizes information-preserving reporting and constructs the least partition closed under a specified family of separate predictions and corrections. These conditions are not interchangeable. Preserving a selected combined schedule can require fewer distinctions than preserving each operation independently.

The next source result, compressed-belief planning (5.4), adds matched actions, costs, terminal losses, and finite-horizon choices. None of those optimization conclusions is silently inferred from the present filtering result. Its formalization remains a separate block.
