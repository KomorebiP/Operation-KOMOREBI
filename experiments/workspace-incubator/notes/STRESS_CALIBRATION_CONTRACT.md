# Outcome-informed access calibration (secondary, after main results)

The original max24/held-out-generator comparison remains unchanged. Its access
repair is incomplete on swap-conjugation48, while joint repair damages B-private
recall. This second experiment asks a different question: can the SAME private
64-state / eight-message / two-exchange architecture learn to retrieve from the
known difficult family when its access training actually includes that family?

Continue each main access-only final checkpoint for1000 additional updates.
Only the copied access parameters train. Original base weights, answer/private
heads, observation, working operations, original message transitions and silent
steps remain frozen. No central decoder or hidden-state targets are introduced.
AdamW restart lr0.0003, batch96, seed340601/340603. Same terminal work (constant
in this arm), memory-consumer and private losses as the main experiment.

At each batch draw one of all six named families uniformly. Lengths12,24,48
are drawn with probabilities0.2,0.2,0.6. This explicitly exposes the previously
held-out swap-conjugation and commuting-flip families and length48. Evaluation
on48 afterward means new histories from a trained family, NOT untrained-family
or untrained-length generalization. Length96 remains unseen. No new geometry
thresholds, projectors or hidden editing procedures are selected. Assess the
same final-bank suite, access communication cuts, multi-consumer working reuse,
repeated retrieval, all-eight recall and private preservation. This is secondary
adaptive development, not a sealed primary, and has extra training vs main arms.
