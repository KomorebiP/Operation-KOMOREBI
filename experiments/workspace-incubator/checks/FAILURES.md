# Failures, limitations, and repairs retained in v0.6

## Scientific failures

- Main access-only max24 training only partially improves held-out swap-conjugation48.
- Main joint training improves A more but degrades B private recall under the long
  stress. A memory gain is not a complete functional pass when another task regresses.
- The additional known-stress calibration exposes length48 and the previously
  held-out generators. It is not untrained-family or untrained-length evidence.
- Even after calibration, recall remains imperfect and length96 severely fails.
- Calibration harms some unstressed repeated/sequential retrieval conditions.
  More reliable one-shot retrieval is not a memory-preserving retraction.
- Repeated cue applications beyond the trained two stages often compound failure.
- Working-state reuse after repaired access is strong in bounded three-operation
  tests, but not perfect, and all-eight recall afterward remains weaker.
- No new candidate support audit, no-wire competence test, unilateral semantic
  workspace-write assay, pretrained-model run, or partner-transfer test occurred.
  Earlier failures remain unresolved. No J-space certificate follows.
- The analytic eight-channel control is a supervised compiled reader with supplied
  codec, not the trained GRU's native readout and not an autonomous discovery.

## Engineering failures

1. The streaming execution interface raised StreamingExecNotEnabledContainerError
   before executing the training shell. A monitored supervisor captured actual
   child exit statuses. All launched experiments finished in this turn.
2. The first independent audit enumerated an eval_*.log as if it were a directory,
   raising NotADirectoryError. Directory filtering was corrected. The original
   audit source/log are retained. No model, datum or prediction changed.
3. A new resume test initially required serialized checkpoint bytes to be identical
   after interruption. The complete loaded state, optimizer/RNG state and every
   tensor payload were identical; only data.pkl and serialization_id differed.
   At pickle offset26729 the uninterrupted file reuses an existing 'lr' string
   via BINGET, while the resumed file writes the equal string via BINUNICODE;
   weight_decay has the same memoization distinction. The test now asserts the
   correct computation-state/tensor-payload contract and explicitly does not
   certify byte equality for resumed serialization. The original failed test and
   log are retained. The separate full1000-update uninterrupted replay DOES match
   checkpoint bytes and all52 evaluation-bank bytes exactly.
4. An early source-navigation command named two nonexistent files. No execution
   depended on them; the actual inherited modules were then read in full.

## Metadata correction

See METADATA_CORRECTIONS.md. Original parent-bank extrapolation flags had a
max24 default instead of the parent's trained max12. Correct limits are explicit
in the confirmation and consolidated report. Depth controls alter recall, not
the separately tested one-step access followed by working reuse.

## Statistical / design boundaries

Two competence-selected initialization lineages, differing ancestral budgets.
The six new continuations are not six independent randomly initialized models.
The secondary phase is outcome-informed. All worlds/aliases are in the training
support. No universal convergence or unlimited persistence is established.
The new architecture adds106530 copied parameters and a supplied phase dispatch.
The two main arms share total capacity and forward schedule but not backward
compute, number of trainable parameters, or wall time. No equal-capacity unsplit
architecture control was executed.
