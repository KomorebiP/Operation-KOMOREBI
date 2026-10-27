# Research route record

Base: v12, SHA256 508aa1d65b7591b94fc638e6fccb2541f1b42e2778826d97eb07fc52d42e6b70.
Goal: implement one genuine packet-selective computation policy with progress and
an actual posterior-certified return, building on v12's output contract.

1. Update a single output/input block and assume all other blocks stay fixed.
   Rejected. Right multiplication by S couples input packets. The explicit
   right-packet-growth counterexample is checked in AdaptivePacketBoundary.
2. Select an output packet but apply the innovation transition across its entire
   input space. Chosen: left orthogonality preserves all other output packets.
   Maximum-energy selection and complete accounting give a geometric global rate.
3. Round the selective updates using the inherited full-update precision policy.
   Deferred: the old proof tracks full Richardson iterates; it does not establish
   the new state-dependent selection dynamics. A separate perturbation analysis
   must account for rounding in updates and, if used, approximate packet selection.
4. Prove only a local descent lemma. Insufficient for this block's goal. Completed
   the executable scan, finite fuel, early stopping, rounded verifier, gain origin,
   posterior-law guarantee, and v12 parameter-output integration as one program.

Outcome: CLOSED_CHECKED within the exact-packet-update/fixed-geometry contract.
No performance or global novelty conclusion is drawn. Dense scanning and full
certificate evaluation may erase computational savings from selective updates.

Next useful bounded block: rigorous cached residual/packet-score maintenance or
rounded selective updates with an explicit selection-error contract. Then compare
total computation and verification cost with the retained full-update solver.
Hierarchy-changing refinement is a distinct stronger extension.
