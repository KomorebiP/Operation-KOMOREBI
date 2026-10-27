# Continue from v0.33

Read README.md, RESEARCH_BOUNDARY.md and RESULT.json. Preserve exact parent SHA-256 636a99685b1da21d8f4a1ec9c046293194e8a7d3563474bb73487cccf43f88e7.

The principal new statement is `SimultaneousNorm.primePower_localization_iff_pivot`; the mixed unipotent statement is `SimultaneousNorm.unipotent_localization_iff_pivot`. They are integrated with the actual norm matching class in SimultaneousFrobeniusCriterion.lean and continuous local-gauge class in ContinuousSimultaneousNormCapstone.lean.

Do not solve restrictions separately and call that simultaneous. Do not apply the mixed primary criterion without its nilpotence and nonzero scalar hypotheses. Do not infer a coefficient tower or global automorphic statement.

The strongest next distinct task is automatic mixed-characteristic matrix-kernel coordinates, then actual layer-by-layer compatibility. The relevant obstruction is now explicitly computable at a supplied layer.

Replay in bounded batches using verify.py --kit PATH --max-modules 8, then --resume. Every module must return zero and the all-constant axiom audit must pass. Run checks/exact_simultaneous_checks.py. Prove any claimed new criterion and include a negative control when weakening an old hypothesis.
