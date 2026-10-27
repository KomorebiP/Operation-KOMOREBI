# Why changing two outputs is not the same as reciprocal communication

Let h_1,h_2 be local states and m_i=S_i(h_i) their learned messages. The receiving
transition is h_i'=F_i(h_i,m_j). The model architecture supplies this interface;
its numerical content is learned in the inherited checkpoints.

An initial edit I of h_1 alone does not directly modify h_2. The first causal path
is I(h_1) → S_1(I(h_1)) → F_2(h_2,S_1(I(h_1))) → the unchanged readout.
Replacing that packet by S_1(h_1) restores the exact factual recipient transition.
Inserting S_1(I(h_1)) into a fully unedited pair reproduces the recipient's first
changed transition. No semantic decoder or truth label is needed for these
identities. They follow from deterministic equality of inputs.

This path identity does not prove a workspace. The additional experimental
obligations include the intended counterfactual answer, suitable time and direction,
other-task preservation, persistence after feedback, and representational support.
Later trajectories can differ because the writer states and feedback paths differ.

The observed direction/lineage asymmetry is a reason not to identify independent
bilateral edits with a globally authoritative shared variable. A good two-agent
readout can exist without an equally reliable two-way write protocol. Present
results instrument that gap; they do not repair it by assumption.
