# v0.6 access repair: development contract before new training

Question: Can copied, phase-local cue/message parameters learn native access to
retained joint information while the entire previously trained observation,
working-operation, silent-update and answer machinery remains unchanged?

Parents: v0.5 A_random and B_random checkpoints. These are two previously
competent initialization lineages with different ancestral training budgets,
not an untouched cohort or from-scratch replication.

Architecture: base v0.5 plus copied cue-phase modules for each agent. Copied
modules act on each agent's own 64-vector and the same receiver-only eight-value
message wire. They share neither weights nor raw hidden state between agents.
No extra persistent state, semantic axes, central reader, probe targets or
hidden-state targets. Original frozen answer and private heads read the results
in the access-only arm. A supplied control flow identifies retrieval vs working
phases. This is explicit architectural scaffolding, not spontaneous routing.

Arms per parent, same total architecture and forward schedule:
- access: only copied cue/input/route/observation/send/receive modules train.
- joint: copied modules and all original modules train, with the same losses.

Both receive 1000 updates, batch96, AdamW restart lr0.0003, weight decay0.00001,
gradient norm cap1, one Torch/BLAS thread per process. The final checkpoint is
primary within this development run, never the best intermediate checkpoint.
All forward calls and episode presentations are matched. Backward work differs
because original parameters are frozen in the access arm; not equal wall time.

Training: one original encode/cue/working program followed by two successive
retrieval stages on each of four independent branches covering all eight facts.
The second retrieval repeats the first cue or changes it. Correct late answers
and private labels are the only objectives. Query types/arguments do not enter
state formation. Verification proposals are generated after targets are fixed.
Work loss weight1, first+second retrieval loss averaged with weight1, private
cross entropy included at0.2. No semantic labels enter forward state formation.

Program families selected by batch: random nonidentity, inverse palindrome,
identity tokens, and flip involution. Lengths0,3,6,12,24. The full named
commuting-flip and swap-conjugation generators are excluded from training;
short incidental strings can occur randomly. Lengths48 and96 are untrained.
Worlds and aliases are not withheld (all256 worlds, two aliases in training).

Evaluation: same banks for all models and arms, no discovery based on scores.
First evaluate parent, access, joint on all four training-family types plus
commuting-flip and swap-conjugation words at0,3,6,12,24,48,96 as applicable.
Report exact current work, all four consumers, all-eight factual reconstruction,
private recall, post-repair short working reuse, retrieval-depth and message cuts.
Projected-state edits are not used. Whole native working twins and nontrivial
same-value program shams are allowed for an additional functional assay, not
localized-space certification. Previous support/no-wire/reciprocity gaps remain.

Conditional interpretation: access improvement with the base tensors and
pre-retrieval trajectories byte-exact isolates a change in the retrieval process,
not improved encoding during that frozen prefix. Access success need not imply
compatibility with later working transitions; that is measured separately.
Joint improvement alone may reflect changed stored information as well as access.
All score thresholds and absent tests remain explicit. A complete process is
not automatically a scientific pass. No J-space or subjective-state certification.
