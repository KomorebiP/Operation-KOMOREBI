# Metadata correction without changing outcomes

The inherited main evaluator's `untrained_length` flag uses L>24 for all models.
That is correct for the new main children but not the v0.5 parent (trained max12).
Parent results at length24 are therefore extrapolation, despite that raw flag.
The raw main records are retained. The new-history confirmation uses the proper
maxima: parent12, main24, calibrated48. The consolidated report and JSON carry
explicit training bounds. No prediction, threshold, training run or score changed.

The `depth` parameter applies to factual-recall branches. Downstream working
reuse always starts from one newly retrieved cue; reuse entries repeated across
depth cells are not tests of working reuse after that many repetitions.
